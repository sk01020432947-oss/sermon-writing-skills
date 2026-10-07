#!/usr/bin/env python3
"""박자 격자 계산기 (원리 B1·B2·A5·C8).

  python3 beatgrid.py --duration 15 --bars 8          # BPM 역산(=128) + 박자표
  python3 beatgrid.py --bpm 128 --duration 15 --scenes 4   # 장면표 뼈대(강박 경계)
  python3 beatgrid.py --bpm 128 --duration 15 --json grid.json
  python3 beatgrid.py --bpm 128 --duration 15 --sheet clip.mp4  # 강박 콘택트 시트
  python3 beatgrid.py --bpm 128 --duration 15 --snap 4.0,9.2    # 컷 시각을 가까운 박·강박에 맞춤
  python3 beatgrid.py --test
"""
import argparse, json, os, subprocess, sys, tempfile

TIERS = ("downbeat", "beat", "eighth", "sixteenth")
ROLE = {
    "downbeat": "장면 전환·주요 등장",
    "beat": "키워드 교체·스케일 펄스",
    "eighth": "글자 단위 등장",
    "sixteenth": "글자 단위 등장(빠른 구간)",
}


def fit_bpm(duration, bars, per_bar=4):
    """길이에 마디 수가 정확히 들어가는 BPM. 15초·8마디 → 128."""
    return bars * per_bar * 60.0 / duration


def grid(bpm, duration, per_bar=4, offset=0.0):
    """16분음표 단위 사건 목록. 각 사건은 가장 높은 계층 하나만 가진다."""
    step = 60.0 / bpm / 4
    out, i = [], 0
    while offset + i * step < duration - 1e-9:
        t = offset + i * step
        if i % (4 * per_bar) == 0:
            tier = "downbeat"
        elif i % 4 == 0:
            tier = "beat"
        elif i % 2 == 0:
            tier = "eighth"
        else:
            tier = "sixteenth"
        out.append({"t": round(t, 4), "bar": i // (4 * per_bar) + 1,
                    "beat": (i // 4) % per_bar + 1, "tier": tier})
        i += 1
    return out


def scenes(events, n):
    """강박을 n개 장면에 고르게 나눈다(장면 경계는 언제나 강박)."""
    downs = [e["t"] for e in events if e["tier"] == "downbeat"]
    n = max(1, min(n, len(downs)))
    starts = [downs[round(k * len(downs) / n)] for k in range(n)]
    return starts


def snap(t, events, tier="beat"):
    """임의 시각(예: 컷 지점)을 가장 가까운 해당 계층 이상의 박으로."""
    rank = TIERS.index(tier)
    cands = [e["t"] for e in events if TIERS.index(e["tier"]) <= rank]
    return min(cands, key=lambda x: abs(x - t))


def sheet(video, times, out, width=480):
    tmp = tempfile.mkdtemp()
    for k, t in enumerate(times):
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t:.3f}", "-i", video,
                        "-frames:v", "1", "-vf", f"scale={width}:-1",
                        os.path.join(tmp, f"f{k:03d}.jpg")], check=True)
    cols = min(4, len(times))
    rows = -(-len(times) // cols)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", os.path.join(tmp, "f%03d.jpg"),
                    "-vf", f"tile={cols}x{rows}", "-frames:v", "1", out], check=True)
    return out


def test():
    assert abs(fit_bpm(15, 8) - 128) < 1e-9
    g = grid(128, 15)
    assert len(g) == 128                        # 32박 × 16분 4개
    assert sum(e["tier"] == "downbeat" for e in g) == 8
    assert sum(e["tier"] in ("downbeat", "beat") for e in g) == 32
    assert scenes(g, 4) == [0.0, 3.75, 7.5, 11.25]
    assert snap(4.0, g, "downbeat") == 3.75
    assert abs(fit_bpm(20, 10) - 120) < 1e-9    # R16: 120BPM 10마디 = 20초
    assert snap(9.2, g, "beat") == 9.375 and len(scenes(g, 20)) == 8
    print("ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--duration", type=float)
    ap.add_argument("--bars", type=int)
    ap.add_argument("--bpm", type=float)
    ap.add_argument("--per-bar", type=int, default=4)
    ap.add_argument("--offset", type=float, default=0.0, help="첫 강박 시각(음악 분석으로 얻은 값)")
    ap.add_argument("--scenes", type=int)
    ap.add_argument("--json")
    ap.add_argument("--sheet", help="렌더된 영상: 강박마다 한 장씩 모은 콘택트 시트")
    ap.add_argument("--snap", help="쉼표로 구분한 컷 시각(초): 가장 가까운 박·강박을 알려 준다")
    ap.add_argument("--test", action="store_true")
    a = ap.parse_args()
    if a.test:
        return test()
    if a.bpm is None:
        if not (a.duration and a.bars):
            ap.error("--bpm 또는 --duration+--bars 가 필요하다")
        a.bpm = fit_bpm(a.duration, a.bars, a.per_bar)
    if a.duration is None:
        a.duration = (a.bars or 8) * a.per_bar * 60 / a.bpm
    g = grid(a.bpm, a.duration, a.per_bar, a.offset)
    beat = 60 / a.bpm
    print(f"BPM {a.bpm:.2f} · 1박 {beat:.4f}s · 1마디 {beat * a.per_bar:.4f}s · "
          f"길이 {a.duration}s · {sum(e['tier'] == 'downbeat' for e in g)}마디")
    bars = (a.duration - a.offset) / (beat * a.per_bar)
    if abs(bars - round(bars)) > 1e-6:
        whole = max(1, round(bars))
        print(f"주의: 길이가 {bars:.2f}마디라 마지막 마디가 잘린다. {whole}마디에 맞추려면 BPM {fit_bpm(a.duration - a.offset, whole, a.per_bar):.2f}")
    print("\n| 마디 | 박 | 시각(s) | 계층 | 배정 |\n|---|---|---|---|---|")
    for e in g:
        if e["tier"] in ("downbeat", "beat"):
            print(f"| {e['bar']} | {e['beat']} | {e['t']:.3f} | {e['tier']} | {ROLE[e['tier']]} |")
    if a.scenes:
        st = scenes(g, a.scenes) + [a.duration]
        if len(st) - 1 < a.scenes:
            print(f"\n주의: 장면 {a.scenes}개를 요청했지만 강박이 {len(st) - 1}개뿐이라 {len(st) - 1}개로 나눴다. 마디를 늘리거나 장면을 줄일 것.")
        print("\n| 장면 | 시작 | 끝 | 화면 | 움직임 |\n|---|---|---|---|---|")
        for k in range(len(st) - 1):
            print(f"| {k + 1} | {st[k]:.3f} | {st[k + 1]:.3f} |  |  |")
    if a.json:
        json.dump({"bpm": a.bpm, "duration": a.duration, "events": g}, open(a.json, "w"), indent=1)
        print(f"\nJSON → {a.json}")
    if a.snap:
        print("\n| 컷 | 가까운 박 | 차이 | 가까운 강박 | 차이 |\n|---|---|---|---|---|")
        for c in (float(v) for v in a.snap.split(",")):
            b, d = snap(c, g, "beat"), snap(c, g, "downbeat")
            print(f"| {c:.3f} | {b:.3f} | {b - c:+.3f} | {d:.3f} | {d - c:+.3f} |")
    if a.sheet:
        if not os.path.isfile(a.sheet):
            sys.exit(f"영상 파일이 없다: {a.sheet}")
        downs = [e["t"] + 0.05 for e in g if e["tier"] == "downbeat"]
        out = os.path.splitext(a.sheet)[0] + "_beats.jpg"
        print(f"\n시트 → {sheet(a.sheet, downs, out)}  (왼→오, 위→아래: " + ", ".join(f"{t:.2f}s" for t in downs) + ")")


if __name__ == "__main__":
    sys.exit(main())
