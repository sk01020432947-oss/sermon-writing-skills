#!/usr/bin/env python3
"""references/*.md 안의 모든 본문 인용·찬송가 등재를 자체 검증.

이 스크립트는 ad-hoc 검증용 — references가 수정될 때마다 1회씩 돌려
풀이 일관되게 유지되는지 확인.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from bible_validator import validate_reference  # noqa
from hymn_validator import is_valid_pair, VERIFIED_HYMNS  # noqa

REF_DIR = HERE.parent / "references"

# 본문 패턴: "벧전 1:3-5", "롬 8:18", "사 53장", "시 119편"
BIBLE_PATTERN = re.compile(
    r"(?<![A-Za-z가-힣])"
    r"([가-힣]{1,4}(?:상|하|전|후|일|이|삼)?(?:서|기|편)?)\s*"
    r"(\d+)(?::(\d+)(?:[-–~](\d+))?|\s*[장편])"
)

# 찬송가 패턴: "384장 「나의 갈 길 다 가도록」"
HYMN_PATTERN = re.compile(r"(\d+)장\s*「([^」]+)」")


def check_file(path: Path) -> tuple[list[str], list[str], int, int]:
    issues_bible: list[str] = []
    issues_hymn: list[str] = []
    text = path.read_text(encoding="utf-8")
    # 본문 검증 — 좌측 문맥과 함께 추출
    bible_count = 0
    seen_refs = set()
    for line_no, line in enumerate(text.splitlines(), 1):
        for m in BIBLE_PATTERN.finditer(line):
            ref_str = m.group(0)
            if ref_str in seen_refs:
                continue
            seen_refs.add(ref_str)
            # 한국어가 아닌 경우 또는 단순 숫자 표기는 건너뜀
            ok, msg = validate_reference(ref_str)
            bible_count += 1
            if not ok:
                # 일부 패턴은 본문 아닌 경우 발생 가능 — 책 약어 검증
                from bible_validator import normalize_book
                if normalize_book(m.group(1)):
                    issues_bible.append(f"{path.name}:{line_no} '{ref_str}' — {msg}")
    # 찬송가 검증
    hymn_count = 0
    for m in HYMN_PATTERN.finditer(text):
        num = int(m.group(1))
        title = m.group(2).strip()
        ok, msg = is_valid_pair(num, title)
        hymn_count += 1
        if not ok:
            issues_hymn.append(f"{path.name}: {num}장 「{title}」 — {msg}")
    return issues_bible, issues_hymn, bible_count, hymn_count


def main() -> int:
    md_files = sorted(REF_DIR.glob("*.md"))
    total_bible = 0
    total_hymn = 0
    all_bible_issues: list[str] = []
    all_hymn_issues: list[str] = []
    for md in md_files:
        b_iss, h_iss, b_cnt, h_cnt = check_file(md)
        total_bible += b_cnt
        total_hymn += h_cnt
        all_bible_issues.extend(b_iss)
        all_hymn_issues.extend(h_iss)
    print(f"=== references 자체 검증 ===")
    print(f"검사 파일: {[p.name for p in md_files]}")
    print(f"본문 인용 검사: {total_bible}건, 이슈: {len(all_bible_issues)}건")
    print(f"찬송가 인용 검사: {total_hymn}건, 이슈: {len(all_hymn_issues)}건")
    if all_bible_issues:
        print("\n--- 본문 이슈 ---")
        for s in all_bible_issues:
            print(f"  {s}")
    if all_hymn_issues:
        print("\n--- 찬송가 이슈 ---")
        for s in all_hymn_issues:
            print(f"  {s}")
    return 0 if not (all_bible_issues or all_hymn_issues) else 3


if __name__ == "__main__":
    sys.exit(main())
