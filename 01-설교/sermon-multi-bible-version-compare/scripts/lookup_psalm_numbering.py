#!/usr/bin/env python3
"""
lookup_psalm_numbering.py — MT/LXX/Vulgata 시편 번호 결정론적 매핑

본 도구는 시편 한 절을 입력받아 MT(마소라)/LXX(70인역)/Vulgata 번호를
모두 반환한다. 할루시네이션을 차단하기 위한 결정론적 lookup.

Usage:
  python3 lookup_psalm_numbering.py <기준> <장:절>
  python3 lookup_psalm_numbering.py MT 23:1
  python3 lookup_psalm_numbering.py LXX 22:1

기준: MT, LXX, VG (= LXX와 동일)
"""

from __future__ import annotations
import sys
from typing import Tuple


def mt_to_lxx(mt_psalm: int, mt_verse: int) -> Tuple[int, int]:
    """MT 시편 번호 → LXX 시편 번호. 절 번호 변경도 처리."""
    if not (1 <= mt_psalm <= 150):
        raise ValueError(f"MT 시편 범위 1-150 초과: {mt_psalm}")

    # MT 1-8 = LXX 1-8 (동일)
    if 1 <= mt_psalm <= 8:
        return (mt_psalm, mt_verse)

    # MT 9 = LXX 9 (앞부분)
    if mt_psalm == 9:
        return (9, mt_verse)

    # MT 10 = LXX 9 (뒷부분). LXX 9에 MT 9·10이 합쳐짐.
    # MT 9는 21절, LXX 9 앞부분은 동일하므로 MT 10:n = LXX 9:(21+n)
    if mt_psalm == 10:
        return (9, 21 + mt_verse)

    # MT 11-113 = LXX 10-112 (1 차이)
    if 11 <= mt_psalm <= 113:
        return (mt_psalm - 1, mt_verse)

    # MT 114 = LXX 113 (앞부분, 8절까지)
    if mt_psalm == 114:
        return (113, mt_verse)

    # MT 115 = LXX 113 (뒷부분). MT 114는 8절, MT 115:n = LXX 113:(8+n)
    if mt_psalm == 115:
        return (113, 8 + mt_verse)

    # MT 116:1-9 = LXX 114
    # MT 116:10-19 = LXX 115:1-10
    if mt_psalm == 116:
        if mt_verse <= 9:
            return (114, mt_verse)
        else:
            return (115, mt_verse - 9)

    # MT 117-146 = LXX 116-145 (1 차이)
    if 117 <= mt_psalm <= 146:
        return (mt_psalm - 1, mt_verse)

    # MT 147:1-11 = LXX 146
    # MT 147:12-20 = LXX 147:1-9
    if mt_psalm == 147:
        if mt_verse <= 11:
            return (146, mt_verse)
        else:
            return (147, mt_verse - 11)

    # MT 148-150 = LXX 148-150 (동일)
    if 148 <= mt_psalm <= 150:
        return (mt_psalm, mt_verse)

    raise ValueError(f"MT 시편 매핑 미정의: {mt_psalm}:{mt_verse}")


def lxx_to_mt(lxx_psalm: int, lxx_verse: int) -> Tuple[int, int]:
    """LXX 시편 번호 → MT 시편 번호. 절 번호 변경도 처리."""
    if not (1 <= lxx_psalm <= 151):
        raise ValueError(f"LXX 시편 범위 1-151 초과: {lxx_psalm}")

    if lxx_psalm == 151:
        return (-1, -1)  # MT에 없음

    # LXX 1-8 = MT 1-8
    if 1 <= lxx_psalm <= 8:
        return (lxx_psalm, lxx_verse)

    # LXX 9 — MT 9 또는 10
    if lxx_psalm == 9:
        # LXX 9:1-21 = MT 9:1-21
        # LXX 9:22-39 = MT 10:1-18
        if lxx_verse <= 21:
            return (9, lxx_verse)
        else:
            return (10, lxx_verse - 21)

    # LXX 10-112 = MT 11-113
    if 10 <= lxx_psalm <= 112:
        return (lxx_psalm + 1, lxx_verse)

    # LXX 113 — MT 114 또는 115
    if lxx_psalm == 113:
        if lxx_verse <= 8:
            return (114, lxx_verse)
        else:
            return (115, lxx_verse - 8)

    # LXX 114 = MT 116:1-9
    if lxx_psalm == 114:
        return (116, lxx_verse)

    # LXX 115 = MT 116:10-19
    if lxx_psalm == 115:
        return (116, lxx_verse + 9)

    # LXX 116-145 = MT 117-146
    if 116 <= lxx_psalm <= 145:
        return (lxx_psalm + 1, lxx_verse)

    # LXX 146 = MT 147:1-11
    if lxx_psalm == 146:
        return (147, lxx_verse)

    # LXX 147 = MT 147:12-20
    if lxx_psalm == 147:
        return (147, lxx_verse + 11)

    # LXX 148-150 = MT 148-150
    if 148 <= lxx_psalm <= 150:
        return (lxx_psalm, lxx_verse)

    raise ValueError(f"LXX 시편 매핑 미정의: {lxx_psalm}:{lxx_verse}")


def lookup(reference: str, psalm: int, verse: int) -> dict:
    """단일 진입점. 어느 기준이든 받아 세 형식 모두 반환."""
    ref = reference.upper()
    if ref == "MT":
        lxx = mt_to_lxx(psalm, verse)
    elif ref in ("LXX", "VG", "VULGATA"):
        # Vulgata는 LXX 번호 동일
        mt = lxx_to_mt(psalm, verse)
        if mt[0] == -1:
            return {
                "input": f"LXX/Vg {psalm}:{verse}",
                "mt": "MT에 없음 (LXX 151은 외경)",
                "lxx": f"{psalm}:{verse}",
                "vg": f"{psalm}:{verse}",
                "note": "사해사본 11Q5에 히브리어 원문 발견 (11QPs^a) 다만 MT 정경에는 없음.",
            }
        return {
            "input": f"LXX/Vg {psalm}:{verse}",
            "mt": f"{mt[0]}:{mt[1]}",
            "lxx": f"{psalm}:{verse}",
            "vg": f"{psalm}:{verse}",
            "note": "Vulgata Clementine·Nova Vulgata 모두 LXX 시편 번호 사용.",
        }
    else:
        raise ValueError(f"기준 미정의: {reference} (MT/LXX/VG 중 하나)")

    # 시편 내 절 번호 추가 차이 — 표제어를 LXX/Vg가 1-2절로 계수하는 시편이 있다
    # 다윗 시편 다수 (시 3·4·5·6·7·8·9·11-14·18-32·34-41·51-65·68-70·86·101·103·108-110·122·124·131·133·138-145) 등
    # 일반 규칙: 표제어가 긴 시편은 LXX/Vg 절 번호가 +1 또는 +2
    # 단순 규칙으로 결정 불가하므로 *플래그*만 표시
    psalms_with_offset_titles = {
        # 표제어가 LXX에서 2절로 늘어나는 대표 시편 (절 번호 +2)
        3, 4, 5, 6, 7, 8, 9, 12, 13, 18, 19, 20, 21, 22, 30, 31, 34, 36, 38,
        39, 40, 41, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64,
        65, 68, 69, 70, 75, 76, 77, 80, 81, 83, 84, 85, 88, 89, 92, 102,
        108, 140, 142,
    }
    title_offset_note = ""
    if psalm in psalms_with_offset_titles:
        title_offset_note = (
            f" ⚠ 추가 주의: MT 시 {psalm}편은 표제어 처리로 인해 LXX/Vg에서 *절 번호*가 "
            f"통상 +1 또는 +2 밀린다 (LXX/Vg는 표제어를 절로 계수, MT는 미계수). "
            f"예: MT 51:7 = Vg 50:9. 정확한 절 매핑은 Rahlfs LXX·Clementine 직접 대조 필요."
        )

    return {
        "input": f"MT {psalm}:{verse}",
        "mt": f"{psalm}:{verse}",
        "lxx": f"{lxx[0]}:{lxx[1]}",
        "vg": f"{lxx[0]}:{lxx[1]}",
        "note": (
            "한국어 성경(개역개정·새번역)은 MT 번호 사용. "
            "Vulgata Clementine·Nova Vulgata는 LXX 시편 번호 사용." + title_offset_note
        ),
    }


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    reference = sys.argv[1]
    chapter_verse = sys.argv[2]
    if ":" not in chapter_verse:
        print("장:절 형식으로 입력 (예: 23:1)")
        sys.exit(1)
    parts = chapter_verse.split(":")
    psalm = int(parts[0])
    verse = int(parts[1]) if len(parts) > 1 else 1

    result = lookup(reference, psalm, verse)
    print()
    print(f"입력: {result['input']}")
    print(f"MT (히브리어/개역개정/한국어): 시 {result['mt']}")
    print(f"LXX (70인역):                  시 {result['lxx']}")
    print(f"Vulgata (Clementine/Nova):     Ps {result['vg']}")
    print(f"비고: {result['note']}")
    print()


# 자체 테스트
def _self_test():
    """결정적 lookup의 자체 검증."""
    tests = [
        ("MT", 23, 1, "22:1"),  # 가장 유명한 변환
        ("MT", 22, 1, "21:1"),  # 메시아 시편
        ("MT", 51, 1, "50:1"),  # 회개시
        ("MT", 19, 1, "18:1"),
        ("MT", 110, 1, "109:1"),  # "주께서 내 주께"
        ("MT", 119, 1, "118:1"),  # 가장 긴 시편
        ("MT", 1, 1, "1:1"),  # 동일 구간
        ("MT", 9, 1, "9:1"),  # 통합 구간
        ("MT", 10, 1, "9:22"),  # MT 10 = LXX 9의 뒷부분
        ("MT", 116, 1, "114:1"),  # 분할 구간 앞
        ("MT", 116, 10, "115:1"),  # 분할 구간 뒤
        ("MT", 147, 1, "146:1"),  # 분할 구간 앞
        ("MT", 147, 12, "147:1"),  # 분할 구간 뒤
        ("MT", 150, 1, "150:1"),  # 마지막 동일
    ]
    failures = []
    for ref, ps, vs, expected in tests:
        result = lookup(ref, ps, vs)
        if result["lxx"] != expected:
            failures.append(f"  FAIL: MT {ps}:{vs} → 기대 LXX {expected}, 실제 {result['lxx']}")

    # 역방향 테스트
    rev_tests = [
        ("LXX", 22, 1, "23:1"),
        ("LXX", 21, 1, "22:1"),
        ("LXX", 50, 1, "51:1"),
        ("LXX", 9, 22, "10:1"),
        ("LXX", 113, 1, "114:1"),
        ("LXX", 113, 9, "115:1"),
        ("LXX", 114, 1, "116:1"),
        ("LXX", 115, 1, "116:10"),
        ("LXX", 146, 1, "147:1"),
        ("LXX", 147, 1, "147:12"),
    ]
    for ref, ps, vs, expected in rev_tests:
        result = lookup(ref, ps, vs)
        if result["mt"] != expected:
            failures.append(f"  FAIL: LXX {ps}:{vs} → 기대 MT {expected}, 실제 {result['mt']}")

    if failures:
        print("자체 테스트 실패:")
        for f in failures:
            print(f)
        return False
    print(f"자체 테스트 통과 ({len(tests) + len(rev_tests)}건)")
    return True


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        sys.exit(0 if _self_test() else 1)
    main()
