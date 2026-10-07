#!/usr/bin/env python3
"""V8 LLM 응답(samples/v8_*.md) 자체 검증.

각 LLM 응답 파일의 모든 본문·찬송가를 추출하여 도구로 일괄 검증.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / ".." / "tools"))

from bible_validator import validate_reference, normalize_book  # noqa
from hymn_validator import is_valid_pair  # noqa

# 본문 패턴
BIBLE_PATTERN = re.compile(
    r"(?<![A-Za-z가-힣])"
    r"([가-힣]{1,4}(?:상|하|전|후|일|이|삼)?(?:서|기|편)?)\s*"
    r"(\d+)(?::(\d+)(?:[-–~](\d+))?|\s*[장편])"
)
HYMN_PATTERN = re.compile(r"(\d+)장\s*[「『]?([^」』\n]+?)[」』]")


def check_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    bible_issues: list[str] = []
    hymn_issues: list[str] = []
    bible_seen: set[str] = set()
    hymn_seen: set[tuple[int, str]] = set()
    bible_count = 0
    hymn_count = 0
    for m in BIBLE_PATTERN.finditer(text):
        ref = m.group(0)
        if ref in bible_seen:
            continue
        bible_seen.add(ref)
        if not normalize_book(m.group(1)):
            continue
        bible_count += 1
        ok, msg = validate_reference(ref)
        if not ok:
            bible_issues.append(f"'{ref}': {msg}")
    for m in HYMN_PATTERN.finditer(text):
        try:
            num = int(m.group(1))
        except ValueError:
            continue
        title = m.group(2).strip().strip("\"'")
        key = (num, title)
        if key in hymn_seen:
            continue
        hymn_seen.add(key)
        hymn_count += 1
        ok, msg = is_valid_pair(num, title)
        if not ok:
            hymn_issues.append(f"{num}장 「{title}」: {msg}")
    return {
        "file": path.name,
        "bible_count": bible_count,
        "bible_issues": bible_issues,
        "hymn_count": hymn_count,
        "hymn_issues": hymn_issues,
    }


def main():
    md_files = sorted(HERE.glob("v8_*.md"))
    total = {"bible": 0, "bible_iss": 0, "hymn": 0, "hymn_iss": 0}
    print("=" * 60)
    print("V8 LLM 응답 자체 검증")
    print("=" * 60)
    for md in md_files:
        r = check_file(md)
        total["bible"] += r["bible_count"]
        total["hymn"] += r["hymn_count"]
        total["bible_iss"] += len(r["bible_issues"])
        total["hymn_iss"] += len(r["hymn_issues"])
        print(f"\n{r['file']}")
        print(f"  본문 {r['bible_count']}건, 이슈 {len(r['bible_issues'])}건")
        for s in r["bible_issues"]:
            print(f"    ⚠ {s}")
        print(f"  찬송가 {r['hymn_count']}종, 이슈 {len(r['hymn_issues'])}건")
        for s in r["hymn_issues"]:
            print(f"    ⚠ {s}")
    print("\n" + "=" * 60)
    print(f"총계: 본문 {total['bible']}건 / 이슈 {total['bible_iss']}건")
    print(f"      찬송가 {total['hymn']}종 / 이슈 {total['hymn_iss']}종")
    print("=" * 60)
    return 0 if (total["bible_iss"] == 0 and total["hymn_iss"] == 0) else 3


if __name__ == "__main__":
    sys.exit(main())
