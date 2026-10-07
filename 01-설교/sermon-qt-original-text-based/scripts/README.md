# 검증 도구 (`scripts/`)

LLM 자가 점검의 한계(특히 토씨 단언·발음 표기 추측·비약 패턴 오감지)를 보완하여, 큐티 산출물의 **할루시네이션을 원천 봉쇄**하는 Python 도구 모음.

## 구성

```
scripts/
├── verify_all.py                  # C1-C8 통합 진입점
├── verify_quote.py                # C1: 인용 정확성 (KRV/GAE)
├── verify_transliteration.py      # C2·C3: 원어 한글 표기
├── verify_misapplication.py       # C5·C6: 비약·이단 패턴
├── verify_format.py               # C4·C7·C8: 형식·분량·투명성
└── data/
    ├── krv_gae_differences.json   # 빈출 토씨 차이
    ├── transliteration_rules.json # 표기 표준 + 단어 사전
    ├── verified_passages.json     # GAE 본문 정답
    └── misapplication_patterns.json # 비약·이단 패턴
```

## 표준 사용법

큐티 산출 후 사용자에게 응답하기 직전:

```bash
python3 scripts/verify_all.py \
    --file /tmp/qt_draft.md \
    --level standard \
    --refs "잠 3:5,잠 3:6" \
    --passage-ref "잠 3:5-6"
```

매개변수:
- `--file` 또는 `--text`: 검증할 큐티 텍스트
- `--level`: `simple` / `standard` / `detailed`
- `--refs`: 산출물에 직접 인용한 모든 구절 (콤마 구분)
- `--passage-ref`: 대표 본문 약어 (비약 패턴 점검용)
- `--json`: JSON 출력 (다른 도구와 연계 시)

## 결과 해석

- **ALL PASS**: 사용자에게 응답
- **하나라도 FAIL**: 해당 부분 재작성 → 재검증
- **2회 재작성 후에도 FAIL**: 응답에 *"○○ 본문은 ○○ 사유로 일반 산출에 제약이 있어 부분 보완 인용으로 처리했습니다"* 한 줄 안내

## 개별 도구 사용

각 모듈은 단독 실행도 가능:

```bash
# 인용 정확성만
python3 scripts/verify_quote.py --file qt.md --refs "롬 12:1"

# 원어 표기만 (수동 입력)
python3 scripts/verify_transliteration.py --pairs "ἀγάπη:아가페" "χάρις:카리스"

# 원어 표기만 (자동 추출)
python3 scripts/verify_transliteration.py --file qt.md

# 비약 패턴만
python3 scripts/verify_misapplication.py --file qt.md --ref "빌 4:13"

# 형식·분량만
python3 scripts/verify_format.py --file qt.md --level standard
```

## 데이터 확장

신규 본문·새 KRV/GAE 차이·새 비약 패턴을 발견하면 `data/*.json`에 추가:

- `verified_passages.json` — 새 본문의 GAE 표준 인용 추가 (`"롬 12:3": "..."`)
- `krv_gae_differences.json` — 새 토씨 차이 (`passages` 또는 `patterns_krv_to_gae`)
- `transliteration_rules.json` — 새 헬·히 단어 (`greek_standard_words` 또는 `hebrew_standard_words`)
- `misapplication_patterns.json` — 새 함정 본문 (`passage_specific_traps`)

JSON 갱신 후 코드 수정 없이 즉시 효과 발휘.

## 환경 제약 대응

Python 실행 불가 환경에서는 SKILL.md의 *환경 제약 대응* 절을 따르되, 다음을 순서대로 점검:

1. KRV/GAE 빈출 패턴표 (`references/krv-vs-gae-differences.md`) 1회 대조
2. 원어 한글 표기 표준표 (`references/original-language-transliteration-standard.md`) 1회 대조
3. 본문 비약 사례 (`references/common-misapplication-cases.md`) 해당 본문 포함 여부 점검
4. 산출물 끝에 *"본문 인용은 개역개정판으로 직접 한 번 더 확인하시기 바랍니다"* 안내

## Python 버전

표준 라이브러리만 사용 (argparse·json·re·os·sys·importlib). Python 3.6 이상에서 동작.
