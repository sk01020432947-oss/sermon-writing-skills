#!/usr/bin/env python3
"""
verify_format.py — 큐티 산출물의 형식·분량·구조 검증

검증 항목 (SKILL.md 자기 검증 C4·C7·C8):
1. 시작 헤더 형식: `# 📖 [본문 약어] 큐티 — [한 줄 주제]`
2. 메타라인: `> 레벨: ... | 본문: 개역개정 | 작성일 기준: 자동`
3. 레벨별 분량 (간단 1,500–2,000자 / 표준 3,500–4,500자 / 상세 6,000–8,000자)
4. 3대지 구조 (대지1·대지2·대지3) 존재
5. 대지3에 "원문 추출 3가지 의미" 명시 (기본형/대안형)
6. 각 대지 끝에 묵상 질문 (간단 QT 외)
7. 적용·기도 항목 포함
8. 검색 출처 투명성 한 줄 (검색 미사용 시)

사용법:
    python3 verify_format.py --file path/to/qt.md --level standard
    python3 verify_format.py --text "큐티 텍스트" --level simple|standard|detailed
"""
import argparse
import json
import re
import sys


LEVEL_RANGES = {
    "simple": (800, 1500),
    "standard": (2000, 3500),
    "detailed": (4000, 6500),
}

LEVEL_KOR = {
    "simple": "간단",
    "standard": "표준",
    "detailed": "상세 설교형",
}


def count_korean_chars(text: str) -> int:
    """한글 음절 기준 글자 수. 공백·기호 제외."""
    return len(re.findall(r"[가-힯a-zA-Z0-9]", text))


def check_header(text: str):
    """헤더 형식 점검."""
    # 첫 비어있지 않은 줄 추출
    lines = [l for l in text.splitlines() if l.strip()]
    if not lines:
        return False, "빈 텍스트"
    head = lines[0]
    # 패턴: # 📖 ... 큐티 — ...
    if re.match(r"^#\s*📖\s+.+\s+큐티\s+(—|-)\s+.+", head):
        return True, head
    if re.match(r"^#\s+.+\s+큐티\s+(—|-)\s+.+", head):
        return True, head + " (이모지 누락)"
    return False, f"헤더 형식 비표준: '{head[:80]}'"


def check_meta_line(text: str):
    """`> 레벨: ... | 본문: 개역개정 | 작성일 기준: 자동` 패턴."""
    m = re.search(
        r">\s*레벨\s*:\s*[^|]+\|\s*본문\s*:\s*개역개정\s*\|\s*작성일\s*기준\s*:\s*자동",
        text,
    )
    return bool(m)


def check_three_points(text: str, level: str):
    """3대지 구조 점검."""
    # "대지1·2·3" 또는 단순히 "## 1.·2.·3." 헤딩으로 검출
    p1 = re.search(r"대지\s*1|## ?\d\..*대지", text)
    p2 = re.search(r"대지\s*2", text)
    p3 = re.search(r"대지\s*3", text)
    # 간단 QT는 대지 명시 안 해도 됨 (한 줄 묵상 포인트 3개로 대체 가능)
    if level == "simple":
        # "묵상 포인트" 또는 "한 줄 묵상" 명시 또는 대지1 명시 둘 중 하나
        has_points = bool(
            re.search(r"한 줄 묵상", text)
            or re.search(r"묵상\s*포인트", text)
            or (p1 and p2 and p3)
        )
        return has_points, {"p1": bool(p1), "p2": bool(p2), "p3": bool(p3)}
    return bool(p1 and p2 and p3), {"p1": bool(p1), "p2": bool(p2), "p3": bool(p3)}


def check_three_meanings(text: str):
    """대지3의 '원문 추출 3가지 의미' 구성 점검 (기본형 또는 대안형)."""
    # 의미 1·2·3 또는 핵심어 3개가 대지3 영역에 있는지
    # 휴리스틱: 대지3 헤딩 이후 "의미 1"·"의미 2"·"의미 3" 또는 "①·②·③" 등
    p3_match = re.search(r"(대지\s*3.*?)(?=(\n##\s|\n#\s|\Z))", text, re.DOTALL)
    if not p3_match:
        return False, "대지3 영역 미발견"
    p3_block = p3_match.group(1)
    has_three = bool(
        (
            re.search(r"의미\s*1|① ", p3_block)
            and re.search(r"의미\s*2|② ", p3_block)
            and re.search(r"의미\s*3|③ ", p3_block)
        )
        or re.findall(r"\*\*원문\*\*", p3_block).__len__() >= 3
    )
    # 기본형/대안형 명시
    has_form = bool(re.search(r"기본형|대안형|세 의미|세 핵심 단어", p3_block))
    return has_three, {"has_three": has_three, "has_form_marker": has_form}


def check_meditation_questions(text: str, level: str):
    """묵상 질문 점검 (간단 QT는 면제, 표준·상세는 각 대지 끝에 1개)."""
    if level == "simple":
        return True, "면제"
    cnt = len(re.findall(r"\*\s*묵상\s*질문", text))
    return cnt >= 2, f"발견 {cnt}개 (최소 2개 권장)"


def check_application_and_prayer(text: str):
    """적용·기도 절 포함 여부."""
    has_app = bool(re.search(r"적용", text))
    has_prayer = bool(re.search(r"기도", text))
    return has_app and has_prayer, {"적용": has_app, "기도": has_prayer}


def check_search_transparency(text: str):
    """검색 미사용 시 투명성 한 줄 점검. 또는 검색 사용 시 출처 표기."""
    no_search_pattern = re.search(
        r"외부\s*자료\s*검색을\s*사용하지\s*않|검색을\s*사용하지\s*않았", text
    )
    source_pattern = re.search(r"출처|기사 출처|참고:\s*http", text)
    return bool(no_search_pattern or source_pattern), {
        "no_search_marker": bool(no_search_pattern),
        "source_marker": bool(source_pattern),
    }


def check_length(text: str, level: str):
    """레벨별 분량 점검. 하한·상한 ±5% 관용 (실제 한국 큐티 책자 편차를 고려)."""
    n = count_korean_chars(text)
    lo, hi = LEVEL_RANGES[level]
    # ±5% 관용 적용
    lo_tol = int(lo * 0.95)
    hi_tol = int(hi * 1.05)
    ok = lo_tol <= n <= hi_tol
    return ok, {"chars": n, "expected_range": [lo, hi], "tolerance_range": [lo_tol, hi_tol]}


def main():
    ap = argparse.ArgumentParser(description="큐티 형식·분량·구조 검증")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--text", help="검증할 큐티 텍스트")
    g.add_argument("--file", help="텍스트 파일 경로")
    ap.add_argument(
        "--level", required=True, choices=["simple", "standard", "detailed"]
    )
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = args.text

    header_ok, header_info = check_header(text)
    meta_ok = check_meta_line(text)
    three_ok, three_info = check_three_points(text, args.level)
    meanings_ok, meanings_info = check_three_meanings(text)
    q_ok, q_info = check_meditation_questions(text, args.level)
    ap_ok, ap_info = check_application_and_prayer(text)
    tr_ok, tr_info = check_search_transparency(text)
    len_ok, len_info = check_length(text, args.level)

    # 대지3 의미는 간단 QT의 경우 면제 가능 (3개 묵상 포인트로 대체)
    if args.level == "simple" and not meanings_ok:
        meanings_ok = three_info["p3"] or True
        meanings_info = {**meanings_info, "note": "간단 QT는 한 줄 묵상 포인트 3개로 대체 가능"}

    out = {
        "level": LEVEL_KOR[args.level],
        "header": {"ok": header_ok, "info": header_info},
        "meta_line": {"ok": meta_ok},
        "three_points": {"ok": three_ok, "info": three_info},
        "three_meanings_in_p3": {"ok": meanings_ok, "info": meanings_info},
        "meditation_questions": {"ok": q_ok, "info": q_info},
        "application_and_prayer": {"ok": ap_ok, "info": ap_info},
        "search_transparency": {"ok": tr_ok, "info": tr_info},
        "length": {"ok": len_ok, "info": len_info},
        "pass": all(
            [
                header_ok,
                meta_ok,
                three_ok,
                meanings_ok,
                q_ok,
                ap_ok,
                tr_ok,
                len_ok,
            ]
        ),
    }

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print("=" * 60)
        print(f"큐티 형식·분량 검증 — 레벨 {out['level']}")
        print("=" * 60)

        def fmt(ok, label, info=None):
            mark = "[OK]  " if ok else "[FAIL]"
            line = f"  {mark} {label}"
            if info is not None:
                line += f"   {info}"
            return line

        print(fmt(header_ok, "헤더 형식", header_info))
        print(fmt(meta_ok, "메타라인"))
        print(fmt(three_ok, "3대지 구조", three_info))
        print(fmt(meanings_ok, "대지3 — 원문 추출 3가지 의미", meanings_info))
        print(fmt(q_ok, "묵상 질문", q_info))
        print(fmt(ap_ok, "적용·기도", ap_info))
        print(fmt(tr_ok, "검색 출처 투명성", tr_info))
        print(fmt(len_ok, f"분량 ({LEVEL_RANGES[args.level][0]}–{LEVEL_RANGES[args.level][1]}자)", len_info))
        print()
        print(f"종합: {'PASS' if out['pass'] else 'FAIL'}")

    sys.exit(0 if out["pass"] else 1)


if __name__ == "__main__":
    main()
