#!/usr/bin/env python3
"""
verify_output_structure.py — 9 layer 비교 출력 구조 검증

본 도구는 본 스킬의 최종 출력 텍스트를 받아 다음을 검사한다:
1. 본문 헤더 ("# ... 다중 번역 비교") 존재
2. 9개 layer (1~9번) 모두 존재
3. 차이점 분석 (A·B·C·D 4섹션)
4. 공통점 분석
5. 번역 포인트 (각 layer별 포인트)
6. 종합 통찰
7. 후속 안내

Usage:
  python3 verify_output_structure.py <파일경로>
  cat output.md | python3 verify_output_structure.py -
"""

from __future__ import annotations
import re
import sys


REQUIRED_LAYERS = [
    ("1. 개역개정", r"###?\s*1\)\s*개역개정|개역개정\s*\(KRV"),
    ("2. NIV", r"###?\s*2\)\s*(?:New International Version|NIV)|영어\s*NIV"),
    ("3. 원어 (헬라어/히브리어)", r"###?\s*3\)\s*원어|GNT|BHS|헬라어|히브리어"),
    ("4. 반대 원어 (LXX/해당 없음)", r"###?\s*4\)\s*(?:반대\s*원어|70인역|LXX|히브리어\s*해당\s*없음)"),
    ("5. Vulgata", r"###?\s*5\)\s*(?:라틴어\s*)?Vulgata|Vg"),
    ("6. 천주교 성경", r"###?\s*6\)\s*(?:한국\s*)?천주교\s*성경|RC"),
    ("7. 추가 번역", r"###?\s*7\)\s*추가\s*번역|ESV|NASB|새번역|KJV|NLT"),
    ("8. 코란", r"###?\s*8\)\s*코란|Quran|Qur"),
    ("9. 탈무드", r"###?\s*9\)\s*탈무드|Talmud"),
]

REQUIRED_SECTIONS = [
    ("본문 헤더", r"^#\s+.*다중\s*번역\s*비교", re.MULTILINE),
    ("9개 본문 나란히 보기", r"##?\s*1\.\s*9개\s*본문\s*나란히\s*보기", 0),
    ("차이점 분석", r"##?\s*2\.\s*차이점\s*분석", 0),
    ("차이점 A 어휘", r"###?\s*A\.\s*어휘\s*선택\s*차이|###?\s*A\.\s*어휘", 0),
    ("차이점 B 문장구조", r"###?\s*B\.\s*문장\s*구조\s*차이|###?\s*B\.\s*문장", 0),
    ("차이점 C 신학", r"###?\s*C\.\s*신학적\s*강조점", 0),
    ("차이점 D 종교 전통", r"###?\s*D\.\s*종교\s*전통", 0),
    ("공통점 분석", r"##?\s*3\.\s*공통점\s*분석", 0),
    ("번역 포인트", r"##?\s*4\.\s*번역\s*포인트", 0),
    ("종합 통찰", r"##?\s*5\.\s*종합\s*통찰", 0),
]


def check_structure(text: str) -> dict:
    issues = []

    # 필수 섹션
    for name, pattern, flags in REQUIRED_SECTIONS:
        if not re.search(pattern, text, flags):
            issues.append(f"섹션 누락: {name}")

    # 9개 layer
    for name, pattern in REQUIRED_LAYERS:
        if not re.search(pattern, text):
            issues.append(f"Layer 누락: {name}")

    # 후속 안내
    if not re.search(r"다른\s*본문|sermon-bible-dictionary|후속|이어서", text):
        issues.append("후속 안내 누락")

    # 분량 점검
    char_count = len(text)
    if char_count < 1500:
        issues.append(f"분량 부족: {char_count}자 (최소 2,500자 권장)")
    elif char_count > 12000:
        issues.append(f"분량 초과: {char_count}자 (최대 6,500자 권장)")

    return {"issues": issues, "total": len(issues), "char_count": char_count}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == "-":
        text = sys.stdin.read()
    else:
        with open(sys.argv[1], encoding="utf-8") as f:
            text = f.read()

    result = check_structure(text)
    print()
    print(f"=== 출력 구조 검증 결과 ===")
    print(f"분량: {result['char_count']}자")
    print(f"이슈 수: {result['total']}")
    print()
    if result["issues"]:
        for i, issue in enumerate(result["issues"], 1):
            print(f"  {i}. {issue}")
    else:
        print("  ✓ 모든 구조 통과")
    print()
    sys.exit(0 if result["total"] == 0 else 1)


def _self_test():
    """검증 도구 자체 테스트."""
    failures = []

    # 1. 정상 출력 모형
    good_output = """# 요 3:16 다중 번역 비교

## 📖 본문: 요한복음 3:16

## 1. 9개 본문 나란히 보기

### 1) 개역개정 (KRV)
> 하나님이 세상을 이처럼 사랑하사

### 2) New International Version (NIV)
> For God so loved the world

### 3) 원어 — 헬라어 GNT
> οὕτως γὰρ ἠγάπησεν ὁ θεὸς

### 4) 반대 원어 — 히브리어 해당 없음
> 신약 본문이므로 히브리어 원문 없음.

### 5) 라틴어 Vulgata (Vg) — Clementine
> Sic enim Deus dilexit mundum

### 6) 한국 천주교 성경
> 하느님께서는 세상을 너무나 사랑하신 나머지

### 7) 추가 번역: ESV
> For God so loved the world

### 8) 코란 — 대응 본문
> 직접 대응 본문 없음. 다만 코란 4:171 등이 예수의 정체에 대한 입장 명시.

### 9) 탈무드 — 대응 본문
> 직접 대응 없음.

## 2. 차이점 분석

### A. 어휘 선택 차이
어휘 차이.

### B. 문장 구조 차이
구조 차이.

### C. 신학적 강조점 차이
신학.

### D. 종교 전통 간 차이
종교 차이.

## 3. 공통점 분석
공통점.

## 4. 번역 포인트
포인트.

## 5. 종합 통찰
통찰.

---

다른 본문도 비교하시려면 알려 주세요.
""" * 3  # 분량 확보

    result = check_structure(good_output)
    if result["total"] > 0:
        failures.append(f"  FAIL: 정상 출력이 통과해야 하나 이슈 {result['issues']}")

    # 2. Layer 일부 누락
    bad_output = good_output.replace("### 8) 코란 — 대응 본문", "### 8) 누락된 layer")
    result = check_structure(bad_output)
    if not any("코란" in i for i in result["issues"]):
        failures.append(f"  FAIL: 코란 layer 누락 미감지: {result['issues']}")

    # 3. 차이점 D 누락
    bad_output2 = good_output.replace("### D. 종교 전통 간 차이", "### D2. 잘못된 섹션")
    result = check_structure(bad_output2)
    if not any("종교 전통" in i for i in result["issues"]):
        failures.append(f"  FAIL: 차이점 D 누락 미감지: {result['issues']}")

    if failures:
        print("자체 테스트 실패:")
        for f in failures:
            print(f)
        return False
    print("자체 테스트 통과 (3건)")
    return True


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        sys.exit(0 if _self_test() else 1)
    main()
