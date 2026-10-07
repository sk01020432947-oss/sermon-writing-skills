#!/usr/bin/env python3
"""새찬송가(2006년 통합찬송가) 번호-제목 검증기.

LLM이 임의로 생성한 (번호, 제목) 쌍이 references/hymn_themes.md·liturgical_calendar.md
풀 안에 있는지 확인하고, 풀 외 항목을 거부한다. 할루시네이션 차단의 핵심 도구.

Usage:
    python3 hymn_validator.py validate 305 "나 같은 죄인 살리신"
    python3 hymn_validator.py list                 # 전체 풀 출력
    python3 hymn_validator.py search 부활          # 키워드 검색
    python3 hymn_validator.py themes 부활          # 주제별 풀
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path
from typing import Optional

# 검증된 새찬송가 풀 (references 파일에서 추출·교차 검증된 항목만 등재)
# 출처: prayertents.com, hbible.co.kr, godpeople.or.kr 등 공개 목록 다중 일치 항목
VERIFIED_HYMNS: dict[int, str] = {
    # 1. 송영·삼위일체·창조
    1: "만복의 근원 하나님",
    8: "거룩 거룩 거룩 전능하신 주님",
    15: "하나님의 크신 사랑",
    21: "다 찬양하여라",
    32: "만유의 주재",
    40: "찬송으로 보답할 수 없는",
    64: "기뻐하며 경배하세",
    # 2. 성탄·대강절
    104: "곧 오소서 임마누엘",
    105: "오랫동안 기다리던",
    106: "아기 예수 나셨네",
    109: "고요한 밤 거룩한 밤",
    112: "그 맑고 환한 밤중에",
    115: "기쁘다 구주 오셨네",
    122: "참 반가운 성도여",
    123: "저 들 밖에 한밤중에",
    126: "천사 찬송하기를",
    # 3. 종려·고난·십자가
    138: "햇빛을 받는 곳마다",
    139: "오 영원한 내 주 예수",
    141: "호산나 호산나",
    145: "오 거룩하신 주님",
    147: "거기 너 있었는가",
    149: "주 달려 죽은 십자가",
    150: "갈보리산 위에",
    151: "만왕의 왕 주께서",
    152: "귀하신 예수",
    # 4. 부활·승천·재림
    162: "부활하신 구세주",
    164: "예수 부활했으니",
    166: "싸움은 모두 끝나고",
    169: "사망의 권세가",
    170: "내 주님은 살아 계셔",
    174: "대속하신 구주께서",
    176: "주 어느 때 다시 오실는지",
    # 5. 성령
    183: "빈 들에 마른 풀 같이",
    186: "영화로신 주 성령",
    191: "내가 매일 기쁘게",
    195: "성령이여 우리 찬송 부를 때",
    196: "성령이여 은사를",
    197: "은혜가 풍성한 하나님은",
    # 6. 말씀·구원·은혜
    202: "하나님 아버지 주신 책은",
    204: "주의 말씀 듣고서",
    214: "나 주의 도움 받고자",
    220: "사랑하는 주님 앞에",
    234: "구주 예수 그리스도",
    245: "저 좋은 낙원 이르니",
    252: "나의 죄를 씻기는",
    268: "죄에서 자유를 얻게 함은",
    270: "변찮는 주님의 사랑과",
    304: "그 크신 하나님의 사랑",
    305: "나 같은 죄인 살리신",
    # 7. 시련·위로·신뢰
    337: "내 모든 시험 무거운 짐을",
    338: "내 주를 가까이 하게 함은",
    341: "십자가를 내가 지고",
    363: "내 기도하는 그 시간",
    369: "죄 짐 맡은 우리 구주",
    372: "그 누가 나의 괴롬 알며",
    384: "나의 갈 길 다 가도록",
    387: "멀리 멀리 갔더니",
    391: "오 놀라운 구세주",
    400: "험한 시험 물 속에서",
    401: "주의 곁에 있을 때",
    405: "주의 친절한 팔에 안기세",
    408: "나 어느 곳에 있든지",
    410: "내맘에 한 노래 있어",
    # 8. 헌신·결단
    412: "내 영혼의 그윽히 깊은 데서",
    413: "내 평생에 가는 길",
    415: "십자가 그늘 아래",
    449: "예수 따라가며",
    450: "내 평생 소원 이것뿐",
    455: "주님의 마음을 본받는 자",
    461: "십자가를 질 수 있나",
    463: "신자 되기 원합니다",
    # 9. 천국·재림·종말
    489: "저 요단강 건너편에 찬란하게",
    491: "저 높은 곳을 향하여",
    493: "하늘 가는 밝은 길이",
    495: "익은 곡식 거둘 자가",
    # 10. 봉사·사명·전도
    496: "새벽부터 우리",
    497: "주 예수 넓은 사랑",
    502: "빛의 사자들이여",
    505: "온 세상 위하여",
    511: "예수 말씀하시기를",
    521: "구원하는 인도하는",
    # 11. 위로 고전
    543: "어려운 일 당할 때",
    545: "이 눈에 아무 증거 아니 뵈어도",
    # 12. 교회·공동체·가정
    550: "시온의 영광이 빛나는 아침",
    555: "우리 주님 모신 가정",
    559: "사철에 봄바람 불어 잇고",
    564: "예수 사랑하심을",
    565: "예수께로 가면",
    569: "선한 목자 되신 우리 주",
    570: "주는 나를 기르시는 목자",
    575: "주님께 귀한 것 드려",
    585: "내 주는 강한 성이요",
    # 13. 감사·자연
    587: "감사하는 성도여",
    588: "공중 나는 새를 보라",
    589: "넓은 들에 익은 곡식",
    590: "논밭에 오곡백과",
    591: "저 밭에 농부 나가",
    592: "산마다 불이 탄다 고운 단풍에",
    593: "아름다운 하늘과",
}

# 주제 → 추천 풀(범위)
THEME_RANGES: dict[str, list[tuple[int, int]]] = {
    "송영": [(1, 67)],
    "삼위일체": [(8, 8)],
    "창조": [(32, 32), (588, 593)],
    "성탄": [(104, 127)],
    "대강절": [(104, 122)],
    "종려": [(138, 141)],
    "고난": [(138, 161)],
    "십자가": [(145, 152)],
    "사순절": [(145, 161), (341, 341)],
    "부활": [(162, 170)],
    "승천": [(174, 176)],
    "재림": [(174, 176), (489, 495)],
    "성령": [(183, 197)],
    "말씀": [(202, 204)],
    "구원": [(214, 305)],
    "은혜": [(214, 305)],
    "시련": [(337, 372)],
    "위로": [(337, 408), (543, 545)],
    "신뢰": [(384, 410), (543, 545)],
    "회개": [(305, 305), (387, 387)],
    "헌신": [(412, 463)],
    "결단": [(412, 463)],
    "천국": [(489, 495)],
    "종말": [(489, 495)],
    "사명": [(496, 521)],
    "선교": [(502, 505)],
    "전도": [(496, 521)],
    "교회": [(550, 575)],
    "공동체": [(550, 585)],
    "가정": [(555, 559)],
    "어린이": [(564, 565)],
    "종교개혁": [(585, 585)],
    "감사": [(40, 40), (587, 593)],
    "맥추감사": [(587, 591)],
    "추수감사": [(587, 593), (304, 304)],
}


def is_valid_pair(number: int, title: str) -> tuple[bool, str]:
    """번호-제목 쌍이 검증 풀에 있는지 확인.

    Returns: (is_valid, message)
    """
    if number not in VERIFIED_HYMNS:
        return False, f"번호 {number}장이 새찬송가 검증 풀에 없음. 풀 안의 곡으로 변경하세요."
    expected = VERIFIED_HYMNS[number]
    norm_input = _normalize(title)
    norm_expected = _normalize(expected)
    if norm_input != norm_expected:
        return False, (
            f"번호 {number}장의 검증된 제목은 「{expected}」입니다. "
            f"입력한 「{title}」과 일치하지 않음. 제목을 정정하거나 다른 곡으로 변경하세요."
        )
    return True, f"✓ {number}장 「{expected}」 검증 통과"


def _normalize(s: str) -> str:
    """제목 비교용 정규화 — 공백·따옴표 제거, 소문자화."""
    return re.sub(r"[\s「」'\"]+", "", s).lower()


def get_title(number: int) -> Optional[str]:
    return VERIFIED_HYMNS.get(number)


def search(keyword: str) -> list[tuple[int, str]]:
    """제목에 키워드 포함된 곡 검색."""
    k = keyword.strip()
    return [(n, t) for n, t in VERIFIED_HYMNS.items() if k in t]


def by_theme(theme: str) -> list[tuple[int, str]]:
    """주제별 추천 풀."""
    ranges = THEME_RANGES.get(theme)
    if not ranges:
        return []
    result = []
    for lo, hi in ranges:
        for n, t in VERIFIED_HYMNS.items():
            if lo <= n <= hi:
                result.append((n, t))
    seen = set()
    deduped = []
    for n, t in result:
        if n not in seen:
            seen.add(n)
            deduped.append((n, t))
    return deduped


def validate_set(pairs: list[tuple[int, str]]) -> dict:
    """5곡 추천 세트를 일괄 검증.

    중복 번호·중복 제목·검증 실패 항목을 모두 보고.
    """
    issues = []
    number_seen = set()
    title_seen = set()
    for idx, (num, title) in enumerate(pairs, 1):
        ok, msg = is_valid_pair(num, title)
        if not ok:
            issues.append(f"#{idx} {msg}")
        if num in number_seen:
            issues.append(f"#{idx} 번호 {num}장이 중복 사용됨")
        number_seen.add(num)
        norm_title = _normalize(title)
        if norm_title in title_seen:
            issues.append(f"#{idx} 제목 「{title}」이 중복 사용됨")
        title_seen.add(norm_title)
    return {"valid": not issues, "issues": issues, "count": len(pairs)}


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd = sys.argv[1]
    if cmd == "validate":
        if len(sys.argv) < 4:
            print("사용: hymn_validator.py validate <번호> <제목>", file=sys.stderr)
            return 2
        try:
            num = int(sys.argv[2])
        except ValueError:
            print(f"번호가 정수가 아님: {sys.argv[2]}", file=sys.stderr)
            return 2
        title = sys.argv[3]
        ok, msg = is_valid_pair(num, title)
        print(msg)
        return 0 if ok else 3
    elif cmd == "list":
        for n in sorted(VERIFIED_HYMNS):
            print(f"{n:>4}장 「{VERIFIED_HYMNS[n]}」")
        print(f"\n총 {len(VERIFIED_HYMNS)}곡")
        return 0
    elif cmd == "search":
        if len(sys.argv) < 3:
            print("사용: hymn_validator.py search <키워드>", file=sys.stderr)
            return 2
        results = search(sys.argv[2])
        for n, t in results:
            print(f"{n:>4}장 「{t}」")
        print(f"\n{len(results)}곡 매칭")
        return 0
    elif cmd == "themes":
        if len(sys.argv) < 3:
            print("사용: hymn_validator.py themes <주제>", file=sys.stderr)
            print(f"가능한 주제: {', '.join(THEME_RANGES.keys())}")
            return 2
        results = by_theme(sys.argv[2])
        if not results:
            print(f"주제 '{sys.argv[2]}'에 해당하는 풀 없음")
            return 3
        for n, t in results:
            print(f"{n:>4}장 「{t}」")
        return 0
    elif cmd == "json":
        # 전체 풀을 JSON으로
        print(json.dumps({"hymns": VERIFIED_HYMNS, "themes": THEME_RANGES}, ensure_ascii=False, indent=2))
        return 0
    else:
        print(f"알 수 없는 명령: {cmd}", file=sys.stderr)
        print(__doc__)
        return 1


if __name__ == "__main__":
    sys.exit(main())
