#!/usr/bin/env python3
"""Vox 영상 한 편을 프로젝트 파일 하나로: 내레이션 → 장면 → 전환 → 소리 → 자막 → 가로·세로판 → 썸네일 → 검수 시트.

사용:
  python3 vox_sequence.py project.json            # 전체
  python3 vox_sequence.py project.json --voice    # 내레이션만 만들고 검증 (그림 확정 전에 길이 확인용)
  python3 vox_sequence.py project.json --only 3   # 3번 장면만 다시 렌더 후 다시 잇기

프로젝트 파일 (예: templates/project.json)
  title, out(파일 이름 앞부분), fps, formats {"16:9":[1920,1080], "9:16":[1080,1920]}
  style    모든 장면에 깔리는 공통 값 {seed, chaos, palette, newsprint, finish, focus, hold, bg, pixelate}
  voice    {engine:"omnivoice"|"none", instruct, language, speed, seed, verify:true}
  captions {"9:16":true, "16:9":false, size, y}
  transition {type: wipe|whip|leak|fade|cut, dur}
  music    {src, volume, offset}   offset = 곡의 몇 초 지점을 영상 0초에 둘지 (큐 맞추기)
  scenes[] {say(읽을 문장), caption(화면 자막, 기본=say), lead, tail, duration(내레이션 없을 때),
            transition, camera, layers, layers_v(세로판 전용, 없으면 layers), bg}
           레이어/카메라의 "at": 내레이션 시작 기준 초 → start로 바뀜. 카메라 "t":"end" → 장면 끝
  thumbnail {size, bg, layers}  한 장 렌더

산출물: <out>_16x9.mp4, <out>_9x16.mp4, <out>.srt, <out>_썸네일.png, 검수/*.jpg, 보고서.md
"""
import hashlib, json, math, os, re, shutil, subprocess, sys, difflib, glob
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COMPOSE = os.path.join(HERE, "vox_compose.py")
OMNI = "http://127.0.0.1:3900"


def sh(cmd, **k):
    return subprocess.run(cmd, check=True, **k)


def wav_dur(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                         capture_output=True, text=True).stdout.strip()
    return float(out)


def find_whisper_model():
    known = os.path.expanduser("~/Desktop/cysjavis/KBG-Bible-Labs-Sermon/data/models/ggml-large-v3-turbo-q8_0.bin")
    if os.environ.get("WHISPER_GGML"):
        return os.environ["WHISPER_GGML"]
    if os.path.exists(known):
        return known
    pats = [os.path.expanduser("~/Desktop/cysjavis/**/ggml-large-v3-turbo*.bin"), os.path.expanduser("~/**/ggml-*.bin")]
    for p in pats[:1]:
        m = glob.glob(p, recursive=True)
        if m:
            return m[0]
    return os.environ.get("WHISPER_GGML")


def norm(s):
    return re.sub(r"[\s,.?!·“”\"'…:;()\-]", "", s)


def asr(path, model):
    tmp = path + ".16k.wav"
    sh(["ffmpeg", "-loglevel", "error", "-y", "-i", path, "-ar", "16000", "-ac", "1", tmp])
    r = subprocess.run(["whisper-cli", "-m", model, "-l", "ko", "-nt", "-np", "-f", tmp], capture_output=True, text=True)
    os.remove(tmp)
    return r.stdout.strip()


def tts(text, out, v):
    """OmniVoice(VoiceStudio) 로컬 TTS. 목소리는 지시문으로 정하고 seed로 고정."""
    cmd = ["curl", "-s", "-m", "600", "-X", "POST", f"{OMNI}/generate", "-F", f"text={text}",
           "-F", f"language={v.get('language', 'Korean')}", "-F", f"instruct={v.get('instruct', 'male, middle-aged, low pitch')}",
           "-F", f"seed={v.get('seed', 42)}", "-F", f"speed={v.get('speed', 0.95)}", "-o", out, "-w", "%{http_code}"]
    code = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
    if code != "200":
        raise RuntimeError(f"TTS 실패 HTTP {code} — VoiceStudio 앱이 켜져 있는지 확인 (127.0.0.1:3900/health)")


def make_voice(P, work, report):
    v = P.get("voice", {"engine": "none"})
    os.makedirs(os.path.join(work, "voice"), exist_ok=True)
    model = find_whisper_model() if v.get("verify", True) else None
    durs = []
    for i, sc in enumerate(P["scenes"]):
        say = sc.get("say")
        if not say:
            durs.append(0.0)
            continue
        if sc.get("audio"):  # 직접 녹음 파일
            durs.append(wav_dur(sc["audio"]))
            continue
        if v.get("engine", "omnivoice") == "none":
            raise SystemExit(f"{i + 1}번 장면: 내레이션 엔진이 none인데 audio 파일이 없음")
        v = {**P.get("voice", {}), **sc.get("voice", {})}  # 장면별 목소리 덮어쓰기(seed 등)
        must = sc.get("must_hear", [])  # 받아쓰기에 반드시 들려야 할 단어
        key = hashlib.md5(json.dumps([say, v, must], ensure_ascii=False).encode()).hexdigest()[:10]
        out = os.path.join(work, "voice", f"n{i + 1:02d}_{key}.wav")
        meta = out + ".json"
        if os.path.exists(out) and os.path.exists(meta):
            m = json.load(open(meta, encoding="utf-8"))
            report.append(f"| {i + 1} | {say} | {m['heard'] or '(검증 안 함)'} | {m['score']:.2f} | seed {m['seed']} (캐시) |")
        if not os.path.exists(out):
            best, seeds = None, [v.get("seed", 42), v.get("seed", 42) + 3, v.get("seed", 42) + 7]
            for s in seeds:
                tmp = out + f".s{s}.wav"
                tts(say, tmp, {**v, "seed": s})
                score = 1.0
                heard = ""
                if model:
                    heard = asr(tmp, model)
                    score = max(difflib.SequenceMatcher(None, norm(x), norm(heard)).ratio()
                                for x in (say, sc.get("caption", say)))  # 숫자 표기(오십/50) 차이 허용
                    if any(norm(w) not in norm(heard) for w in must):
                        score = min(score, 0.5)  # 꼭 들려야 할 단어가 안 들림
                if best is None or score > best[0]:
                    best = (score, tmp, heard, s)
                if score >= v.get("pass", 0.9):
                    break
            shutil.move(best[1], out)
            for f in glob.glob(out + ".s*.wav"):
                os.remove(f)
            report.append(f"| {i + 1} | {say} | {best[2] or '(검증 안 함)'} | {best[0]:.2f} | seed {best[3]} |")
            json.dump({"heard": best[2], "score": best[0], "seed": best[3]}, open(meta, "w", encoding="utf-8"), ensure_ascii=False)
        sc["_audio"] = sc.get("audio") or out
        durs.append(wav_dur(sc["_audio"]))
    return durs


# ---------- 자막 ----------
def wrap(t, n):
    lines, cur = [], ""
    for w in t.split():
        if cur and len(cur) + 1 + len(w) > n:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    return lines + [cur] if cur else lines


def chunks(sentence, n):
    segs = [s.strip() for s in re.split(r"(?<=[,.?!])\s+", sentence) if s.strip()]
    out, cur = [], ""
    for s in segs:
        cand = (cur + " " + s).strip()
        if cur and (len(wrap(cand, n)) > 2 or cur[-1] in ".?!"):
            out.append(cur)
            cur = s
        else:
            cur = cand
    return out + [cur] if cur else out


def caption_layers(text, start, d, cfg, W, H):
    n = cfg.get("chars", 15 if W < H else 24)
    cs = chunks(text, n)
    total = sum(len(c) for c in cs) or 1
    t, layers = start, []
    for i, c in enumerate(cs):
        span = d * len(c) / total
        layers.append({"text": "\n".join(wrap(c, n)), "size": cfg.get("size", 58 if W < H else 46), "color": "#FFFFFF",
                       "box": "ink", "x": cfg.get("x", 0.47 if W < H else 0.5), "y": cfg.get("y", 0.72 if W < H else 0.88),
                       "depth": 0.0, "start": round(t, 2), "end": round(t + span + (0.5 if i == len(cs) - 1 else 0), 2),
                       "torn": False, "chaos": False})
        t += span
    return layers


def srt_time(s):
    return "%02d:%02d:%02d,%03d" % (s // 3600, s % 3600 // 60, s % 60, round((s % 1) * 1000))


# ---------- 전환 (파이썬 블렌딩) ----------
def frames_of(path, W, H):
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         stdout=subprocess.PIPE)
    n = W * H * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)
    p.wait()


def hblur(a, r):
    if r < 1:
        return a
    k = int(r)
    c = np.cumsum(np.pad(a.astype(np.float32), ((0, 0), (k + 1, k), (0, 0)), mode="edge"), axis=1)
    return (c[:, 2 * k + 1:] - c[:, :-2 * k - 1]) / (2 * k + 1)


def blend(A, B, k, typ, W, H, rng):
    A, B = A.astype(np.float32), B.astype(np.float32)
    if typ == "fade":
        return A * (1 - k) + B * k
    if typ == "wipe":  # 찢어진 종이 가장자리로 왼→오 공개
        edge = k * (W + 80) - 40
        jag = (np.sin(np.arange(H) * 0.21) * 9 + np.sin(np.arange(H) * 0.047 + 2) * 14)[:, None]
        m = (np.arange(W)[None, :] < edge + jag).astype(np.float32)[..., None]
        rim = ((np.arange(W)[None, :] > edge + jag - 8) & (np.arange(W)[None, :] < edge + jag)).astype(np.float32)[..., None]
        out = A * (1 - m) + B * m
        return out * (1 - rim) + 245 * rim
    if typ == "whip":  # 빠른 휩 팬: 방향 블러(속도) — 초점 흐림과 섞지 않는다
        sp = math.sin(math.pi * k)
        shift = int(W * (k if k < 0.5 else k - 1))
        src = A if k < 0.5 else B
        moved = np.roll(src, -shift, axis=1)
        return hblur(moved, 6 + 70 * sp)
    if typ == "leak":  # 빛샘: 컷 위에서만, 컷을 다 덮게
        base = A * (1 - k) + B * k
        g = np.linspace(0, 1, W)[None, :, None] * np.linspace(0.6, 1, H)[:, None, None]
        warm = np.array([255, 190, 120], np.float32)
        a = math.sin(math.pi * k) ** 0.8
        return base + (warm - base) * (a * (0.18 + 0.4 * g))
    return B if k >= 0.5 else A


def join(parts, out, W, H, fps):
    """parts: [(mp4, 길이초, 다음과의 전환 종류, 전환초)]"""
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(fps), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out],
                         stdin=subprocess.PIPE)
    rng = np.random.default_rng(0)
    carry = []
    for i, (mp4, L, typ, xd) in enumerate(parts):
        fr = list(frames_of(mp4, W, H))
        if carry:  # 앞 장면 꼬리와 이 장면 머리 겹치기
            n = len(carry)
            for j in range(n):
                k = (j + 0.5) / n
                p.stdin.write(blend(carry[j], fr[j], k, prev_typ, W, H, rng).clip(0, 255).astype(np.uint8).tobytes())
            fr = fr[n:]
        nx = int(round(xd * fps)) if i < len(parts) - 1 and typ != "cut" else 0
        body, carry = (fr[:-nx], fr[-nx:]) if nx else (fr, [])
        for f in body:
            p.stdin.write(f.tobytes())
        prev_typ = typ
    p.stdin.close()
    p.wait()


def scene_spec(P, sc, i, fmt, W, H, lead, total, n_dur, work):
    style = P.get("style", {})
    layers = json.loads(json.dumps(sc.get("layers_v") if (H > W and sc.get("layers_v")) else sc.get("layers", [])))
    for L in layers:
        if "at" in L:
            L["start"] = round(lead + L.pop("at"), 3)
        for k in ("path", "route"):
            if k in L and "at" in L[k]:
                L[k]["start"] = round(lead + L[k].pop("at"), 3)
    cam = json.loads(json.dumps(sc.get("camera", [{"t": 0, "zoom": 1.0}, {"t": "end", "zoom": 1.06}])))
    for c in cam:
        if c["t"] == "end":
            c["t"] = total
    cap = P.get("captions", {})
    if cap.get(fmt) and sc.get("say"):
        layers += caption_layers(sc.get("caption", sc["say"]), lead, n_dur, cap, W, H)
    spec = {**style, **sc.get("style", {}), "size": [W, H], "fps": P.get("fps", 30), "duration": round(total, 3),
            "camera": cam, "layers": layers, "out": f"s{i + 1:02d}.mp4"}
    if "bg" in sc:
        spec["bg"] = sc["bg"]
    return spec


def rel_assets(spec, proj_dir, scene_dir):
    """레이어의 src/frames 경로를 장면 폴더 기준으로 바꾼다."""
    def fix(p):
        ap = p if os.path.isabs(p) else os.path.join(proj_dir, p)
        return os.path.relpath(ap, scene_dir)
    for L in spec["layers"]:
        if "src" in L:
            L["src"] = fix(L["src"])
        if "frames" in L:
            L["frames"] = [fix(x) for x in L["frames"]]
    return spec


def main():
    args = sys.argv[1:]
    pj = os.path.abspath(args[0])
    proj_dir = os.path.dirname(pj)
    P = json.load(open(pj, encoding="utf-8"))
    out_base = os.path.join(proj_dir, P.get("out", "vox"))
    work = os.path.join(proj_dir, "_작업")
    os.makedirs(work, exist_ok=True)
    report = ["| # | 대본 | 받아쓰기 | 일치 | 비고 |", "|---|---|---|---|---|"]
    durs = make_voice(P, work, report)
    tr = P.get("transition", {"type": "wipe", "dur": 0.9})
    plan, t = [], 0.0
    for i, sc in enumerate(P["scenes"]):
        lead = sc.get("lead", 0.6 if i else 0.4)
        total = sc.get("duration") or (lead + durs[i] + sc.get("tail", 0.8))
        typ = sc.get("transition", tr.get("type", "wipe"))
        xd = 0 if typ == "cut" else sc.get("transition_dur", tr.get("dur", 0.9))
        plan.append({"lead": lead, "total": total, "typ": typ, "xd": xd, "t0": t})
        t += total - (xd if i < len(P["scenes"]) - 1 else 0)
    length = t
    if "--voice" in args:
        print("\n".join(report))
        print(f"예상 길이 {length:.1f}s")
        return
    only = int(args[args.index("--only") + 1]) - 1 if "--only" in args else None
    fps = P.get("fps", 30)
    outs = []
    for fmt, (W, H) in P.get("formats", {"16:9": [1920, 1080]}).items():
        sd = os.path.join(work, fmt.replace(":", "x"))
        os.makedirs(sd, exist_ok=True)
        parts = []
        for i, sc in enumerate(P["scenes"]):
            pl = plan[i]
            spec = rel_assets(scene_spec(P, sc, i, fmt, W, H, pl["lead"], pl["total"], durs[i], work), proj_dir, sd)
            jp = os.path.join(sd, f"s{i + 1:02d}.json")
            json.dump(spec, open(jp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            mp4 = os.path.join(sd, f"s{i + 1:02d}.mp4")
            if only is None or only == i or not os.path.exists(mp4):
                sh(["python3", COMPOSE, jp])
            parts.append((mp4, pl["total"], pl["typ"], pl["xd"]))
        silent = os.path.join(sd, "_무음.mp4")
        join(parts, silent, W, H, fps)
        final = f"{out_base}_{fmt.replace(':', 'x')}.mp4"
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", silent]
        f, n = [], 0
        for i, sc in enumerate(P["scenes"]):
            if sc.get("_audio"):
                cmd += ["-i", sc["_audio"]]
                n += 1
                f.append(f"[{n}:a]adelay={int((plan[i]['t0'] + plan[i]['lead']) * 1000)}:all=1,apad[a{n}]")
        m = P.get("music")
        if m and os.path.exists(os.path.join(proj_dir, m["src"])):
            cmd += ["-ss", str(m.get("offset", 0)), "-i", os.path.join(proj_dir, m["src"])]
            n += 1
            f.append(f"[{n}:a]volume={m.get('volume', 0.25)},apad[a{n}]")
        if n:
            f.append("".join(f"[a{k}]" for k in range(1, n + 1)) + f"amix=inputs={n}:normalize=0:duration=longest,"
                     f"afade=t=out:st={length - 0.8:.2f}:d=0.8[aout]")
            cmd += ["-filter_complex", ";".join(f), "-map", "0:v", "-map", "[aout]", "-c:a", "aac", "-b:a", "192k"]
        cmd += ["-c:v", "copy", "-t", f"{length:.2f}", final]
        sh(cmd)
        outs.append(final)
        # 검수 시트: 장면마다 시작·가운데·끝
        os.makedirs(os.path.join(proj_dir, "검수"), exist_ok=True)
        from PIL import Image, ImageDraw
        tw = 400 if W >= H else 220
        th = int(H * tw / W)
        cols = 3
        sheet = Image.new("RGB", (tw * cols, th * len(plan)), "white")
        for i, pl in enumerate(plan):
            for j, u in enumerate((0.15, 0.55, 0.95)):
                ts = pl["t0"] + pl["total"] * u
                tmp = os.path.join(sd, "_f.jpg")
                sh(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{ts:.2f}", "-i", final, "-frames:v", "1", tmp])
                im = Image.open(tmp).resize((tw, th))
                ImageDraw.Draw(im).text((5, 4), f"#{i + 1} {ts:.1f}s", fill=(255, 220, 0))
                sheet.paste(im, (j * tw, i * th))
        sheet.save(os.path.join(proj_dir, "검수", f"시트_{fmt.replace(':', 'x')}.jpg"), quality=85)
    # 자막 파일 (가로판 기준 시각)
    with open(out_base + ".srt", "w", encoding="utf-8") as fo:
        k = 0
        for i, sc in enumerate(P["scenes"]):
            if not sc.get("say"):
                continue
            k += 1
            s0 = plan[i]["t0"] + plan[i]["lead"]
            fo.write(f"{k}\n{srt_time(s0)} --> {srt_time(s0 + durs[i])}\n{sc.get('caption', sc['say'])}\n\n")
    # 썸네일
    th_ = P.get("thumbnail")
    if th_:
        W, H = th_.get("size", [1280, 720])
        spec = {**P.get("style", {}), "size": [W, H], "fps": 30, "duration": 1, "camera": [], "layers": th_["layers"]}
        if "bg" in th_:
            spec["bg"] = th_["bg"]
        spec = rel_assets(spec, proj_dir, work)
        jp = os.path.join(work, "thumbnail.json")
        json.dump(spec, open(jp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        sh(["python3", COMPOSE, jp, "--still", str(th_.get("t", 0.99)), out_base + "_썸네일.png"])
    with open(os.path.join(proj_dir, "보고서.md"), "w", encoding="utf-8") as fo:
        fo.write(f"# {P.get('title', '')} 렌더 보고서\n\n길이 {length:.1f}초 · 장면 {len(plan)}개\n\n")
        fo.write("## 내레이션 검증 (받아쓰기 대조, 0.9 이상 통과)\n\n" + "\n".join(report) + "\n\n## 산출물\n\n")
        for o in outs + [out_base + ".srt"]:
            fo.write(f"- {os.path.basename(o)}\n")
    print("\n".join(outs), f"{length:.1f}s")


if __name__ == "__main__":
    main()
