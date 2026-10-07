#!/usr/bin/env python3
"""
audit_claims.py — 스킬 출력의 모든 주장을 *출처 종류*로 분류 감사

본 도구는 출력 텍스트의 각 주장(claim)을 다음 카테고리로 분류:
  - DETERMINISTIC_DB: lookup_verified_citation 검증 데이터베이스에서 추출 (vulgata/quran/talmud)
  - DETERMINISTIC_CALC: lookup_psalm_numbering / lookup_jeremiah_numbering 결정론적 계산
  - LLM_TRAINING_TEXT: LLM 학습 데이터에서 추출한 본문 인용 (KRV/NIV/원어/LXX/천주교 성경/추가 번역) — *외부 검증 필요*
  - LLM_REASONING: LLM 분석/추론 (차이점·공통점·번역 포인트·종합 통찰) — 학술적 정직성 평가 필요
  - FALLBACK_DISCLOSURE: 자신 없음·미등재 명시
  - SKILL_BOILERPLATE: 헤더·구조 텍스트

본 분류는 *투명성*을 위한 것. LLM_TRAINING_TEXT는 사용자가 1차 출처(vatican.va·Bible Gateway·STEPbible)에서 외부 검증하기를 권장.

Usage:
  python3 audit_claims.py <파일경로>
  cat output.md | python3 audit_claims.py -
"""

from __future__ import annotations
import sys
import re
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from lookup_verified_citation import VULGATA_FACTS, QURAN_FACTS, TALMUD_FACTS


def audit(text: str) -> dict:
    lines = text.splitlines()
    audit_report = []

    current_section = "PREAMBLE"
    in_layer = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue

        # 섹션 헤더 탐지
        if stripped.startswith("# "):
            current_section = "HEADER"
            audit_report.append({"line": i + 1, "type": "SKILL_BOILERPLATE", "content": stripped[:80], "section": current_section})
            continue
        if stripped.startswith("## "):
            current_section = stripped[3:].split("—")[0].strip()
            audit_report.append({"line": i + 1, "type": "SKILL_BOILERPLATE", "content": stripped[:80], "section": current_section})
            continue
        if stripped.startswith("### "):
            # Layer 식별
            layer_match = re.match(r"###\s+(\d+)\)", stripped)
            if layer_match:
                in_layer = int(layer_match.group(1))
            audit_report.append({"line": i + 1, "type": "SKILL_BOILERPLATE", "content": stripped[:80], "section": current_section})
            continue

        # 인용 (>) 처리
        if stripped.startswith(">"):
            content = stripped.lstrip("> ").strip()
            if not content:
                continue

            # Vulgata layer (5번)
            if in_layer == 5:
                # 데이터베이스 매칭 확인
                db_match = False
                for ref, data in VULGATA_FACTS.items():
                    if data["clementine"][:30] in content or data.get("nova_vulgata", "")[:30] in content:
                        db_match = True
                        audit_report.append({
                            "line": i + 1, "type": "DETERMINISTIC_DB",
                            "content": content[:80],
                            "verification": f"VULGATA_FACTS['{ref}']: {data.get('source', 'no source')}",
                            "scholarly": data.get("scholarly_reference", "no scholarly ref"),
                        })
                        break
                if not db_match:
                    # 미등재 또는 fallback
                    if re.search(r"미확정|자신 없음|미등재|확인 필요|verify externally", content):
                        audit_report.append({"line": i + 1, "type": "FALLBACK_DISCLOSURE", "content": content[:80]})
                    elif "출처:" in content:
                        audit_report.append({"line": i + 1, "type": "DETERMINISTIC_DB", "content": content[:80]})
                    else:
                        audit_report.append({
                            "line": i + 1, "type": "LLM_TRAINING_TEXT",
                            "content": content[:80],
                            "verification": "*외부 검증 필요* — vatican.va·Stuttgart Vulgate 직접 대조",
                        })

            # 한국어/NIV/원어/LXX/Catholic/추가 번역 layer (1~4·6~7)
            elif in_layer in (1, 2, 3, 4, 6, 7):
                layer_names = {1: "개역개정", 2: "NIV", 3: "원어", 4: "반대 원어", 6: "천주교", 7: "추가 번역"}
                if "해당 없음" in content or "원문 없음" in content:
                    audit_report.append({"line": i + 1, "type": "SKILL_BOILERPLATE", "content": content[:80]})
                elif re.search(r"미확정|자신 없음|확인 필요", content):
                    audit_report.append({"line": i + 1, "type": "FALLBACK_DISCLOSURE", "content": content[:80]})
                else:
                    audit_report.append({
                        "line": i + 1, "type": "LLM_TRAINING_TEXT",
                        "content": content[:80],
                        "verification": f"*외부 검증 필요* — {layer_names.get(in_layer)} 1차 출처 대조 (Bible Gateway·STEPbible·한국천주교주교회의)",
                    })

            # 코란 layer (8)
            elif in_layer == 8:
                # QURAN_FACTS 매칭 시도
                matched = False
                for topic, data in QURAN_FACTS.items():
                    if data["sura"] in content or topic in content:
                        matched = True
                        audit_report.append({
                            "line": i + 1, "type": "DETERMINISTIC_DB",
                            "content": content[:80],
                            "verification": f"QURAN_FACTS['{topic}']: {data['sura']}",
                        })
                        break
                if not matched:
                    if re.search(r"직접 대응 본문 없음|미등재|확인되지 않음", content):
                        audit_report.append({"line": i + 1, "type": "FALLBACK_DISCLOSURE", "content": content[:80]})
                    else:
                        audit_report.append({
                            "line": i + 1, "type": "LLM_TRAINING_TEXT",
                            "content": content[:80],
                            "verification": "*외부 검증 필요* — Quran.com·김용선·최영길역 직접 대조",
                        })

            # 탈무드 layer (9)
            elif in_layer == 9:
                matched = False
                for topic, data in TALMUD_FACTS.items():
                    if data["ref"] in content or topic in content:
                        matched = True
                        audit_report.append({
                            "line": i + 1, "type": "DETERMINISTIC_DB",
                            "content": content[:80],
                            "verification": f"TALMUD_FACTS['{topic}']: {data['ref']}",
                        })
                        break
                if not matched:
                    if re.search(r"직접 대응 없음|미등재|확인되지 않음", content):
                        audit_report.append({"line": i + 1, "type": "FALLBACK_DISCLOSURE", "content": content[:80]})
                    else:
                        audit_report.append({
                            "line": i + 1, "type": "LLM_TRAINING_TEXT",
                            "content": content[:80],
                            "verification": "*외부 검증 필요* — Sefaria.org·Soncino영역판 직접 대조",
                        })

        # 분석 본문 (>) 가 아닌 단락
        else:
            if current_section in ("2. 차이점 분석", "3. 공통점 분석", "4. 번역 포인트", "5. 종합 통찰"):
                audit_report.append({"line": i + 1, "type": "LLM_REASONING", "content": stripped[:80], "section": current_section})

    return audit_report


def summarize(audit_report):
    types = {}
    for entry in audit_report:
        t = entry["type"]
        types[t] = types.get(t, 0) + 1
    return types


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    if sys.argv[1] == "-":
        text = sys.stdin.read()
    else:
        with open(sys.argv[1], encoding="utf-8") as f:
            text = f.read()

    report = audit(text)
    summary = summarize(report)

    print()
    print("=== 주장 감사 결과 ===")
    print(f"총 {len(report)}개 주장 분류")
    print()
    print("[분포]")
    for k, v in sorted(summary.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}건")
    print()

    # 결정론적 vs LLM 비율
    deterministic = summary.get("DETERMINISTIC_DB", 0) + summary.get("DETERMINISTIC_CALC", 0)
    llm = summary.get("LLM_TRAINING_TEXT", 0) + summary.get("LLM_REASONING", 0)
    total_substantive = deterministic + llm
    if total_substantive > 0:
        det_pct = 100 * deterministic / total_substantive
        llm_pct = 100 * llm / total_substantive
        print(f"[학술적 검증 가능 비율]")
        print(f"  결정론적(DB·계산): {deterministic}건 ({det_pct:.1f}%)")
        print(f"  LLM (외부 검증 필요): {llm}건 ({llm_pct:.1f}%)")
        print()

    # LLM_TRAINING_TEXT 항목들의 외부 검증 출처 명시
    llm_items = [r for r in report if r["type"] == "LLM_TRAINING_TEXT"]
    if llm_items:
        print(f"[LLM 학습 데이터에서 추출된 본문 인용 — 사용자가 외부 검증해야 할 항목]")
        for item in llm_items[:5]:
            print(f"  line {item['line']}: {item['content'][:60]}")
            print(f"    → {item.get('verification', '')}")
        if len(llm_items) > 5:
            print(f"  ... 외 {len(llm_items) - 5}건")
        print()


def _self_test():
    """감사 도구 자체 테스트."""
    failures = []

    # 결정론적 DB 매칭 — 등재된 Vulgata 본문
    test_text_db = """
### 5) 라틴어 Vulgata
> Clementine: In principio erat Verbum, et Verbum erat apud Deum, et Deus erat Verbum.
"""
    report = audit(test_text_db)
    types = summarize(report)
    if "DETERMINISTIC_DB" not in types:
        failures.append(f"  FAIL: 등재 Vulgata 본문이 DETERMINISTIC_DB로 분류되지 않음: {types}")

    # LLM_TRAINING_TEXT — 한국어 KRV
    test_text_krv = """
### 1) 개역개정 (KRV)
> 하나님이 세상을 이처럼 사랑하사
"""
    report = audit(test_text_krv)
    types = summarize(report)
    if "LLM_TRAINING_TEXT" not in types:
        failures.append(f"  FAIL: KRV 인용이 LLM_TRAINING_TEXT로 분류되지 않음: {types}")

    # FALLBACK_DISCLOSURE — 미확정 표기
    test_text_fb = """
### 5) 라틴어 Vulgata
> [본문 표기 미확정 — 사용자 확인 필요]
"""
    report = audit(test_text_fb)
    types = summarize(report)
    if "FALLBACK_DISCLOSURE" not in types:
        failures.append(f"  FAIL: 미확정 표기가 FALLBACK_DISCLOSURE로 분류되지 않음: {types}")

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
