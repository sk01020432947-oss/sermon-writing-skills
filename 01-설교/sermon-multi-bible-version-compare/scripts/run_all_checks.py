#!/usr/bin/env python3
"""
run_all_checks.py — 본 스킬의 모든 검증 도구 통합 실행

본 스킬 출력 텍스트를 받아 다음을 모두 검사:
1. 출력 구조 (9 layer + 분석 섹션)
2. 인용 형식 (코란/탈무드/Vulgata)
3. 시편/예레미야 번호 (LXX/MT 차이)
4. caritas 오류
5. 흔한 오용 본문 컨텍스트

Usage:
  python3 run_all_checks.py <파일경로>
  cat output.md | python3 run_all_checks.py -
"""

from __future__ import annotations
import sys
import os

# 같은 디렉토리의 모듈 import
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from verify_output_structure import check_structure
from verify_citation_format import check_text


def check_misreadings(text: str) -> list[str]:
    """common-misreadings.md의 컨텍스트 오용 자동 점검."""
    import re
    issues = []

    misuse_patterns = [
        # (본문 패턴, 오용 신호 패턴, 정확 컨텍스트 신호 패턴, 메시지)
        (
            r"렘\s*29[:：]11|예레미야\s*29[:：]11|Jeremiah\s*29[:：]11",
            r"개인\s*번영|개인의?\s*[복꿈]|꿈을\s*이루|성공\s*약속|번영의?\s*약속",
            r"포로|70년|공동체|회복",
            "렘 29:11은 포로 공동체 회복 약속. 개인 번영 약속이 아님 (29:10 직전 컨텍스트).",
        ),
        (
            r"빌\s*4[:：]13|빌립보서\s*4[:：]13|Phil(ippians)?\s*4[:：]13",
            r"무한정\s*가능|무엇이든\s*가능|무제한",
            r"자족|만족|풍부\s*궁핍|배부르거나\s*주리거나",
            "빌 4:13은 자족의 비결. 무제한 가능을 약속하지 않음 (4:11-12).",
        ),
        (
            r"룻\s*1[:：]16|Ruth\s*1[:：]16",
            r"결혼\s*서약|혼인\s*맹세|배우자",
            r"시어머니|며느리|나오미",
            "룻 1:16은 시어머니-며느리 약속. 결혼 서약이 아님.",
        ),
        (
            r"마\s*18[:：]20|마태\s*18[:：]20|Matt(hew)?\s*18[:：]20",
            r"기도\s*모임|모임\s*임재|어디든\s*임재",
            r"권징|교회\s*권위|매고\s*풀고|책망",
            "마 18:20은 권징·교회 권위 컨텍스트 (18:15-20). 일반 모임 임재 약속이 아님.",
        ),
        (
            r"잠\s*22[:：]6|Proverbs?\s*22[:：]6",
            r"양육\s*약속|반드시\s*돌아온|확실한\s*약속",
            r"격언|일반\s*원칙|잠언",
            "잠 22:6은 잠언적 격언. 절대 약속이 아님.",
        ),
    ]

    for body_pat, misuse_pat, ctx_pat, msg in misuse_patterns:
        if re.search(body_pat, text):
            if re.search(misuse_pat, text) and not re.search(ctx_pat, text):
                issues.append(f"컨텍스트 오용 위험: {msg}")

    return issues


def run_all(text: str) -> dict:
    structure = check_structure(text)
    citation = check_text(text)
    misreadings = check_misreadings(text)

    return {
        "structure": structure,
        "citation": citation,
        "misreadings": {"issues": misreadings, "total": len(misreadings)},
        "grand_total": structure["total"] + citation["total"] + len(misreadings),
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    if sys.argv[1] == "-":
        text = sys.stdin.read()
    else:
        with open(sys.argv[1], encoding="utf-8") as f:
            text = f.read()

    result = run_all(text)

    print()
    print(f"=== 종합 검증 결과 ===")
    print(f"분량: {result['structure']['char_count']}자")
    print(f"총 이슈 수: {result['grand_total']}")
    print()
    print("[1. 출력 구조]")
    if result["structure"]["issues"]:
        for i, issue in enumerate(result["structure"]["issues"], 1):
            print(f"  {i}. {issue}")
    else:
        print("  ✓ 통과")
    print()
    print("[2. 인용 형식]")
    citation_total = result["citation"]["total"]
    if citation_total > 0:
        for cat, issues in result["citation"]["issues"].items():
            for issue in issues:
                print(f"  [{cat}] {issue}")
    else:
        print("  ✓ 통과")
    print()
    print("[3. 컨텍스트 오용]")
    if result["misreadings"]["issues"]:
        for i, issue in enumerate(result["misreadings"]["issues"], 1):
            print(f"  {i}. {issue}")
    else:
        print("  ✓ 통과")
    print()

    sys.exit(0 if result["grand_total"] == 0 else 1)


def _self_test():
    """종합 검증 도구 자체 테스트."""
    failures = []

    # 정상 출력 모형 — 모든 검증 통과해야
    good = """# 요 3:16 다중 번역 비교
## 📖 본문: 요한복음 3:16
## 1. 9개 본문 나란히 보기

### 1) 개역개정 (KRV)
> 본문

### 2) New International Version (NIV)
> For God so loved the world

### 3) 원어 — 헬라어 GNT
> 헬라어 본문

### 4) 반대 원어 — 히브리어 해당 없음
> 신약이므로.

### 5) 라틴어 Vulgata (Vg) Clementine
> Sic enim Deus dilexit mundum

### 6) 한국 천주교 성경
> 본문

### 7) 추가 번역: ESV
> 본문

### 8) 코란 — 대응 본문
> 직접 대응 본문 없음. 김용선역 인용.

### 9) 탈무드 — 대응 본문
> 직접 대응 없음.

## 2. 차이점 분석

### A. 어휘 선택 차이
어휘.
### B. 문장 구조 차이
구조.
### C. 신학적 강조점 차이
신학.
### D. 종교 전통 간 차이
종교 차이.

## 3. 공통점 분석
공통.

## 4. 번역 포인트
포인트.

## 5. 종합 통찰
통찰.

---

다른 본문도 비교하시려면 알려 주세요.
""" * 3

    result = run_all(good)
    if result["grand_total"] > 0:
        # 정상 출력이지만 미세 경고는 허용 — 다만 critical issue는 없어야
        critical_count = sum(
            1 for issues in result["citation"]["issues"].values()
            for i in issues if "CRITICAL" in i
        )
        if critical_count > 0:
            failures.append(f"  FAIL: 정상 출력에 CRITICAL 이슈 {critical_count}건")

    # 컨텍스트 오용 — 렘 29:11 + 개인 번영
    bad = good + "\n\n렘 29:11에 따르면 우리 개인의 꿈을 이루어 주실 것이다."
    result = run_all(bad)
    if not result["misreadings"]["issues"]:
        failures.append(f"  FAIL: 렘 29:11 개인 번영 오용 미감지: {result['misreadings']}")

    if failures:
        print("자체 테스트 실패:")
        for f in failures:
            print(f)
        return False
    print("자체 테스트 통과")
    return True


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        sys.exit(0 if _self_test() else 1)
    main()
