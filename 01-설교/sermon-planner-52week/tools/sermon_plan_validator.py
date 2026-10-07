#!/usr/bin/env python3
"""sermon-planner-52week 출력 통합 검증기.

JSON 형식의 주차별 계획을 입력받아 (1) 본문 정경 범위 (2) 찬송가 번호-제목 매핑
(3) 절기 주차 일치 (4) 중복 등록 (5) 트렌드 적용 빈도를 모두 검증한다.

표준 입력 스키마:
{
  "year": 2027,
  "keyword": "소망",
  "weeks": [
    {
      "week": 1,
      "observance": "신년주일",
      "topic": "...",
      "primary_text": "벧전 1:3-5",
      "parallel_texts": ["사 43:18-19", "..."],
      "hymns": [[384, "나의 갈 길 다 가도록"], ...]
    },
    ...
  ],
  "trend_notes": [{"quarter": 1, "topic": "...", "text": "..."}]
}

Usage:
    python3 sermon_plan_validator.py plan.json
    python3 sermon_plan_validator.py --stdin < plan.json
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

# 같은 폴더 모듈 import
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from easter_calculator import compute_all_week_numbers  # noqa: E402
from hymn_validator import is_valid_pair, _normalize  # noqa: E402
from bible_validator import validate_reference  # noqa: E402


def validate_plan(plan: dict) -> dict:
    issues: list[str] = []
    warnings: list[str] = []

    year = plan.get("year")
    keyword = plan.get("keyword", "")
    weeks = plan.get("weeks", [])
    trend_notes = plan.get("trend_notes", [])

    if not isinstance(year, int):
        issues.append("year 필드 누락 또는 정수가 아님")
    if not weeks:
        issues.append("weeks 배열이 비어 있음")

    # 1. 연도별 자동 산출 절기 주차
    calendar_data = None
    if isinstance(year, int):
        try:
            calendar_data = compute_all_week_numbers(year)
        except Exception as e:
            issues.append(f"연도 {year} 절기 산출 실패: {e}")

    expected_observances: dict[int, list[str]] = {}
    if calendar_data:
        for name, info in calendar_data["weeks"].items():
            wk = info["week"]
            if isinstance(wk, int):
                expected_observances.setdefault(wk, []).append(name)

    # 2. 주차별 검증
    seen_weeks = set()
    for w in weeks:
        wn = w.get("week")
        if not isinstance(wn, int):
            issues.append(f"week 번호가 정수 아님: {w}")
            continue
        if wn in seen_weeks:
            issues.append(f"{wn}주차가 중복 등록됨")
        seen_weeks.add(wn)
        # 절기 일치
        obs = w.get("observance", "").strip()
        if obs and obs != "—":
            exp = expected_observances.get(wn, [])
            if exp and not any(obs in e or e in obs for e in exp):
                warnings.append(
                    f"{wn}주차 절기 표기 '{obs}'가 자동 산출 결과({', '.join(exp)})와 불일치"
                )
        # 본문 검증
        primary = w.get("primary_text", "").strip()
        if primary:
            ok, msg = validate_reference(primary)
            if not ok:
                issues.append(f"{wn}주차 주본문 '{primary}': {msg}")
        else:
            issues.append(f"{wn}주차 primary_text 누락")
        parallels = w.get("parallel_texts", [])
        for p in parallels:
            if not p:
                continue
            ok, msg = validate_reference(p)
            if not ok:
                issues.append(f"{wn}주차 병행본문 '{p}': {msg}")
        # 찬송가 검증
        hymns = w.get("hymns", [])
        seen_nums = set()
        seen_titles = set()
        for h in hymns:
            if not (isinstance(h, list) and len(h) == 2):
                issues.append(f"{wn}주차 찬송가 항목 형식 오류: {h}")
                continue
            num, title = h
            ok, msg = is_valid_pair(num, title)
            if not ok:
                issues.append(f"{wn}주차 찬송가: {msg}")
            if num in seen_nums:
                issues.append(f"{wn}주차 찬송가 번호 {num}장 중복")
            seen_nums.add(num)
            nt = _normalize(title)
            if nt in seen_titles:
                issues.append(f"{wn}주차 찬송가 제목 「{title}」 중복")
            seen_titles.add(nt)

    # 3. 트렌드 적용 빈도: 분기당 최소 1회
    quarter_trends: dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0}
    for t in trend_notes:
        q = t.get("quarter")
        if q in quarter_trends:
            quarter_trends[q] += 1
    for q, cnt in quarter_trends.items():
        if cnt < 1:
            warnings.append(f"Q{q} 트렌드 적용 포인트가 부족함 (현재 {cnt}회, 최소 1회 권장)")

    # 4. 자동 산출 충돌 보고
    if calendar_data and calendar_data.get("conflicts"):
        for wk, obs_list in calendar_data["conflicts"].items():
            warnings.append(
                f"⚠️ {wk}주차에 절기 충돌: {' + '.join(obs_list)} — SKILL.md 우선순위 규약 적용 필요"
            )

    return {
        "valid": not issues,
        "issues": issues,
        "warnings": warnings,
        "keyword": keyword,
        "year": year,
        "weeks_checked": len(seen_weeks),
    }


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    if sys.argv[1] == "--stdin":
        text = sys.stdin.read()
    else:
        text = Path(sys.argv[1]).read_text(encoding="utf-8")
    try:
        plan = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"JSON 파싱 실패: {e}", file=sys.stderr)
        return 2
    result = validate_plan(plan)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 3


if __name__ == "__main__":
    sys.exit(main())
