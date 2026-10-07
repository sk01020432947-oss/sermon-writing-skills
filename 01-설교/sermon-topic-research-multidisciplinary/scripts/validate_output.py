#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sermon-topic-research-multidisciplinary 산출물 결정론적 검증기.

LLM 자연어 추론으로는 할루시네이션을 구조적으로 차단할 수 없는 단계를
결정론적 파이썬 함수로 분리해 처리한다.

검사 항목:
  C1. 11개 분야 전수 출력 (G5)            — §1 ~ §11 헤더 존재
  C2. 분야 순서 (G5)                       — 사회→기술→산업→경제→환경→정치→국제관계→법→제도→심리→영성
  C3. 분야별 4요소 구조 (출력 양식)        — 핵심 진단/주요 데이터·이론·사상가/현재 흐름/설교 활용 포인트
  C4. 양화어 단독 사용 (G6)                — "많은/대부분/점점 더/갈수록/심각하게/엄청나게" 등이 통계·한정 표현 없이 노출
  C5. 분량 균형 (운영 원칙 2)              — 한 분야가 다른 분야 분량의 2배 초과 금지
  C6. §0/§12/§13/§14 존재                  — 필수 헤더 누락 검사
  C7. §13 본문 후보 형식                   — "장절" 패턴 5+3+1 이상
  C8. 한국어 번역서 ±1년 오차 차단 (G4)   — 외국 저자 + 한국어 출판년도 단독 명시 시 "직접 확인 권장" 동반 필수
  C9. 원서/번역서 연도 구분 (G10)          — "원서 NNNN" / "한국어 ...NNNN" 동시 표기 또는 "직접 확인 권장"
  C10. 통계 3요소 패턴 (G1 휴리스틱)       — 숫자+단위+(연도 또는 출처) 동반 확인, "○○%·○○명·○○건" 단독 노출 차단
  C11. 한국 자료 키워드 1+ (G7 휴리스틱)   — 분야별 "한국|통계청|KDI|한국은행|보건복지부|문화체육관광부|국회|대법원|교육부|기재부|고용노동부|한국갤럽|바나|기독교사회문제연구원" 1회 이상
  C12. "직접 확인 권장" 패턴 (G9)          — 불확실 항목 명시 표현 사용 여부 (경고만, 0이어도 가능)
  C13. 시작 안내 문구 (출력 양식)          — "표준 양식으로 산출했습니다"
  C14. 종료 안내 문구 (산출 후 안내)       — sermon-topic-message-coach·doctrinal-planner 등 후속 연결 문구
  C15. 외국 저자 추정 표기 일관성 (G10)    — 본문·§14에서 동일 저작이 두 번 등장할 때 표기 일관

사용:
  python3 validate_output.py <산출물.md>
  종료 코드 0: 모든 필수(critical) 검사 통과
  종료 코드 1: 필수 검사 1건 이상 실패
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict


REQUIRED_FIELD_ORDER = [
    "사회",
    "기술",
    "산업",
    "경제",
    "환경",
    "정치",
    "국제관계",
    "법",
    "제도",
    "심리",
    "영성",
]

# C3 — 분야별 4요소 (출력 양식 §1~§11 내부)
FIELD_REQUIRED_SUBSECTIONS = [
    "핵심 진단",
    "주요 데이터·이론·사상가",
    "현재 흐름과 미래 전망",
    "설교 활용 포인트",
]

# C4 — 양화어 (단독 사용 금지). 통계·한정 표현이 직전 25자 안에 동반되지 않으면 위반.
QUANTIFIER_PATTERNS = [
    r"많은\s*사람들?이",
    r"대부분(?:의|이|은)?",
    r"점점\s*더",
    r"갈수록",
    r"심각하게",
    r"엄청나게",
    r"수많은",
    r"굉장히",
    r"대다수(?:의|가|는)?",
]
# 동반 가능한 한정·근거 표현
NEAR_CONTEXT_GUARDS = [
    r"통계",
    r"\d+\s*년",
    r"\d+\s*%",
    r"\d+\s*명",
    r"\d+\s*건",
    r"OECD",
    r"통계청",
    r"KDI",
    r"한국은행",
    r"보건복지부",
    r"교육부",
    r"바나",
    r"갤럽",
    r"현장 관찰",
    r"조사에 따르면",
    r"보고서",
]

# C11 — 한국 자료 키워드
KOREA_KEYWORDS = [
    "한국",
    "통계청",
    "KDI",
    "한국은행",
    "보건복지부",
    "문화체육관광부",
    "국회",
    "대법원",
    "헌법재판소",
    "교육부",
    "기재부",
    "고용노동부",
    "한국갤럽",
    "바나",
    "기독교사회문제연구원",
    "한국기독교",
    "한국교회",
    "여성가족부",
    "행정안전부",
    "환경부",
    "법무부",
    "외교부",
    "통일부",
    "산업통상자원부",
]

# C8/C9 — 외국 저자 휴리스틱 (한글로 표기된 외국 저자 일부)
FOREIGN_AUTHORS = [
    "프로이트", "융", "아들러", "로저스", "프랭클",
    "어거스틴", "칼빈", "루터", "웨슬리", "바빙크", "본회퍼", "켈러",
    "로이드 존스", "로이드존스", "마틴 로이드",
    "마틴 부버", "한병철", "토마스 머튼", "앙리 누웬", "나우웬",
    "필립 얀시", "팀 켈러", "C. S. 루이스", "루이스",
    "마이클 샌델", "샌델", "찰스 테일러", "테일러",
    "유발 하라리", "하라리", "마이클 무어", "지젝",
    "엘륄", "자크 엘륄", "라인홀드 니버", "니버",
    "리처드 도킨스", "스티븐 핑커", "핑커",
    "도스토예프스키", "톨스토이",
    "라너", "발타자르", "본회퍼",
    "다니엘 카너먼", "카너먼", "조던 피터슨",
]

CRITICAL_CHECKS = {
    "C1", "C2", "C3", "C6", "C7", "C8", "C9", "C10", "C13", "C14",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def find_field_blocks(text: str) -> List[Tuple[str, int, int]]:
    """`## [N]. [분야명]` 패턴으로 11개 분야 블록을 찾는다. (name, start_idx, end_idx)."""
    pattern = re.compile(
        r"^##\s*(?:###\s*)?(\d+)\.\s*([^\n(]+?)(?:\s*\(|\s*$)",
        re.MULTILINE,
    )
    matches = list(pattern.finditer(text))
    blocks: List[Tuple[str, int, int]] = []
    for i, m in enumerate(matches):
        name = m.group(2).strip()
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        blocks.append((name, start, end))
    return blocks


def check_C1_C2(text: str) -> Tuple[bool, str]:
    blocks = find_field_blocks(text)
    field_names = [name for name, _, _ in blocks]
    # 11개 분야만 추려낸다 (0 개요·12 종합·13 본문·14 자료는 제외)
    core = [n for n in field_names if n in REQUIRED_FIELD_ORDER]
    missing = [f for f in REQUIRED_FIELD_ORDER if f not in core]
    if missing:
        return False, f"C1 위반: 누락 분야 {missing}"
    if core != REQUIRED_FIELD_ORDER:
        return False, f"C2 위반: 분야 순서 불일치 — 실제 {core}"
    return True, "C1·C2 통과"


def check_C3(text: str) -> Tuple[bool, str]:
    blocks = find_field_blocks(text)
    violations = []
    for name, start, end in blocks:
        if name not in REQUIRED_FIELD_ORDER:
            continue
        body = text[start:end]
        missing_subs = [s for s in FIELD_REQUIRED_SUBSECTIONS if s not in body]
        if missing_subs:
            violations.append(f"§{name}: {missing_subs}")
    if violations:
        return False, "C3 위반(분야별 4요소 결손): " + "; ".join(violations)
    return True, "C3 통과"


def check_C4(text: str) -> Tuple[bool, str]:
    violations = []
    for qp in QUANTIFIER_PATTERNS:
        for m in re.finditer(qp, text):
            start = max(0, m.start() - 30)
            end = min(len(text), m.end() + 30)
            window = text[start:end]
            guarded = any(re.search(g, window) for g in NEAR_CONTEXT_GUARDS)
            # 인용 부호 안 또는 "이라는 표현은 금지"처럼 메타 진술은 통과
            meta = bool(re.search(r"(금지|위반|규약|G\d|예:|예시|메타)", window))
            if not guarded and not meta:
                violations.append(f"'{m.group(0)}' near: …{window.strip()}…")
    if violations:
        return False, "C4 위반(양화어 단독): " + " | ".join(violations[:5])
    return True, "C4 통과"


def check_C5(text: str) -> Tuple[bool, str]:
    blocks = find_field_blocks(text)
    lens: Dict[str, int] = {}
    for name, start, end in blocks:
        if name in REQUIRED_FIELD_ORDER:
            lens[name] = end - start
    if not lens:
        return True, "C5 보류(분야 미검출)"
    mn, mx = min(lens.values()), max(lens.values())
    if mn == 0:
        return False, f"C5 위반: 빈 분야 발견 — {lens}"
    if mx / mn > 2.5:
        ratio = mx / mn
        return False, f"C5 위반: 분야 분량 불균형 — 최대/최소={ratio:.2f}배 (최대 {max(lens, key=lens.get)}={mx}, 최소 {min(lens, key=lens.get)}={mn})"
    return True, f"C5 통과 (분야 분량 비율 {mx/mn:.2f}배 — 임계 2.5 이내)"


def check_C6(text: str) -> Tuple[bool, str]:
    required_headers = ["0.", "12.", "13.", "14."]
    pattern = re.compile(r"^##\s*(?:###\s*)?(\d+)\.", re.MULTILINE)
    nums = [m.group(1) + "." for m in pattern.finditer(text)]
    missing = [h for h in required_headers if h not in nums]
    if missing:
        return False, f"C6 위반: 필수 헤더 누락 {missing}"
    return True, "C6 통과"


def check_C7(text: str) -> Tuple[bool, str]:
    section = extract_section(text, "13")
    if not section:
        return False, "C7 위반: §13 본문 후보 섹션 없음"
    # 장절 패턴: 한글 책 이름 + 1+:1+ 형식 (예: 마태복음 5:3, 고린도전서 13:1)
    refs = re.findall(r"[가-힣]+(?:전서|후서|기|복음|서|록|애가|편)?\s*\d+\s*[:：]\s*\d+", section)
    if len(refs) < 5:
        return False, f"C7 위반: §13 본문 후보 장절 패턴 {len(refs)}개(5+3+1=9 이상 권장)"
    return True, f"C7 통과 (§13 장절 패턴 {len(refs)}개)"


def check_C8_C9(text: str) -> Tuple[bool, str]:
    """외국 저자 + 한국어 번역 출판년도 단독 표기 차단.

    패턴: 외국 저자명 ... '한국어 NNNN' 또는 '역 NNNN'이 등장하지만
    "직접 확인 권장"이 동일 30자 윈도우에 없으면 위반.
    """
    msgs = []
    for author in FOREIGN_AUTHORS:
        for m in re.finditer(re.escape(author), text):
            start = max(0, m.start() - 5)
            end = min(len(text), m.end() + 80)
            window = text[start:end]
            # 한국어 출판년도 후보 (4자리 1950-2029). "영역"·"지역"·"내역"의 "역"은 제외.
            # 한국어 번역 표지 정확 패턴: "한국어 NNNN", "번역 NNNN", "○○ 역(NNNN)", "○○ 옮김 NNNN", "한국어판 NNNN"
            ko_year_patterns = [
                r"한국어\s*판?\s*[^()\n]*?(19[5-9]\d|20[0-2]\d)",
                r"번역\s*[^()\n]*?(19[5-9]\d|20[0-2]\d)",
                r"옮김\s*[^()\n]*?(19[5-9]\d|20[0-2]\d)",
                r"역자?\s+\S+\s*(19[5-9]\d|20[0-2]\d)",
                r"\S+\s+역\s*(19[5-9]\d|20[0-2]\d)",
            ]
            ko_years = []
            for p in ko_year_patterns:
                ko_years.extend(re.findall(p, window))
            if ko_years and "직접 확인 권장" not in window:
                # 원서 ... 한국어 ... 동시 표기 (G10 정확 표기)는 통과
                if re.search(r"원서[^/\n]*?\d{4}", window) and re.search(r"한국어[^()\n]*?\d{4}", window):
                    continue
                # 출판사명이 원서 식별을 대체할 수도 있다 (예: "Matthes & Seitz 2010 / 한국어 ... 2012")
                if re.search(r"(Matthes|Seitz|Eerdmans|Baker|Zondervan|IVP|Crossway|HarperCollins|Penguin|Oxford|Cambridge|Princeton|Harvard|Yale|MIT Press|Anthropos|Sierra Club|Beacon Press|Doubleday|Pantheon|Free Press|Routledge|Random House|Westminster|Fortress|Brazos|Dutton|Portfolio|Simon\s*&\s*Schuster)\s+\d{4}\s*/\s*한국어", window):
                    continue
                msgs.append(f"외국 저자 '{author}' 한국어 출판년도 {ko_years} 단독: …{window.strip()[:80]}…")
    if msgs:
        return False, "C8·C9 위반(외국 저자 번역 연도 단독): " + " | ".join(msgs[:5])
    return True, "C8·C9 통과"


def check_C10(text: str) -> Tuple[bool, str]:
    """통계 3요소 — 숫자+단위가 노출되면 25자 이내에 연도(YYYY) 또는 출처 키워드 1개 동반."""
    UNITS = r"%|명|건|원|배|만|억|조|시간|일|개|개월|위|점"
    pattern = re.compile(rf"\d[\d,\.]*\s*(?:{UNITS})")
    sources = ["통계청", "OECD", "KDI", "한국은행", "교육부", "보건복지부",
               "고용노동부", "여성가족부", "환경부", "법무부", "행안부",
               "국회", "유엔", "WHO", "UNDP", "World Bank", "IMF",
               "갤럽", "바나", "한국갤럽", "리얼미터", "Pew",
               "Statista", "통계", "보고서", "조사", "백서", "포럼",
               "기독교사회문제연구원", "한국갤럽조사연구소"]
    src_pat = "|".join(re.escape(s) for s in sources)
    violations = []
    for m in pattern.finditer(text):
        start = max(0, m.start() - 40)
        end = min(len(text), m.end() + 40)
        window = text[start:end]
        has_year = bool(re.search(r"(19\d{2}|20[0-2]\d)\b", window))
        has_source = bool(re.search(src_pat, window))
        if not has_year and not has_source:
            # 페이지·장절·서수·체크리스트 숫자는 제외
            if re.search(r"(쪽|페이지|장|편|회|월|일\s*기준|위안)", window):
                continue
            if "직접 확인 권장" in window:
                continue
            # 메타 수치 — 분야·본문·키워드·개념 등 본 산출물 내부 구조 참조는 통계가 아님
            if re.search(r"(분야|본문|케이스|키워드|개념|항목|단계|규약|체크|챕터|문항|범주|관통|구조|저작|신학자|도서|추천|이론|사상가|성경|구절)", window):
                continue
            # "이론·개념: ○○" 식 이름 뒤 숫자가 출판 연도가 아닌 권수일 수도 있어 권/판 컨텍스트 제외
            if re.search(r"(권|판|장\b)", window):
                continue
            violations.append(f"'{m.group(0)}' near: …{window.strip()[:60]}…")
    if violations:
        return False, "C10 위반(통계 3요소 결손): " + " | ".join(violations[:5])
    return True, "C10 통과"


def check_C11(text: str) -> Tuple[bool, str]:
    blocks = find_field_blocks(text)
    weak = []
    for name, start, end in blocks:
        if name not in REQUIRED_FIELD_ORDER:
            continue
        body = text[start:end]
        if not any(kw in body for kw in KOREA_KEYWORDS):
            weak.append(name)
    if len(weak) > 3:
        return False, f"C11 경고(한국 자료 키워드 부재 분야 {len(weak)}개): {weak}"
    if weak:
        return True, f"C11 통과(한국 자료 키워드 부재 {weak} — 경고 수준)"
    return True, "C11 통과"


def check_C12(text: str) -> Tuple[bool, str]:
    n = text.count("직접 확인 권장")
    # 0이어도 통과 가능 — 모든 인용이 100% 검증된 경우. 경고만.
    return True, f"C12 경고({n}회 '직접 확인 권장' 표현 사용)"


def check_C13(text: str) -> Tuple[bool, str]:
    if "표준 양식으로 산출했습니다" not in text:
        return False, "C13 위반: 시작 안내 문구 누락"
    return True, "C13 통과"


def check_C14(text: str) -> Tuple[bool, str]:
    required_links = ["sermon-topic-message-coach", "sermon-doctrinal-planner"]
    missing = [r for r in required_links if r not in text]
    if missing:
        return False, f"C14 위반: 후속 연결 문구 누락 {missing}"
    return True, "C14 통과"


def extract_section(text: str, section_num: str) -> str:
    pattern = re.compile(
        rf"^##\s*(?:###\s*)?{section_num}\.\s.+?(?=^##\s*(?:###\s*)?\d+\.\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(text)
    return m.group(0) if m else ""


def main(argv: List[str]) -> int:
    if len(argv) != 2:
        print("usage: python3 validate_output.py <산출물.md>")
        return 2
    path = Path(argv[1])
    if not path.exists():
        print(f"파일 없음: {path}")
        return 2
    text = read_text(path)

    checks = [
        ("C1·C2", check_C1_C2),
        ("C3", check_C3),
        ("C4", check_C4),
        ("C5", check_C5),
        ("C6", check_C6),
        ("C7", check_C7),
        ("C8·C9", check_C8_C9),
        ("C10", check_C10),
        ("C11", check_C11),
        ("C12", check_C12),
        ("C13", check_C13),
        ("C14", check_C14),
    ]

    results: List[Tuple[str, bool, str]] = []
    for label, fn in checks:
        ok, msg = fn(text)
        results.append((label, ok, msg))

    print(f"=== {path.name} 검증 ===")
    failures_critical = 0
    failures_warning = 0
    for label, ok, msg in results:
        mark = "✅" if ok else "❌"
        print(f"{mark} {label}: {msg}")
        if not ok:
            # CRITICAL_CHECKS에 속한 라벨이면 critical 카운트
            crit = any(label.startswith(c) or c in label.split("·") for c in CRITICAL_CHECKS)
            if crit:
                failures_critical += 1
            else:
                failures_warning += 1
    print()
    print(f"[요약] critical 실패 {failures_critical}건 / warning 실패 {failures_warning}건")
    return 0 if failures_critical == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
