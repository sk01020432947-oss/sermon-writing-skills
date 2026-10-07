#!/usr/bin/env python3
"""폴더 안 HWP·HWPX·PDF·DOCX·XLSX(·XLS)를 하위 폴더까지 일괄로 Markdown 변환.

엔진은 kordoc (HanMark 옵시디언 플러그인과 같은 엔진). 폴더 구조를 그대로 복제한다.
이미 변환된 파일(md가 원본보다 새것)은 건너뛴다 — 다시 돌려도 새 파일만 처리.

사용:
  python3 batch_to_md.py <원본폴더> [출력폴더] [--ocr] [--force] [-j 4]
  python3 batch_to_md.py <파일> [출력.md] [--ocr] [--force]   # 파일 하나 → 같은 폴더에 이름.md
  출력폴더 기본값: <원본폴더>_md
"""
import argparse, subprocess, sys, unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

EXTS = {".hwp", ".hwpx", ".pdf", ".docx", ".xlsx", ".xls"}


def targets(src: Path, dst: Path):
    files = sorted(p for p in src.rglob("*")
                   if p.is_file() and p.suffix.lower() in EXTS and not p.name.startswith(("~$", ".")))
    stems = {}
    for p in files:  # 같은 폴더에 승낙서.hwp + 승낙서.docx → 이름 충돌 방지
        key = (p.parent, unicodedata.normalize("NFC", p.stem))
        stems[key] = stems.get(key, 0) + 1
    for p in files:
        rel = p.relative_to(src)
        dup = stems[(p.parent, unicodedata.normalize("NFC", p.stem))] > 1
        name = f"{p.stem}{p.suffix}.md" if dup else f"{p.stem}.md"
        yield p, dst / rel.parent / unicodedata.normalize("NFC", name)


def convert(src_file: Path, out: Path, ocr: bool):
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["npx", "-y", "kordoc", str(src_file), "-o", str(out), "--silent"] + (["--ocr"] if ocr else [])
    r = subprocess.run(cmd, capture_output=True, text=True)
    ok = r.returncode == 0 and out.exists()
    return ok, (r.stderr or r.stdout).strip().splitlines()[-1:] if not ok else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst", nargs="?")
    ap.add_argument("--ocr", action="store_true", help="스캔 PDF OCR")
    ap.add_argument("--force", action="store_true", help="이미 변환된 것도 다시")
    ap.add_argument("-j", type=int, default=4)
    a = ap.parse_args()
    src = Path(a.src).expanduser().resolve()
    if src.is_file():  # 파일 하나: 같은 폴더에 이름.md. 기존 md는 --force 없이 덮어쓰지 않는다
        out = Path(a.dst).expanduser().resolve() if a.dst else src.with_suffix(".md")
        if src.suffix.lower() not in EXTS:
            sys.exit(f"지원하지 않는 형식: {src.name}")
        if out.exists() and not a.force:
            sys.exit(f"이미 있음: {out.name} (--force로 덮어쓰기)")
        ok, err = convert(src, out, a.ocr)
        print(f"완료: {out.name}" if ok else f"실패: {src.name} {' '.join(err)}")
        sys.exit(0 if ok else 1)
    dst = Path(a.dst).expanduser().resolve() if a.dst else src.with_name(src.name + "_md")
    if not src.is_dir():
        sys.exit(f"폴더가 아님: {src}")

    jobs = [(s, o) for s, o in targets(src, dst)
            if a.force or not o.exists() or o.stat().st_mtime < s.stat().st_mtime]
    print(f"대상 {len(jobs)}개 → {dst}")
    fails = []
    with ThreadPoolExecutor(a.j) as ex:
        for (s, o), (ok, err) in zip(jobs, ex.map(lambda j: convert(*j, a.ocr), jobs)):
            print(("OK  " if ok else "FAIL"), s.relative_to(src), *err)
            if not ok:
                fails.append(f"{s.relative_to(src)}\t{' '.join(err)}")
    if fails:
        dst.mkdir(parents=True, exist_ok=True)
        (dst / "_실패목록.txt").write_text("\n".join(fails) + "\n", encoding="utf-8")
    print(f"완료: 성공 {len(jobs) - len(fails)} / 실패 {len(fails)}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
