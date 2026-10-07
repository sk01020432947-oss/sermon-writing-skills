#!/usr/bin/env python3
"""Vox식 종이 콜라주 모션 합성기 v2.

이미지 레이어(PNG)를 JSON 장면 설명대로 겹치고 움직여 MP4로 만든다.
원리 출처: 원카AI 「Vox 스타일 모션 그래픽」(youtu.be/a3HPd9wsROU) 화면 속 제작 지침 + 확장.

장면 전체(최상위) 키
  size fps duration hold bg out audio camera layers           (v1과 같음)
  seed chaos            같은 seed+chaos → 같은 프레임. chaos 0=정렬, 1=겨우 버팀
  palette               {ink, paper, grey, accent} 네 값으로 고정
  newsprint             {count, opacity}  배경 뒤 신문 조각(읽히지 않게, seed로 배치)
  focus                 {depth, strength} 초점 깊이 밖 레이어를 흐림(초점 흐림)
  finish                {grain, vignette, halftone, xerox, chroma}  인쇄물 마감
  pixelate              {block, colors}  픽셀아트 양자화
  camera[].tilt         도(°). 버드뷰 0 → 30 처럼 화면 전체를 원근 기울임(깊이 0 글자는 제외)

레이어 키 (v1 + 추가)
  src | frames(+fps, register) | text(+serif, box) | rect | route
  key tol torn rough shadow bw accent(duotone|backing|recolor) recolor_box blur boil
  x y width scale rot depth start end enter exit bob drift path
  enter.type: pop slap fade left right top bottom mask wipe beat   enter.ease: out expo back linear inout
  path: {points:[[x,y]...], start, dur, ease, arc, rotate, rotate_max}
  route: {points, start, dur, arc, dash:[on,off], width, color}  점선 항로를 그려 나간다

사용:
  python3 vox_compose.py scene.json                 # 렌더
  python3 vox_compose.py scene.json --still 2.5 a.png   # 한 장 (썸네일·검수)
  python3 vox_compose.py scene.json --sheet 8 s.jpg     # 검수용 모아보기
  python3 vox_compose.py --demo <폴더>              # 예제 소재+장면 생성 후 렌더 (자체 점검)
의존: Pillow, numpy, ffmpeg
"""
import json, math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops, ImageEnhance

FONT_CANDIDATES = [
    os.path.expanduser("~/Library/Fonts/NotoSansKR-Black.ttf"),
    os.path.expanduser("~/Library/Fonts/NotoSansKR-Bold.ttf"),
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
]
SERIF_CANDIDATES = [
    os.path.expanduser("~/Library/Fonts/NanumMyeongjoExtraBold.ttf"),
    os.path.expanduser("~/Library/Fonts/NanumMyeongjoBold.ttf"),
    "/System/Library/Fonts/Supplemental/AppleMyungjo.ttf",
]
PALETTE = {"ink": "#1B1A17", "paper": "#EFE6D2", "grey": "#8C877D", "accent": "#C8432B"}


def font(size, path=None, serif=False):
    for p in ([path] if path else []) + (SERIF_CANDIDATES if serif else []) + FONT_CANDIDATES:
        if p and os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def ease(t, kind="out"):
    t = max(0.0, min(1.0, t))
    if kind == "linear":
        return t
    if kind == "inout":
        return 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2
    if kind == "back":  # 살짝 넘쳤다 돌아오는 종이 '툭'
        c = 1.70158
        return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2
    if kind == "expo":  # 지수 감속 + 작은 오버슈트 후 정착 (주인공 등장)
        base = 1 - 2 ** (-10 * t) if t < 1 else 1.0
        return base + 0.06 * math.sin(math.pi * min(1, t * 1.6)) * (1 - t)
    return 1 - (1 - t) ** 3


def keyframe(track, t):
    """[{"t":0,"zoom":1,...},...] 보간(ease inout)."""
    if not track:
        return {}
    if t <= track[0]["t"]:
        return track[0]
    for a, b in zip(track, track[1:]):
        if a["t"] <= t <= b["t"]:
            k = ease((t - a["t"]) / max(1e-6, b["t"] - a["t"]), b.get("ease", "inout"))
            return {key: a.get(key, 0) + (b.get(key, a.get(key, 0)) - a.get(key, 0)) * k
                    for key in set(a) | set(b) if key not in ("t", "ease")}
    return track[-1]


def chroma_key(img, color="#FFFFFF", tol=40):
    """가장자리와 이어진 단색 배경만 투명하게 (피사체 안의 같은 색은 남김)."""
    a = np.asarray(img.convert("RGB"), dtype=np.int16)
    near = (np.abs(a - np.array(hex2rgb(color))).max(axis=2) <= tol).astype(np.uint8) * 255
    m = Image.fromarray(near).copy()  # fromarray 이미지는 floodfill이 안 먹는다
    w, h = m.size
    for xy in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):  # 네 모서리에서 번지기
        if m.getpixel(xy) == 255:
            ImageDraw.floodfill(m, xy, 128)
    bgmask = np.asarray(m) == 128
    out = img.copy()
    alpha = np.asarray(out.getchannel("A")).copy()
    alpha[bgmask] = 0
    out.putalpha(Image.fromarray(alpha).filter(ImageFilter.MinFilter(3)))
    return out


# ---------- 종이·인쇄 효과 ----------
def torn_edge(img, rough=6, seed=0, paper=(250, 247, 238)):
    """알파 가장자리를 들쭉날쭉하게 깎고 흰 종이 테두리를 남긴다."""
    rng = np.random.default_rng(seed)
    a = np.array(img.getchannel("A"), dtype=np.float32) / 255
    h, w = a.shape
    noise = rng.random((h // 8 + 2, w // 8 + 2)).astype(np.float32)
    noise = np.array(Image.fromarray((noise * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), dtype=np.float32) / 255
    blur = np.array(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(rough)), dtype=np.float32) / 255
    inner = (blur - 0.5 + (noise - 0.5) * 0.35) > 0.05
    outer = (blur - 0.5 + (noise - 0.5) * 0.45) > -0.12
    rgb = img.convert("RGB")
    out = Image.composite(rgb, Image.new("RGB", img.size, paper), Image.fromarray((inner * 255).astype(np.uint8)))
    out.putalpha(Image.fromarray((outer * 255).astype(np.uint8)))
    return out


def drop_shadow(img, offset=(10, 14), blur=10, opacity=0.35):
    pad = blur * 3 + max(map(abs, offset))
    W, H = img.size[0] + pad * 2, img.size[1] + pad * 2
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", img.size, (0, 0, 0, int(255 * opacity)))
    sh.putalpha(ImageChops.multiply(img.getchannel("A"), sh.getchannel("A")))
    base.alpha_composite(sh, (pad + offset[0], pad + offset[1]))
    base = base.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(img, (pad, pad))
    return base, pad


def paper_grain(size, strength=0.06, seed=1):
    rng = np.random.default_rng(seed)
    w, h = size
    n = rng.normal(0, 1, (h // 2, w // 2)).astype(np.float32)
    n = np.array(Image.fromarray(((n * 40) + 128).clip(0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
                 .filter(ImageFilter.GaussianBlur(0.8)), dtype=np.float32)
    return (n - 128) / 128 * strength  # 곱해서 쓰는 밝기 변조


def to_bw(img, contrast=1.2):
    """흑백 변환(알파 유지). 원리: 주인공도 흑백으로 만든 뒤 강조를 얹는다."""
    a = img.getchannel("A")
    g = ImageEnhance.Contrast(img.convert("L")).enhance(contrast).convert("RGBA")
    g.putalpha(a)
    return g


def duotone(img, ink, hi):
    """그림자→먹색, 밝은 곳→강조색."""
    L = np.asarray(img.convert("L"), dtype=np.float32)[..., None] / 255
    rgb = np.array(hex2rgb(ink), np.float32) * (1 - L) + np.array(hex2rgb(hi), np.float32) * L
    out = Image.fromarray(rgb.clip(0, 255).astype(np.uint8)).convert("RGBA")
    out.putalpha(img.getchannel("A"))
    return out


def recolor(img, box, color):
    """주인공을 정의하는 한 부분(상자 범위, 이미지 비율)만 강조색으로 곱하기."""
    arr = np.asarray(img, dtype=np.float32).copy()
    h, w = arr.shape[:2]
    x0, y0, x1, y1 = int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)
    c = np.array(hex2rgb(color), np.float32) / 255
    seg = arr[y0:y1, x0:x1, :3]
    L = seg.mean(axis=2, keepdims=True) / 255
    arr[y0:y1, x0:x1, :3] = (255 * c * (0.35 + 0.75 * L)).clip(0, 255)
    return Image.fromarray(arr.astype(np.uint8))


def backing(img, color, rng, pad=0.12, rough=4):
    """주인공 뒤에 평평한 색종이 판(강조색 또는 밝은 피사체용 중간 회색)."""
    w, h = img.size
    pw, ph = int(w * (1 + pad * 2)), int(h * (1 + pad * 2))
    card = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    bw_, bh_ = int(w * (0.78 + rng.random() * 0.2)), int(h * (0.62 + rng.random() * 0.25))
    bx, by = int((pw - bw_) / 2 + (rng.random() - 0.5) * w * 0.15), int((ph - bh_) / 2 + (rng.random() - 0.3) * h * 0.12)
    rect = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    ImageDraw.Draw(rect).rectangle([bx, by, bx + bw_, by + bh_], fill=hex2rgb(color) + (255,))
    rect = torn_edge(rect, rough, seed=int(rng.random() * 1e6), paper=hex2rgb(color))
    card.alpha_composite(rect)
    card.alpha_composite(img, ((pw - w) // 2, (ph - h) // 2))
    return card


def newsprint_sheet(W, H, count, opacity, rng, chaos, pal):
    """읽히지 않는 신문 조각들을 흩뿌린 큰 판(화면의 1.3배). 내용이 아니라 분위기."""
    SW, SH = int(W * 1.3), int(H * 1.3)
    sheet = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    paper = np.array(hex2rgb(pal["paper"]))
    for i in range(count):
        fw, fh = int(W * rng.uniform(0.12, 0.3)), int(H * rng.uniform(0.15, 0.4))
        tone = tuple(int(v) for v in (paper * rng.uniform(0.9, 1.0)).clip(0, 255))
        frag = Image.new("RGBA", (fw, fh), tone + (255,))
        d = ImageDraw.Draw(frag)
        cols = rng.choice([1, 2, 3])
        cw = fw // cols
        lh = max(6, int(H * 0.012))
        if rng.random() < 0.6:  # 머리기사 띠
            d.rectangle([cw * 0.08, lh, fw * rng.uniform(0.5, 0.9), lh * 3.2], fill=(70, 66, 60, 255))
            y0 = lh * 5
        else:
            y0 = lh
        for c in range(cols):
            y = y0
            while y < fh - lh:
                x0 = c * cw + cw * 0.08
                d.rectangle([x0, y, x0 + cw * rng.uniform(0.55, 0.84), y + lh * 0.45], fill=(95, 90, 82, 255))
                y += lh
        frag = torn_edge(frag, 4, seed=int(rng.random() * 1e6), paper=tone)
        a = np.asarray(frag.getchannel("A"), np.float32) * opacity * rng.uniform(0.7, 1.2)
        frag.putalpha(Image.fromarray(a.clip(0, 255).astype(np.uint8)))
        frag = frag.rotate(rng.uniform(-1, 1) * (4 + 10 * chaos), expand=True, resample=Image.BICUBIC)
        sheet.alpha_composite(frag, (int(rng.uniform(0, SW - fw)), int(rng.uniform(0, SH - fh))))
    return sheet


def perspective_coeffs(src, dst):
    """dst(출력) 좌표 → src(입력) 좌표 투영 계수 (PIL PERSPECTIVE)."""
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()


def tilt_image(im, deg, fill):
    """화면을 수평축으로 deg만큼 눕힌다(위쪽이 멀어짐). 위 끝이 화면을 채우도록 확대 보정."""
    if abs(deg) < 0.05:
        return im
    W, H = im.size
    a, d = math.radians(deg), 2.2
    f = 1 / (math.cos(a) * d / (d + math.sin(a)))
    top_s, bot_s = d / (d + math.sin(a)) * f, d / (d - math.sin(a)) * f
    ty, by = H / 2 - math.cos(a) * top_s * H / 2, H / 2 + math.cos(a) * bot_s * H / 2
    dst = [(W / 2 - W / 2 * top_s, ty), (W / 2 + W / 2 * top_s, ty), (W / 2 + W / 2 * bot_s, by), (W / 2 - W / 2 * bot_s, by)]
    src = [(0, 0), (W, 0), (W, H), (0, H)]
    return im.transform((W, H), Image.PERSPECTIVE, perspective_coeffs(src, dst), Image.BICUBIC, fillcolor=fill)


def sample_path(points, arc=0.0, n=60):
    """꺾은선(또는 점프 호)을 촘촘한 점 목록과 누적 길이로."""
    pts = []
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        for i in range(n):
            u = i / n
            pts.append((x0 + (x1 - x0) * u, y0 + (y1 - y0) * u - arc * 4 * u * (1 - u)))
    pts.append(tuple(points[-1]))
    acc = [0.0]
    for (a, b), (c, d) in zip(pts, pts[1:]):
        acc.append(acc[-1] + math.hypot(c - a, d - b))
    return pts, acc


def at_progress(pts, acc, k):
    L = acc[-1] * max(0.0, min(1.0, k))
    for i in range(1, len(acc)):
        if acc[i] >= L:
            u = (L - acc[i - 1]) / max(1e-9, acc[i] - acc[i - 1])
            (a, b), (c, d) = pts[i - 1], pts[i]
            return (a + (c - a) * u, b + (d - b) * u), math.atan2(d - b, c - a), i
    return pts[-1], 0.0, len(pts) - 1


def finish(arr, spec, W, H, fidx, grain, rng_seed):
    """인쇄물 마감: 망점(그림자·중간톤만, 강조색 영역 제외) · 복사기 열화 · 색수차 · 비네트 · 종이 결."""
    fin = spec.get("finish", {})
    vig = fin.get("vignette", spec.get("vignette", 0.25))
    if grain is not None:
        arr *= (1 + grain)[..., None]
    ht = fin.get("halftone", 0)
    if ht:
        p = max(4, int(H / 180))
        yy, xx = np.mgrid[:H, :W]
        dist = np.hypot((xx % p) - p / 2, (yy % p) - p / 2) / (p / 2)
        L = arr.mean(axis=2) / 255
        acc = np.array(hex2rgb(spec.get("palette", {}).get("accent", PALETTE["accent"])), np.float32)
        is_acc = (np.abs(arr - acc).max(axis=2) < 60)
        gate = np.clip((0.72 - L) / 0.3, 0, 1) * (~is_acc)
        dots = (dist < (1 - L) * 1.15).astype(np.float32)
        arr *= (1 - ht * 0.35 * dots * gate)[..., None]
    xr = fin.get("xerox", 0)
    if xr:
        r = np.random.default_rng(rng_seed + fidx)
        speck = (r.random((H // 3, W // 3)) < 0.004 * xr).astype(np.uint8) * 255
        speck = np.asarray(Image.fromarray(speck).resize((W, H), Image.NEAREST), np.float32) / 255
        arr = (arr - 128) * (1 + 0.25 * xr) + 128  # 대비가 뭉개지는 복사 느낌
        arr *= (1 - 0.6 * speck)[..., None]
    ch = fin.get("chroma", 0)
    if ch:
        s = int(ch)
        yy, xx = np.ogrid[:H, :W]
        m = np.clip((((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2 - 0.35), 0, 1)
        r_sh, b_sh = np.roll(arr[..., 0], s, axis=1), np.roll(arr[..., 2], -s, axis=1)
        arr[..., 0] = arr[..., 0] * (1 - m) + r_sh * m
        arr[..., 2] = arr[..., 2] * (1 - m) + b_sh * m
    if vig:
        yy, xx = np.ogrid[:H, :W]
        v = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
        arr *= (1 - vig * np.clip(v - 0.3, 0, 1))[..., None]
    return arr


# ---------- 레이어 ----------
class Layer:
    def __init__(self, spec, base_dir, W, H, idx, S):
        self.s = spec
        self.idx = idx
        self.W, self.H = W, H
        self.kind = "route" if "route" in spec else ("text" if "text" in spec else ("rect" if "rect" in spec else "img"))
        self.depth = spec.get("depth", 0.0 if self.kind == "text" else 0.5)
        self.start, self.end = spec.get("start", 0), spec.get("end", 1e9)
        self.seed, self.chaos = S.get("seed", 0), S.get("chaos", 0.0)
        self.pal = {**PALETTE, **S.get("palette", {})}
        self.rng = random.Random(self.seed * 1000 + idx)
        c = self.chaos if spec.get("chaos", True) and spec.get("fit") != "cover" else 0
        r = self.rng
        self.cj = (c * 0.015 * (r.random() * 2 - 1), c * 0.015 * (r.random() * 2 - 1),
                   c * 6 * (r.random() * 2 - 1), 1 + c * 0.08 * (r.random() * 2 - 1))  # dx dy rot scale
        self.images = []
        if self.kind == "route":
            pts, acc = sample_path(spec["route"]["points"], spec["route"].get("arc", 0))
            self.route = (pts, acc)
            return
        if self.kind == "text":
            self.images = [self._text_img(spec)]
        elif self.kind == "rect":  # 색 막대 (밑줄·띠). rect=[폭 비율, 높이 px]
            col = spec.get("color", self.pal["accent"])
            self.images = [Image.new("RGBA", (max(1, int(spec["rect"][0] * W)), int(spec["rect"][1])),
                                     hex2rgb(self.pal.get(col, col) if not col.startswith("#") else col) + (255,))]
        else:
            srcs = spec.get("frames") or [spec["src"]]
            ims = []
            for p in srcs:
                im = Image.open(os.path.join(base_dir, p)).convert("RGBA")
                if "key" in spec:  # 단색 배경 지우기 (투명 PNG를 못 내는 모델용)
                    im = chroma_key(im, spec["key"], spec.get("tol", 40))
                    bb = im.getchannel("A").getbbox()  # 피사체 크기로 자르기 → x·y·width가 피사체 기준
                    if bb:
                        im = im.crop(bb)
                ims.append(im)
            if len(ims) > 1 and spec.get("register", True):  # 프레임 정렬: 아래-가운데 기준 같은 크기
                mw, mh = max(i.width for i in ims), max(i.height for i in ims)
                reg = []
                for i in ims:
                    c_ = Image.new("RGBA", (mw, mh), (0, 0, 0, 0))
                    c_.alpha_composite(i, ((mw - i.width) // 2, mh - i.height))
                    reg.append(c_)
                ims = reg
            for i, im in enumerate(ims):
                if spec.get("fit") == "cover":
                    r_ = max(W * 1.25 / im.width, H * 1.25 / im.height)  # 카메라 여유 25%
                    im = im.resize((int(im.width * r_), int(im.height * r_)), Image.LANCZOS)
                elif "width" in spec:
                    r_ = spec["width"] * W / im.width
                    im = im.resize((max(1, int(im.width * r_)), max(1, int(im.height * r_))), Image.LANCZOS)
                if spec.get("bw"):
                    im = to_bw(im)
                acc = spec.get("accent")
                if acc == "duotone":
                    im = duotone(im, self.pal["ink"], self.pal["accent"])
                elif acc == "recolor" and "recolor_box" in spec:
                    im = recolor(im, spec["recolor_box"], self.pal["accent"])
                if spec.get("torn"):
                    im = torn_edge(im, spec.get("rough", 6), seed=self.seed * 31 + idx * 17 + i)
                if acc == "backing":
                    im = backing(im, self.pal["accent"], random.Random(self.seed + idx), rough=spec.get("rough", 4))
                elif spec.get("bw") and spec.get("auto_back", True) and acc != "duotone":
                    a = np.asarray(im.getchannel("A")) > 128
                    Lv = np.asarray(im.convert("L"))[a] if a.any() else None
                    if Lv is not None and (Lv.mean() > 140 or (Lv > 200).mean() > 0.35):  # 밝은 피사체는 회색 판으로 떼어 낸다
                        im = backing(im, self.pal["grey"], random.Random(self.seed + idx), rough=spec.get("rough", 4))
                self.images.append(im)
        blur = spec.get("blur", 0)
        foc = S.get("focus")
        if foc and self.depth > 0 and spec.get("fit") != "cover" or (foc and spec.get("fit") == "cover"):
            blur = max(blur, foc.get("strength", 6) * abs(self.depth - foc.get("depth", 0.6)))
        if blur > 0.3:
            self.images = [im.filter(ImageFilter.GaussianBlur(blur)) for im in self.images]
        self.pad = 0
        if spec.get("shadow", self.kind == "img" and spec.get("fit") != "cover"):
            out = [drop_shadow(im) for im in self.images]
            self.images, self.pad = [o[0] for o in out], out[0][1]

    def _text_img(self, s):
        size = s.get("size", 96)
        f = font(size, s.get("font"), serif=s.get("serif", False))
        col = s.get("color", self.pal["ink"])
        col = hex2rgb(self.pal[col] if col in self.pal else col) + (255,)
        lines = s["text"].split("\n")
        lh = int(size * s.get("leading", 1.25))
        boxes = [f.getbbox(l) for l in lines]
        w = max(b[2] for b in boxes) + 40
        h = lh * (len(lines) - 1) + max(b[3] for b in boxes) + 30
        tj = self.chaos * s.get("type_jitter", 1.0) if s.get("chaos", True) else 0
        pad = int(size * 0.2 * (1 if tj else 0))
        im = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
        if s.get("box"):  # 종이 띠 위 글자
            bc = s["box"]
            ImageDraw.Draw(im).rectangle([pad, pad, pad + w, pad + h], fill=hex2rgb(self.pal.get(bc, bc) if not bc.startswith("#") else bc) + (255,))
        d = ImageDraw.Draw(im)
        if not tj:
            for i, l in enumerate(lines):
                d.text((20 + pad, 10 + i * lh + pad), l, font=f, fill=col)
        else:  # 어절마다 기준선·회전을 조금씩 흔든다(읽기 줄은 깨지지 않게)
            r = random.Random(self.seed * 7 + self.idx)
            for i, l in enumerate(lines):
                x = 20 + pad
                for wd in l.split(" "):
                    ww = int(f.getlength(wd))
                    wim = Image.new("RGBA", (ww + 20, int(size * 1.5)), (0, 0, 0, 0))
                    ImageDraw.Draw(wim).text((10, 0), wd, font=f, fill=col)
                    wim = wim.rotate((r.random() * 2 - 1) * 4 * tj, expand=True, resample=Image.BICUBIC)
                    im.alpha_composite(wim, (int(x - 10), int(10 + i * lh + pad + (r.random() * 2 - 1) * 0.08 * size * tj)))
                    x += ww + f.getlength(" ")
        if s.get("box") and s.get("torn", True):
            im = torn_edge(im, 3, seed=self.seed + self.idx)
        return im

    def frame(self, t, held_t):
        if not (self.start <= t < self.end):
            return None
        s = self.s
        if len(self.images) > 1:
            im = self.images[int(held_t * s.get("fps", 6)) % len(self.images)]
        else:
            im = self.images[0]
        local = t - self.start
        dx, dy, rot0, sc = self.cj[0], self.cj[1], self.cj[2], self.cj[3]
        rot = s.get("rot", 0.0) + rot0
        alpha = 1.0
        ax, ay = s.get("x", 0.5), s.get("y", 0.5)
        enter = s.get("enter")
        if enter:
            e = enter if isinstance(enter, dict) else {"type": enter}
            typ = e.get("type", "pop")
            k = ease(local / e.get("dur", 0.6), e.get("ease", "back" if typ in ("pop", "slap") else "out"))
            if typ == "pop":
                sc *= max(0.01, k)
            elif typ == "fade":
                alpha = min(1, local / e.get("dur", 0.6))
            elif typ in ("left", "right", "top", "bottom"):
                v = (1 - k) * e.get("dist", 0.6)
                dx += {"left": -v, "right": v}.get(typ, 0)
                dy += {"top": -v, "bottom": v}.get(typ, 0)
            elif typ == "slap":
                sc *= 1 + (1 - k) * 0.4
                rot += (1 - k) * 12
            elif typ == "beat":
                sc *= 1.4 - 0.4 * ease(local / e.get("dur", 0.2), "out")
            elif typ == "mask":  # 제자리 상자 안에서 아래→위로 올라옴
                off = int((1 - k) * im.height * 1.1)
                if off >= im.height:
                    return None
                clip = Image.new("RGBA", im.size, (0, 0, 0, 0))
                clip.paste(im.crop((0, 0, im.width, im.height - off)), (0, off))
                im = clip
            elif typ == "wipe":  # 왼→오 드로우
                k = ease(local / e.get("dur", 0.6), "linear" if e.get("linear") else e.get("ease", "out"))
                cw = int(im.width * k)
                if cw <= 0:
                    return None
                clip = Image.new("RGBA", im.size, (0, 0, 0, 0))
                clip.paste(im.crop((0, 0, cw, im.height)), (0, 0))
                im = clip
        if self.end < 1e8 and s.get("exit") == "fade":
            alpha *= min(1, (self.end - t) / 0.4)
        if "bob" in s:
            b = s["bob"]
            dy += b.get("amp", 0.01) * math.sin(2 * math.pi * held_t / b.get("period", 2))
            rot += b.get("tilt", 0) * math.sin(2 * math.pi * held_t / b.get("period", 2) + 1)
        if "boil" in s:  # 프레임마다 살짝 들썩·기울기 (종이 애니메이션)
            r = random.Random(self.seed * 13 + self.idx * 101 + int(held_t * 100))
            bp, bd = s["boil"]
            dx += (r.random() * 2 - 1) * bp / self.W
            dy += (r.random() * 2 - 1) * bp / self.H
            rot += (r.random() * 2 - 1) * bd
        if "drift" in s:
            dx += s["drift"][0] * local
            dy += s["drift"][1] * local
        if "path" in s:
            p = s["path"]
            pts, acc = sample_path(p["points"], p.get("arc", 0))
            k = ease((t - p.get("start", self.start)) / p.get("dur", 3), p.get("ease", "inout"))
            (px, py), ang, _ = at_progress(pts, acc, k)
            ax, ay = px, py
            if p.get("rotate"):
                deg = -math.degrees(ang)
                m = p.get("rotate_max", 180)
                rot += max(-m, min(m, deg))
        return im, dx, dy, sc, rot, alpha, ax, ay


def draw_route(canvas, L, t, W, H, cam, pal):
    r = L.s["route"]
    if t < r.get("start", L.start):
        return
    k = ease((t - r.get("start", L.start)) / r.get("dur", 3), r.get("ease", "inout"))
    pts, acc = L.route
    _, _, n = at_progress(pts, acc, k)
    zoom, cx, cy = cam
    lz = 1 + (zoom - 1) * L.depth
    sp = [(W / 2 + (x * W - W / 2 - cx * L.depth * W) * lz, H / 2 + (y * H - H / 2 - cy * L.depth * H) * lz) for x, y in pts[:n + 1]]
    if len(sp) < 2:
        return
    on, off = r.get("dash", [18, 12])
    col = r.get("color", "accent")
    col = hex2rgb(pal[col] if col in pal else col) + (255,)
    wid = int(r.get("width", 6) * H / 1080)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    pos, draw = 0.0, True
    seg_left = on
    for (a, b), (c, e) in zip(sp, sp[1:]):
        L_ = math.hypot(c - a, e - b)
        u = 0.0
        while u < L_:
            step = min(seg_left, L_ - u)
            if draw:
                d.line([(a + (c - a) * u / L_, b + (e - b) * u / L_), (a + (c - a) * (u + step) / L_, b + (e - b) * (u + step) / L_)], fill=col, width=wid)
            u += step
            seg_left -= step
            if seg_left <= 1e-6:
                draw = not draw
                seg_left = on if draw else off
    canvas.alpha_composite(lay)


def build(spec_path):
    base = os.path.dirname(os.path.abspath(spec_path))
    S = json.load(open(spec_path, encoding="utf-8"))
    W, H = S.get("size", [1920, 1080])
    pal = {**PALETTE, **S.get("palette", {})}
    S["palette"] = pal
    bgc = S.get("bg", pal["paper"])
    bgc = pal.get(bgc, bgc) if not str(bgc).startswith("#") else bgc
    layers = [Layer(l, base, W, H, i, S) for i, l in enumerate(S["layers"])]
    np_spec = S.get("newsprint")
    news = None
    if np_spec:
        rng = random.Random(S.get("seed", 0) * 97 + 5)
        news = newsprint_sheet(W, H, np_spec.get("count", 14), np_spec.get("opacity", 0.35), rng, S.get("chaos", 0), pal)
    fin = S.get("finish", {})
    g = fin.get("grain", S.get("grain", 0.05))
    grain = paper_grain((W, H), g, seed=S.get("seed", 0) + 1) if g else None
    return S, base, W, H, hex2rgb(bgc), layers, news, grain


def render_frame(S, W, H, bg, layers, news, grain, f, fps, hold):
    t = f / fps
    held_t = (f // hold) * hold / fps
    rnd = random.Random(S.get("seed", 0) * 7919 + f // hold)
    cam = keyframe(S.get("camera", []), t)
    zoom, cx, cy, tilt = cam.get("zoom", 1.0), cam.get("x", 0.0), cam.get("y", 0.0), cam.get("tilt", 0.0)
    jitter = S.get("jitter", 1.5) * (1 + 2 * S.get("chaos", 0))
    canvas = Image.new("RGBA", (W, H), bg + (255,))

    def put(L):
        if L.kind == "route":
            draw_route(canvas, L, t, W, H, (zoom, cx, cy), S["palette"])
            return
        r = L.frame(t, held_t)
        if r is None:
            return
        im, dx, dy, sc, rot, alpha, ax, ay = r
        d = L.depth
        lz = 1 + (zoom - 1) * d
        s_total = sc * lz * L.s.get("scale", 1.0)
        if abs(s_total - 1) > 1e-3:
            im = im.resize((max(1, int(im.width * s_total)), max(1, int(im.height * s_total))), Image.BILINEAR)
        if abs(rot) > 0.01:
            im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
        if alpha < 1:
            im = im.copy()
            im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
        px = W / 2 + ((ax + dx) * W - W / 2 - cx * d * W) * lz  # 화면 중심 기준 확대 + 깊이만큼 패럴랙스
        py = H / 2 + ((ay + dy) * H - H / 2 - cy * d * H) * lz
        if L.s.get("fit") != "cover" and jitter:
            px += rnd.uniform(-jitter, jitter)
            py += rnd.uniform(-jitter, jitter)
        canvas.alpha_composite(im, (int(px - im.width / 2), int(py - im.height / 2)))

    world = [L for L in layers if not (tilt and L.depth == 0 and L.kind in ("text", "rect"))]
    hud = [L for L in layers if L not in world]
    if news is not None:  # 신문 조각은 가장 뒤 배경(덮는 배경 그림 바로 위)
        covers = [L for L in world if L.s.get("fit") == "cover"]
        for L in covers:
            put(L)
        lz = 1 + (zoom - 1) * 0.08
        nim = news if abs(lz - 1) < 1e-3 else news.resize((int(news.width * lz), int(news.height * lz)), Image.BILINEAR)
        canvas.alpha_composite(nim, (int(W / 2 - nim.width / 2 - cx * 0.08 * W), int(H / 2 - nim.height / 2 - cy * 0.08 * H)))
        world = [L for L in world if L not in covers]
    for L in world:
        put(L)
    if tilt:
        canvas = tilt_image(canvas, tilt, bg + (255,))
        for L in hud:
            put(L)
    arr = np.asarray(canvas.convert("RGB"), dtype=np.float32)
    arr = finish(arr, S, W, H, f // hold, grain, S.get("seed", 0))
    out = arr.clip(0, 255).astype(np.uint8)
    px = S.get("pixelate")
    if px:
        b = px.get("block", 8)
        small = Image.fromarray(out).resize((W // b, H // b), Image.BILINEAR)
        if px.get("colors"):
            small = small.quantize(px["colors"], method=Image.Quantize.MEDIANCUT).convert("RGB")
        out = np.asarray(small.resize((W, H), Image.NEAREST))
    return out


def render(spec_path):
    S, base, W, H, bg, layers, news, grain = build(spec_path)
    fps = S.get("fps", 30)
    hold = S.get("hold", 2)  # 2 = 2프레임씩 같은 그림(종이 스톱모션 느낌), 1 = 매끈
    dur = S["duration"]
    out = os.path.join(base, S.get("out", "out.mp4"))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(fps), "-i", "-"]
    audio = [a for a in S.get("audio", []) if os.path.exists(os.path.join(base, a["src"]))]
    for a in audio:
        cmd += ["-i", os.path.join(base, a["src"])]
    if audio:
        parts = [f"[{i + 1}:a]volume={a.get('volume', 1)},adelay={int(a.get('start', 0) * 1000)}:all=1[a{i}]"
                 for i, a in enumerate(audio)]
        mix = "".join(f"[a{i}]" for i in range(len(audio)))
        cmd += ["-filter_complex", ";".join(parts) + f";{mix}amix=inputs={len(audio)}:normalize=0[aout]",
                "-map", "0:v", "-map", "[aout]", "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-t", str(dur), out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    cache = None
    for f in range(int(dur * fps)):
        if f % hold and cache is not None:
            p.stdin.write(cache)
            continue
        cache = render_frame(S, W, H, bg, layers, news, grain, f, fps, hold).tobytes()
        p.stdin.write(cache)
    p.stdin.close()
    if p.wait():
        sys.exit("ffmpeg 실패")
    print(out)
    return out


def still(spec_path, t, out_png):
    S, base, W, H, bg, layers, news, grain = build(spec_path)
    fps, hold = S.get("fps", 30), S.get("hold", 2)
    Image.fromarray(render_frame(S, W, H, bg, layers, news, grain, int(t * fps), fps, hold)).save(out_png)
    print(out_png)


def sheet(spec_path, n, out_jpg):
    """검수용: 시작·중간·끝을 고르게 n장 모아보기."""
    S, base, W, H, bg, layers, news, grain = build(spec_path)
    fps, hold, dur = S.get("fps", 30), S.get("hold", 2), S["duration"]
    tw = 480
    th = int(H * tw / W)
    cols = 4 if W >= H else 5
    rows = (n + cols - 1) // cols
    sh = Image.new("RGB", (tw * cols, th * rows), "white")
    for i in range(n):
        t = dur * (i + 0.5) / n
        im = Image.fromarray(render_frame(S, W, H, bg, layers, news, grain, int(t * fps), fps, hold)).resize((tw, th))
        ImageDraw.Draw(im).text((6, 4), f"{t:.1f}s", fill=(255, 220, 0), font=font(18))
        sh.paste(im, ((i % cols) * tw, (i // cols) * th))
    sh.save(out_jpg, quality=88)
    print(out_jpg)


# ---------- 예제 / 자체 점검 ----------
def demo(folder):
    os.makedirs(folder, exist_ok=True)
    W, H = 1920, 1080

    def shape(name, size, draw_fn):
        im = Image.new("RGBA", size, (0, 0, 0, 0))
        draw_fn(ImageDraw.Draw(im), size)
        im.save(os.path.join(folder, name))

    shape("sky.png", (W, H), lambda d, s: [d.rectangle([0, 0, *s], fill=(232, 222, 200, 255)),
                                           d.ellipse([1350, 120, 1600, 370], fill=(233, 120, 60, 255))])
    shape("mount_far.png", (2400, 700), lambda d, s: d.polygon(
        [(0, 700), (300, 250), (650, 520), (1000, 120), (1400, 480), (1800, 200), (2400, 600), (2400, 700)], fill=(120, 140, 150, 255)))
    shape("mount_near.png", (2400, 600), lambda d, s: d.polygon(
        [(0, 600), (200, 380), (520, 520), (900, 260), (1300, 560), (1700, 330), (2400, 560), (2400, 600)], fill=(52, 72, 70, 255)))
    shape("cable.png", (2600, 60), lambda d, s: d.line([(0, 50), (2600, 8)], fill=(30, 30, 30, 255), width=5))

    def car(d, s):
        d.line([(160, 0), (160, 60)], fill=(30, 30, 30, 255), width=8)
        d.rounded_rectangle([20, 60, 300, 260], 20, fill=(214, 48, 49, 255))
        for x in (50, 130, 210):
            d.rectangle([x, 90, x + 60, 160], fill=(245, 236, 215, 255))
    shape("car.png", (320, 280), car)
    for i in range(4):  # 프레임 순환용: 깃발 펄럭임 4장
        shape(f"flag{i}.png", (220, 200), lambda d, s, i=i: [
            d.line([(20, 0), (20, 200)], fill=(40, 40, 40, 255), width=8),
            d.polygon([(24, 10), (200, 30 + i * 12), (24, 100)], fill=(242, 193, 78, 255))])

    spec = {
        "size": [W, H], "fps": 30, "duration": 6, "hold": 2, "bg": "#E8DEC8", "out": "demo.mp4",
        "seed": 11, "chaos": 0.3,
        "camera": [{"t": 0, "zoom": 1.0, "x": 0, "y": 0}, {"t": 6, "zoom": 1.18, "x": 0.06, "y": -0.02}],
        "layers": [
            {"src": "sky.png", "fit": "cover", "depth": 0.05},
            {"src": "mount_far.png", "width": 1.25, "x": 0.5, "y": 0.72, "depth": 0.25, "torn": True, "shadow": False},
            {"src": "cable.png", "width": 1.35, "x": 0.5, "y": 0.33, "depth": 0.5, "shadow": False, "chaos": False},
            {"src": "car.png", "width": 0.16, "x": 0.42, "y": 0.42, "depth": 0.55, "torn": True,
             "bob": {"amp": 0.012, "period": 2.4, "tilt": 2.5}, "drift": [0.035, -0.003],
             "enter": {"type": "top", "dur": 0.9, "dist": 0.5, "ease": "expo"}},
            {"src": "mount_near.png", "width": 1.3, "x": 0.5, "y": 0.86, "depth": 0.85, "torn": True},
            {"frames": ["flag0.png", "flag1.png", "flag2.png", "flag3.png"], "fps": 6, "width": 0.09,
             "x": 0.82, "y": 0.66, "depth": 0.85},
            {"text": "1905년", "size": 150, "serif": True, "x": 0.2, "y": 0.13, "depth": 0.0,
             "start": 1.2, "enter": "slap", "rot": -3},
            {"text": "그린델발트로 가는 길", "size": 64, "color": "#FFFFFF", "box": "ink",
             "x": 0.24, "y": 0.3, "depth": 0.0, "start": 2.0, "enter": {"type": "left", "dur": 0.5, "dist": 0.4}},
        ],
    }
    path = os.path.join(folder, "scene.json")
    json.dump(spec, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    out = render(path)
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                            "stream=width,height,nb_frames", "-of", "csv=p=0", out], capture_output=True, text=True).stdout.strip()
    w, h, nf = probe.split(",")
    assert (int(w), int(h)) == (W, H) and abs(int(nf) - 180) <= 1, probe
    # 결정론: 같은 seed+chaos → 같은 프레임, 다른 seed → 다른 프레임
    S1 = build(path)
    a = render_frame(*S1[:1], *S1[2:], 60, 30, 2)
    b = render_frame(*build(path)[:1], *build(path)[2:], 60, 30, 2)
    assert np.array_equal(a, b), "같은 seed인데 프레임이 다름"
    spec["seed"] = 12
    json.dump(spec, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    c = render_frame(*build(path)[:1], *build(path)[2:], 60, 30, 2)
    assert not np.array_equal(a, c), "seed를 바꿨는데 같은 프레임"
    spec["seed"] = 11
    json.dump(spec, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # 경로·점선·기울기 계산 점검
    pts, acc = sample_path([[0, 0], [1, 0]])
    (x, y), ang, _ = at_progress(pts, acc, 0.5)
    assert abs(x - 0.5) < 1e-6 and abs(ang) < 1e-6
    assert tilt_image(Image.new("RGB", (64, 36), "white"), 30, (0, 0, 0)).size == (64, 36)
    print("demo ok:", probe, "· 결정론 ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 2 and a[0] == "--demo":
        demo(a[1])
    elif len(a) == 4 and a[1] == "--still":
        still(a[0], float(a[2]), a[3])
    elif len(a) == 4 and a[1] == "--sheet":
        sheet(a[0], int(a[2]), a[3])
    elif len(a) == 1:
        render(a[0])
    else:
        print(__doc__)
