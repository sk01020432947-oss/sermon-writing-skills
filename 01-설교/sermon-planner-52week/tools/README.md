# sermon-planner-52week 할루시네이션 차단 도구

LLM이 임의로 생성할 위험이 있는 4가지 영역(절기 주차·찬송가 번호·성경 본문·자체 출력)을 결정적(deterministic) Python 함수로 검증한다. SKILL.md의 자체 점검 단계에서 *반드시* 호출한다.

## 4종 도구

### 1. `easter_calculator.py` — 절기 자동 산출

특정 연도(예: 2027)를 입력하면 부활주일·성령강림·종려·재의수요일·성탄·송구영신·대강절·신년·맥추·추수감사·종교개혁·어린이·어버이·광복절·추도주일 등 모든 주요 절기의 정확한 날짜와 N주차를 산출한다.

**알고리즘**: 그레고리력 부활절 = Anonymous Gregorian Algorithm (Meeus J. 1991, *Astronomical Algorithms* ch. 8). 1583년 이후 모든 연도 정확.

**사용**:
```bash
python3 tools/easter_calculator.py 2027
python3 tools/easter_calculator.py 2027 --json
```

**출력**: 텍스트(사람용) 또는 JSON. 절기 충돌(같은 주차 둘 이상 절기) 자동 감지.

### 2. `hymn_validator.py` — 새찬송가 번호-제목 검증

LLM이 추천한 (번호, 제목) 쌍이 검증된 풀(총 100여 곡 — references/hymn_themes.md, liturgical_calendar.md에서 추출)에 있는지 확인.

**검증 방식**: 번호 존재 → 제목 일치(정규화 비교) → 두 단계.

**사용**:
```bash
python3 tools/hymn_validator.py validate 305 "나 같은 죄인 살리신"
python3 tools/hymn_validator.py list           # 전체 풀
python3 tools/hymn_validator.py search 부활    # 키워드 검색
python3 tools/hymn_validator.py themes 부활    # 주제별 풀
python3 tools/hymn_validator.py json          # 전체 JSON
```

### 3. `bible_validator.py` — 성경 본문 정경 범위 검증

LLM이 인용한 본문(예: "벧전 1:6", "시 151:1")이 정경 66권의 실제 장·절 범위 안에 있는지 확인. 책 약어를 정규화(예: "벧전" → "베드로전서").

**데이터 출처**: 개역개정 정경(66권 / 1,189장 / 31,103절) — BibleGateway·BibleHub 다중 검증.

**사용**:
```bash
python3 tools/bible_validator.py 벧전 1:3-5      # 정상
python3 tools/bible_validator.py 시 151:1        # 오류 (정경 밖)
python3 tools/bible_validator.py stats           # 통계
```

### 4. `sermon_plan_validator.py` — 통합 출력 검증

위 3개 도구를 결합하여 한 주차 또는 전체 plan을 JSON 입력으로 검증.

**스키마** (요약):
```json
{
  "year": 2027,
  "keyword": "소망",
  "weeks": [
    {"week": 1, "observance": "신년주일", "primary_text": "벧전 1:3-5",
     "parallel_texts": ["...", "..."],
     "hymns": [[64, "기뻐하며 경배하세"], ...]}
  ],
  "trend_notes": [{"quarter": 1, "topic": "...", "text": "..."}]
}
```

**사용**:
```bash
python3 tools/sermon_plan_validator.py plan.json
python3 tools/sermon_plan_validator.py --stdin < plan.json
```

**검증 항목**:
- 본문 정경 범위
- 찬송가 번호-제목 매핑
- 절기 표기와 자동 산출 일치
- 주차 중복
- 분기당 트렌드 적용 빈도
- 절기 충돌 보고

## SKILL.md에서의 호출 순서

1. 사용자가 연도를 명시(또는 "올해") → `easter_calculator.py <year>` 호출하여 모든 절기 주차를 받음.
2. 키워드별 본문 풀에서 *주본문·병행본문 후보*를 선정한 후, 각 본문에 대해 `bible_validator.py` 호출.
3. 찬송가 5곡 선정 후 각 쌍에 대해 `hymn_validator.py validate` 호출 (또는 5곡 묶어 `validate_set` 함수 import 호출).
4. 52주 완성된 plan에 대해 마지막에 `sermon_plan_validator.py` 일괄 호출. issues 비어있어야 출력.

도구가 fail하면:
- 본문 오류 → 풀 안의 다른 본문으로 변경
- 찬송가 오류 → 풀 안 다른 곡으로 변경 또는 "회중 친숙곡 1곡"으로 우회
- 절기 충돌 → SKILL.md 절기 우선순위 규약 적용
- 도구 실행 자체 실패 → 사용자에게 명확히 보고하고 진행 중단
