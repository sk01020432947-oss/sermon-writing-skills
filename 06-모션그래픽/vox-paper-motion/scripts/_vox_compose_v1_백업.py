#!/usr/bin/env python3
"""Vox식 종이 콜라주 모션 합성기.

이미지 레이어(PNG)를 JSON 장면 설명대로 겹치고 움직여 MP4로 만든다.
2.5D 패럴랙스 카메라, 찢어진 종이 가장자리, 그림자, 종이 결, 2프레임 홀드(스톱모션 느낌),
프레임 순환(종이 애니메이션), 글자 등장, 내레이션/음악 합치기.

사용:
  python3 vox_compose.py scene.json            # 렌더
  python3 vox_compose.py --demo <폴더>         # 예제 소재+장면 생성 후 렌더 (자체 점검)
의존: Pillow, numpy, ffmpeg
"""
import json, math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

FONT_CANDIDATES = [
    os.path.expanduser("~/Library/Fonts/NotoSansKR-Black.ttf"),
    os.path.expanduser("~/Library/Fonts/NotoSansKR-Bold.ttf"),
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
]


def font(size, path=None):
    for p in ([path] if path else []) + FONT_CANDIDATES:
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
    return 1 - (1 - t) ** 3


def keyframe(track, t):
    """[{"t":0,"zoom":1,...},...] 선형보간(ease inout)."""
    if not track:
        return {}
    if t <= track[0]["t"]:
        return track[0]
    for a, b in zip(track, track[1:]):
        if a["t"] <= t <= b["t"]:
            k = ease((t - a["t"]) / max(1e-6, b["t"] - a["t"]), "inout")
            return {key: a.get(key, 0) + (b.get(key, a.get(key, 0)) - a.get(key, 0)) * k
                    for key in set(a) | set(b) if key != "t"}
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


# ---------- 종이 효과 ----------
def torn_edge(img, rough=6, seed=0):
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
    paper = Image.new("RGB", img.size, (250, 247, 238))
    out = Image.composite(rgb, paper, Image.fromarray((inner * 255).astype(np.uint8)))
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


# ---------- 레이어 ----------
class Layer:
    def __init__(self, spec, base_dir, W, H, idx):
        self.s = spec
        self.idx = idx
        self.depth = spec.get("depth", 0.5)
        self.start, self.end = spec.get("start", 0), spec.get("end", 1e9)
        self.images = []
        if "text" in spec:
            self.images = [self._text_img(spec)]
        elif "rect" in spec:  # 색 막대 (밑줄·띠). rect=[폭 비율, 높이 px]
            self.images = [Image.new("RGBA", (max(1, int(spec["rect"][0] * W)), int(spec["rect"][1])),
                                     hex2rgb(spec.get("color", "#C2412D")) + (255,))]
        else:
            srcs = spec.get("frames") or [spec["src"]]
            for i, p in enumerate(srcs):
                im = Image.open(os.path.join(base_dir, p)).convert("RGBA")
                if "key" in spec:  # 단색 배경 지우기 (투명 PNG를 못 내는 모델용)
                    im = chroma_key(im, spec["key"], spec.get("tol", 40))
                    bb = im.getchannel("A").getbbox()  # 피사체 크기로 자르기 → x·y·width가 피사체 기준
                    if bb:
                        im = im.crop(bb)
                if spec.get("fit") == "cover":
                    r = max(W * 1.25 / im.width, H * 1.25 / im.height)  # 카메라 여유 25%
                    im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
                elif "width" in spec:
                    r = spec["width"] * W / im.width
                    im = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)
                if spec.get("torn"):
                    im = torn_edge(im, spec.get("rough", 6), seed=idx * 17 + i)
                self.images.append(im)
        self.pad = 0
        if spec.get("shadow", "text" not in spec and "rect" not in spec and spec.get("fit") != "cover"):
            out = [drop_shadow(im) for im in self.images]
            self.images, self.pad = [o[0] for o in out], out[0][1]

    def _text_img(self, s):
        f = font(s.get("size", 96), s.get("font"))
        lines = s["text"].split("\n")
        boxes = [f.getbbox(l) for l in lines]
        lh = int(s.get("size", 96) * 1.25)
        w = max(b[2] for b in boxes) + 40
        h = lh * (len(lines) - 1) + max(b[3] for b in boxes) + 30
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        if s.get("box"):  # 종이 띠 위 글자
            d.rectangle([0, 0, w, h], fill=hex2rgb(s["box"]) + (255,))
        for i, l in enumerate(lines):
            d.text((20, 10 + i * lh), l, font=f, fill=hex2rgb(s.get("color", "#1D1D1D")) + (255,))
        if s.get("box") and s.get("torn", True):
            im = torn_edge(im, 3, seed=self.idx)
        return im

    def frame(self, t, held_t):
        if not (self.start <= t < self.end):
            return None
        s = self.s
        if len(self.images) > 1:
            k = int(held_t * s.get("fps", 6)) % len(self.images)
            im = self.images[k]
        else:
            im = self.images[0]
        local = t - self.start
        # 등장
        enter = s.get("enter")
        dx = dy = 0.0
        sc = 1.0
        rot = s.get("rot", 0.0)
        alpha = 1.0
        if enter:
            e = enter if isinstance(enter, dict) else {"type": enter}
            k = ease(local / e.get("dur", 0.6), "back" if e.get("type", "pop") in ("pop", "slap") else "out")
            typ = e.get("type", "pop")
            if typ == "pop":
                sc *= max(0.01, k)
            elif typ == "fade":
                alpha = min(1, local / e.get("dur", 0.6))
            elif typ in ("left", "right", "top", "bottom"):
                dist = e.get("dist", 0.6)
                v = (1 - k) * dist
                dx = {"left": -v, "right": v}.get(typ, 0)
                dy = {"top": -v, "bottom": v}.get(typ, 0)
            elif typ == "slap":  # 비스듬히 툭 붙기
                sc *= 1 + (1 - k) * 0.4
                rot += (1 - k) * 12
            elif typ == "beat":  # 키네틱 비트: 1.4배에서 제자리로 빠르게 정착
                sc *= 1.4 - 0.4 * ease(local / e.get("dur", 0.2), "out")
            elif typ == "mask":  # 마스크 리빌: 제자리 상자 안에서 아래→위로 올라옴
                off = int((1 - k) * im.height * 1.1)
                if off >= im.height:
                    return None
                clip = Image.new("RGBA", im.size, (0, 0, 0, 0))
                clip.paste(im.crop((0, 0, im.width, im.height - off)), (0, off))
                im = clip
            elif typ == "wipe":  # 왼→오 드로우 (밑줄·띠)
                k = ease(local / e.get("dur", 0.6), "linear" if e.get("linear") else "out")
                cw = int(im.width * k)
                if cw <= 0:
                    return None
                clip = Image.new("RGBA", im.size, (0, 0, 0, 0))
                clip.paste(im.crop((0, 0, cw, im.height)), (0, 0))
                im = clip
        # 퇴장
        if self.end < 1e8 and s.get("exit") == "fade":
            alpha *= min(1, (self.end - t) / 0.4)
        # 반복 움직임
        if "bob" in s:
            b = s["bob"]
            dy += b.get("amp", 0.01) * math.sin(2 * math.pi * held_t / b.get("period", 2))
            rot += b.get("tilt", 0) * math.sin(2 * math.pi * held_t / b.get("period", 2) + 1)
        if "drift" in s:
            dx += s["drift"][0] * local
            dy += s["drift"][1] * local
        return im, dx, dy, sc, rot, alpha


def render(spec_path):
    base = os.path.dirname(os.path.abspath(spec_path))
    S = json.load(open(spec_path, encoding="utf-8"))
    W, H = S.get("size", [1920, 1080])
    fps = S.get("fps", 30)
    hold = S.get("hold", 2)  # 2 = 2프레임씩 같은 그림(종이 스톱모션 느낌), 1 = 매끈
    dur = S["duration"]
    out = os.path.join(base, S.get("out", "out.mp4"))
    bg = hex2rgb(S.get("bg", "#EFE6D2"))
    layers = [Layer(l, base, W, H, i) for i, l in enumerate(S["layers"])]
    grain = paper_grain((W, H), S.get("grain", 0.05)) if S.get("grain", 0.05) else None
    jitter = S.get("jitter", 1.5)  # 홀드마다 위치 미세 떨림(px)

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

    n = int(dur * fps)
    cache = None
    for f in range(n):
        t = f / fps
        if f % hold and cache is not None:
            p.stdin.write(cache)
            continue
        held_t = (f // hold) * hold / fps
        rnd = random.Random(f // hold)
        cam = keyframe(S.get("camera", []), t)
        zoom, cx, cy = cam.get("zoom", 1.0), cam.get("x", 0.0), cam.get("y", 0.0)
        canvas = Image.new("RGBA", (W, H), bg + (255,))
        for L in layers:
            r = L.frame(t, held_t)
            if r is None:
                continue
            im, dx, dy, sc, rot, alpha = r
            d = L.depth
            lz = 1 + (zoom - 1) * d  # 깊을수록(depth↑ = 앞) 카메라에 더 반응
            s_total = sc * lz * L.s.get("scale", 1.0)
            if abs(s_total - 1) > 1e-3:
                im = im.resize((max(1, int(im.width * s_total)), max(1, int(im.height * s_total))), Image.BILINEAR)
            if rot:
                im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
            if alpha < 1:
                a = im.getchannel("A").point(lambda v: int(v * alpha))
                im = im.copy()
                im.putalpha(a)
            ax, ay = L.s.get("x", 0.5), L.s.get("y", 0.5)
            # 화면 중심 기준 확대 + 깊이만큼 패럴랙스 이동
            px = W / 2 + ((ax + dx) * W - W / 2 - cx * d * W) * lz
            py = H / 2 + ((ay + dy) * H - H / 2 - cy * d * H) * lz
            if L.s.get("fit") != "cover" and jitter:
                px += rnd.uniform(-jitter, jitter)
                py += rnd.uniform(-jitter, jitter)
            canvas.alpha_composite(im, (int(px - im.width / 2), int(py - im.height / 2)))
        arr = np.asarray(canvas.convert("RGB"), dtype=np.float32)
        if grain is not None:
            arr *= (1 + grain)[..., None]
        if S.get("vignette", 0.25):
            yy, xx = np.ogrid[:H, :W]
            v = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
            arr *= (1 - S.get("vignette", 0.25) * np.clip(v - 0.3, 0, 1))[..., None]
        cache = arr.clip(0, 255).astype(np.uint8).tobytes()
        p.stdin.write(cache)
    p.stdin.close()
    if p.wait():
        sys.exit("ffmpeg 실패")
    print(out)
    return out


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
        "camera": [{"t": 0, "zoom": 1.0, "x": 0, "y": 0}, {"t": 6, "zoom": 1.18, "x": 0.06, "y": -0.02}],
        "layers": [
            {"src": "sky.png", "fit": "cover", "depth": 0.05},
            {"src": "mount_far.png", "width": 1.25, "x": 0.5, "y": 0.72, "depth": 0.25, "torn": True, "shadow": False},
            {"src": "cable.png", "width": 1.35, "x": 0.5, "y": 0.33, "depth": 0.5, "shadow": False},
            {"src": "car.png", "width": 0.16, "x": 0.42, "y": 0.42, "depth": 0.55, "torn": True,
             "bob": {"amp": 0.012, "period": 2.4, "tilt": 2.5}, "drift": [0.035, -0.003],
             "enter": {"type": "top", "dur": 0.9, "dist": 0.5}},
            {"src": "mount_near.png", "width": 1.3, "x": 0.5, "y": 0.86, "depth": 0.85, "torn": True},
            {"frames": ["flag0.png", "flag1.png", "flag2.png", "flag3.png"], "fps": 6, "width": 0.09,
             "x": 0.82, "y": 0.66, "depth": 0.85},
            {"text": "1905년", "size": 150, "color": "#1D1D1D", "x": 0.2, "y": 0.13, "depth": 0.0,
             "start": 1.2, "enter": "slap", "rot": -3},
            {"text": "그린델발트로 가는 길", "size": 64, "color": "#FFFFFF", "box": "#1D1D1D",
             "x": 0.24, "y": 0.3, "depth": 0.0, "start": 2.0, "enter": {"type": "left", "dur": 0.5, "dist": 0.4}},
        ],
    }
    path = os.path.join(folder, "scene.json")
    json.dump(spec, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    out = render(path)
    # 자체 점검: 길이·해상도 확인
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                            "stream=width,height,nb_frames", "-of", "csv=p=0", out], capture_output=True, text=True).stdout.strip()
    w, h, nf = probe.split(",")
    assert (int(w), int(h)) == (W, H) and abs(int(nf) - 180) <= 1, probe
    print("demo ok:", probe)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--demo":
        demo(sys.argv[2])
    elif len(sys.argv) == 2:
        render(sys.argv[1])
    else:
        print(__doc__)
