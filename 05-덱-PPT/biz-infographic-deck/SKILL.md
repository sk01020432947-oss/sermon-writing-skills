---
name: biz-infographic-deck
description: 원고를 주면 네이비·플럼·레드·앰버 팔레트의 비즈니스 인포그래픽 PPTX를 생성. SMART 스텝 체인, 불스아이 타깃, 허브 다이어그램, 피라미드, 통계 카드, 간트 액션플랜, 2×2 매트릭스, 컬러 테이블, 다크 섹션 디바이더가 특징. 사용자가 "인포그래픽 덱", "마케팅 플랜 PPT", "비즈니스 다이어그램 발표자료", "biz infographic", "/biz-infographic-deck"을 요청할 때 발동. HTML 덱이 아닌 진짜 .pptx 산출.
---

# biz-infographic-deck

원고(텍스트)를 받아 비즈니스 인포그래픽 스타일의 **PPTX**를 생성한다.
레퍼런스: 마케팅 플랜 템플릿 룩 — 흰 배경 + 컬러 다이어그램, 상단 타이틀/서브타이틀/헤어라인, 다크 네이비 섹션 디바이더.

## 디자인 토큰 (build.py에 내장 — 수정 금지)

- 팔레트 순환: 네이비 `#414263` → 플럼 `#9A5A6C` → 레드 `#D04A54` → 앰버 `#E8A33D` (요소 순서대로 자동 적용)
- 잉크 `#2E2E3A`, 그레이 텍스트 `#8B8B94`, 카드 배경 `#F2F2F5`
- 폰트: Pretendard ExtraBold(타이틀/숫자) / SemiBold / Regular — 한/영 모두 커버
- 사진 미지원(이 스타일은 다이어그램 중심). 아이콘은 `icon` 필드에 이모지/글리프/문자 1개.

## 워크플로

1. **원고 파싱** → 콘텐츠 성격에 맞는 레이아웃 매핑(아래 가이드). 챕터 경계마다 `divider`를 넣어 리듬을 만든다.
2. **spec JSON 작성** — 스크래치패드에 저장. `output`은 사용자가 지정하지 않으면 `~/Documents/<제목>-infographic.pptx`.
3. **빌드**: `python ~/.claude/skills/biz-infographic-deck/scripts/build.py spec.json`
4. **검증(가능하면)**: PowerPoint COM으로 PNG 내보내기 → 육안 확인 → 넘침 시 축약 후 재빌드. COM 불가 시 생략.
5. SendUserFile로 pptx 전달 + 파일 링크.

## spec JSON 스키마

공통: 모든 본문 레이아웃은 `"title"`(상단 좌측)과 `"sub"`(회색 서브타이틀, 선택)를 받는다.

```json
{
  "output": "/Users/kbg1023/Documents/plan-infographic.pptx",
  "slides": [
    {"layout": "divider", "title": "MARKET RESEARCH", "sub": "Best Marketing Plan", "icon": "📊"},

    {"layout": "steps", "title": "SMART Goal", "sub": "설명",
     "items": [{"label": "S", "head": "Specific", "body": "설명"}]},

    {"layout": "target", "title": "Target Market",
     "items": [{"icon": "👥", "head": "타깃 1", "body": "설명"}]},

    {"layout": "numlist", "title": "Convince Customers",
     "items": [{"head": "Patience", "body": "설명", "icon": "🤝"}]},

    {"layout": "cards", "title": "전략 4축",
     "items": [{"head": "헤더", "body": "본문"}]},

    {"layout": "hub", "title": "Marketing Research", "center": "4\nSTEPS",
     "items": [{"head": "항목", "body": "설명"}]},

    {"layout": "pyramid", "title": "How To Convince",
     "items": [{"head": "Step 01", "body": "설명", "icon": "💡"}]},

    {"layout": "stats", "title": "Research Results",
     "items": [{"value": "+16%", "head": "Research 1", "pct": 35, "body": "설명"}]},

    {"layout": "gantt", "title": "Action Plan", "col_head": "TASK",
     "months": ["1월", "2월", "3월", "4월", "5월", "6월"],
     "rows": [{"task": "시장 조사", "start": 1, "end": 2}]},

    {"layout": "matrix", "title": "Strategy Matrix",
     "axes": {"top": "개인화 ↑", "bottom": "대중화 ↓"},
     "quads": [{"head": "Customized", "body": "설명"}]},

    {"layout": "table", "title": "Strategy Summary",
     "cols": ["WHERE?", "WHY?", "WHAT?", "WHEN?"],
     "rows": [["시장", "근거", "활동", "시기"]]}
  ]
}
```

## 분량 가드 (넘침 방지 — 반드시 지킬 것)

- steps.items ≤6(SMART면 5), head ≤10자, body ≤120자
- target.items ≤4, body ≤90자. numlist.items ≤5, body ≤110자
- cards.items ≤4, body ≤300자. hub.items 4~6, head ≤14자, body ≤70자
- pyramid.items ≤5, body ≤90자. stats.items ≤4, value는 "+16%"형, pct는 0~100 정수(생략 가능)
- gantt.rows ≤8, months ≤12, task ≤14자. matrix.quads 정확히 4개. table: cols ≤5, rows ≤6, 셀 ≤40자
- 원고가 길면 슬라이드를 쪼갤 것. 한 슬라이드에 욱여넣지 말 것.

## 레이아웃 선택 가이드

- 챕터 전환/표지 → `divider` (다크 네이비, 커버로도 사용: 첫 슬라이드에 배치)
- 단계·프로세스(약어 체인 포함) → `steps` / 위계·단계별 상세 → `pyramid`
- 타깃·고객 정의 → `target` / 원칙·요소 나열 → `numlist` 또는 `cards`
- 중심 개념+구성 요소 → `hub` / 수치 성과 → `stats`
- 일정 계획 → `gantt` / 포지셔닝·전략 사분면 → `matrix` / 요약 비교 → `table`
