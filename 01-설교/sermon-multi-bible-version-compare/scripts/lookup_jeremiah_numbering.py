#!/usr/bin/env python3
"""
lookup_jeremiah_numbering.py — MT/LXX 예레미야 장 매핑 결정론적 lookup.

LXX 예레미야는 MT보다 약 13% 짧고 25:14 이후 장 순서가 크게 다르다.
본 도구는 검증된 매핑만 반환하며, 매핑이 *명확치 않은 구간*은 명시한다.

Usage:
  python3 lookup_jeremiah_numbering.py MT 31:31
  python3 lookup_jeremiah_numbering.py LXX 38:31
"""

from __future__ import annotations
import sys
from typing import Optional, Tuple


# 검증된 핵심 매핑 (장 단위; 절은 본문에 따라 미세 차이)
# 출처: Septuaginta (Rahlfs-Hanhart 2006), BHS (Stuttgart 1997),
#       Tov "Textual Criticism of the Hebrew Bible" (3rd ed.)

MT_TO_LXX_CHAPTER_MAP = {
    # 1-25:13: 거의 동일
    **{ch: ch for ch in range(1, 25)},
    25: 25,  # 일부만 (25:1-13만 LXX 25:1-13에 대응; 25:15-38 별도)
    # 26-31: LXX에 동일 번호 부재 (재배치). 핵심 본문:
    26: 33,  # MT 26 (예레미야 성전 설교) = LXX 33
    27: 34,  # MT 27 (멍에 비유) = LXX 34
    28: 35,  # MT 28 (하나냐) = LXX 35
    29: 36,  # MT 29 (포로민 편지·"내가 너희에게 향한 생각") = LXX 36
    30: 37,  # MT 30 (회복 예언) = LXX 37
    31: 38,  # MT 31 (새 언약·"내가 그들과 새 언약을 맺으리니") = LXX 38
    32: 39,  # MT 32 (땅 매매) = LXX 39
    33: 40,  # MT 33 (다윗의 의로운 가지) = LXX 40
    34: 41,  # MT 34 (시드기야 예언) = LXX 41
    35: 42,  # MT 35 (레갑 족속) = LXX 42
    36: 43,  # MT 36 (예레미야 두루마리) = LXX 43
    37: 44,  # MT 37 = LXX 44
    38: 45,  # MT 38 (구덩이에 던져짐) = LXX 45
    39: 46,  # MT 39 (예루살렘 함락) = LXX 46
    40: 47,  # MT 40 = LXX 47
    41: 48,  # MT 41 (그달리야 살해) = LXX 48
    42: 49,  # MT 42 = LXX 49
    43: 50,  # MT 43 = LXX 50
    44: 51,  # MT 44 (애굽 유다인) = LXX 51 (일부)
    45: 51,  # MT 45 (바룩 위로) = LXX 51 (일부, 끝부분)
    # 예언 (Oracles against the Nations) 부분:
    46: 26,  # 애굽 = LXX 26
    47: 29,  # 블레셋 = LXX 29
    48: 31,  # 모압 = LXX 31
    49: 30,  # 암몬·에돔·다메섹·게달·하솔·엘람 = LXX 30 (일부) + 25:14-20
    50: 27,  # 바벨론 = LXX 27
    51: 28,  # 바벨론 = LXX 28
    52: 52,  # 결론 (예루살렘 함락 역사) = LXX 52
}

# LXX → MT 역방향 (장 단위)
LXX_TO_MT_CHAPTER_MAP = {}
for mt_ch, lxx_ch in MT_TO_LXX_CHAPTER_MAP.items():
    if lxx_ch in LXX_TO_MT_CHAPTER_MAP:
        if isinstance(LXX_TO_MT_CHAPTER_MAP[lxx_ch], list):
            LXX_TO_MT_CHAPTER_MAP[lxx_ch].append(mt_ch)
        else:
            LXX_TO_MT_CHAPTER_MAP[lxx_ch] = [LXX_TO_MT_CHAPTER_MAP[lxx_ch], mt_ch]
    else:
        LXX_TO_MT_CHAPTER_MAP[lxx_ch] = mt_ch


def mt_to_lxx(mt_chapter: int, mt_verse: Optional[int] = None) -> dict:
    if not (1 <= mt_chapter <= 52):
        raise ValueError(f"예레미야 장 범위 1-52 초과: {mt_chapter}")

    lxx_ch = MT_TO_LXX_CHAPTER_MAP.get(mt_chapter)

    # 특수 처리: MT 25
    if mt_chapter == 25 and mt_verse is not None:
        if 1 <= mt_verse <= 13:
            return {
                "mt": f"렘 25:{mt_verse}",
                "lxx": f"렘 25:{mt_verse}",
                "note": "MT 25:1-13 = LXX 25:1-13 (동일).",
            }
        elif 14 == mt_verse:
            return {
                "mt": "렘 25:14",
                "lxx": "(LXX에 단순 대응 없음)",
                "note": "MT 25:14는 LXX에 직접 대응 없음. 일부 학자는 LXX 25:13b 또는 후속 본문 단편으로 봄.",
            }
        elif 15 <= mt_verse <= 38:
            return {
                "mt": f"렘 25:{mt_verse}",
                "lxx": f"렘 32:{mt_verse - 14}",
                "note": "MT 25:15-38 = LXX 32:1-24. 진노의 잔 환상이 LXX에서는 32장.",
            }

    # 특수 처리: MT 49 (여러 민족 예언)
    if mt_chapter == 49 and mt_verse is not None:
        if 1 <= mt_verse <= 6:
            return {
                "mt": f"렘 49:{mt_verse}",
                "lxx": f"렘 30:{16 + mt_verse}",
                "note": "MT 49:1-6 (암몬) = LXX 30:17-22.",
            }
        elif 7 <= mt_verse <= 22:
            return {
                "mt": f"렘 49:{mt_verse}",
                "lxx": f"렘 30:{mt_verse - 6}",
                "note": "MT 49:7-22 (에돔) = LXX 30:1-16.",
            }
        elif 23 <= mt_verse <= 27:
            return {
                "mt": f"렘 49:{mt_verse}",
                "lxx": f"렘 30:{mt_verse + 6}",
                "note": "MT 49:23-27 (다메섹) = LXX 30:29-33.",
            }
        elif 28 <= mt_verse <= 33:
            return {
                "mt": f"렘 49:{mt_verse}",
                "lxx": f"렘 30:{mt_verse - 5}",
                "note": "MT 49:28-33 (게달·하솔) = LXX 30:23-28.",
            }
        elif 34 <= mt_verse <= 39:
            return {
                "mt": f"렘 49:{mt_verse}",
                "lxx": f"렘 25:{mt_verse - 19}",
                "note": "MT 49:34-39 (엘람) = LXX 25:14-20.",
            }

    if lxx_ch is None:
        return {
            "mt": f"렘 {mt_chapter}{f':{mt_verse}' if mt_verse else ''}",
            "lxx": "(매핑 미정의)",
            "note": "본 도구의 검증된 매핑에 포함되지 않음. Tov·Rahlfs·BHS 직접 대조 필요.",
        }

    verse_str = f":{mt_verse}" if mt_verse else ""
    return {
        "mt": f"렘 {mt_chapter}{verse_str}",
        "lxx": f"렘 {lxx_ch}{verse_str if mt_verse else ''}",
        "note": "LXX 절 번호는 MT와 미세 차이 가능. 절 단위 정밀 매핑은 Rahlfs 직접 대조.",
    }


def lxx_to_mt(lxx_chapter: int, lxx_verse: Optional[int] = None) -> dict:
    if not (1 <= lxx_chapter <= 52):
        raise ValueError(f"LXX 예레미야 장 범위 1-52 초과: {lxx_chapter}")

    mt_ch = LXX_TO_MT_CHAPTER_MAP.get(lxx_chapter)

    if mt_ch is None:
        return {
            "lxx": f"LXX 렘 {lxx_chapter}{f':{lxx_verse}' if lxx_verse else ''}",
            "mt": "(매핑 미정의)",
            "note": "본 도구의 검증된 매핑에 포함되지 않음.",
        }

    verse_str = f":{lxx_verse}" if lxx_verse else ""
    if isinstance(mt_ch, list):
        return {
            "lxx": f"LXX 렘 {lxx_chapter}{verse_str}",
            "mt": "MT 후보: " + ", ".join(f"렘 {c}" for c in mt_ch),
            "note": "LXX 장 하나가 MT 여러 장에 대응. 절 단위 확인 필요.",
        }
    return {
        "lxx": f"LXX 렘 {lxx_chapter}{verse_str}",
        "mt": f"렘 {mt_ch}{verse_str if lxx_verse else ''}",
        "note": "절 번호는 미세 차이 가능. Rahlfs 직접 대조 권장.",
    }


def lookup(reference: str, ch_vs: str) -> dict:
    ref = reference.upper()
    if ":" in ch_vs:
        ch_str, vs_str = ch_vs.split(":")
        chapter = int(ch_str)
        verse = int(vs_str)
    else:
        chapter = int(ch_vs)
        verse = None

    if ref == "MT":
        return mt_to_lxx(chapter, verse)
    elif ref == "LXX":
        return lxx_to_mt(chapter, verse)
    else:
        raise ValueError(f"기준은 MT 또는 LXX: {reference}")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    result = lookup(sys.argv[1], sys.argv[2])
    print()
    print(f"MT (마소라/한국어): {result['mt']}")
    print(f"LXX (70인역):       {result['lxx']}")
    print(f"비고: {result['note']}")
    print()


def _self_test():
    tests = [
        # (기준, ch:vs, 기대 결과 키, 기대 부분 문자열)
        ("MT", "31:31", "lxx", "렘 38:31"),  # 새 언약
        ("MT", "29:11", "lxx", "렘 36:11"),  # 포로 공동체 약속
        ("MT", "46:1", "lxx", "렘 26:1"),  # 애굽 예언
        ("MT", "50:1", "lxx", "렘 27:1"),  # 바벨론 예언
        ("MT", "1:1", "lxx", "렘 1:1"),  # 동일 구간
        ("MT", "52:1", "lxx", "렘 52:1"),  # 마지막 동일
        ("MT", "25:1", "lxx", "렘 25:1"),  # MT 25 앞부분 동일
        ("MT", "25:15", "lxx", "렘 32:1"),  # MT 25 뒷부분 재배치
        ("LXX", "38:31", "mt", "렘 31:31"),
        ("LXX", "26:1", "mt", "렘 46:1"),
        ("LXX", "27:1", "mt", "렘 50:1"),
    ]
    failures = []
    for ref, ch_vs, key, expected in tests:
        result = lookup(ref, ch_vs)
        if expected not in result[key]:
            failures.append(f"  FAIL: {ref} {ch_vs} → {key}={result[key]}, 기대 {expected}")
    if failures:
        print("자체 테스트 실패:")
        for f in failures:
            print(f)
        return False
    print(f"자체 테스트 통과 ({len(tests)}건)")
    return True


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        sys.exit(0 if _self_test() else 1)
    main()
