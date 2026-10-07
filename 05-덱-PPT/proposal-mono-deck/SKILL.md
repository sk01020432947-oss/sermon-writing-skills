---
name: proposal-mono-deck
description: 원고를 주면 흑백 프로젝트 프로포절(제안서) 스타일 PPTX를 생성. 슬라이드 전체를 감싸는 얇은 검정 프레임, 매 슬라이드 상단 메타 행(Project/Date/Company), 마침표로 끝나는 볼드 타이틀, 고스트 넘버(01~), 회색 틴트 블록, 흑백 사진, 타임라인이 특징. 사용자가 "프로포절 덱", "제안서 PPT", "흑백 제안서", "proposal mono", "/proposal-mono-deck"을 요청할 때 발동. HTML 덱이 아닌 진짜 .pptx 산출.
---

# proposal-mono-deck

원고(텍스트)를 받아 흑백 프로젝트 프로포절 스타일의 **PPTX**를 생성한다.
레퍼런스: Project Proposal 템플릿 룩 — 흰 종이 + 1pt 검정 프레임, 문서형 메타 헤더, 미니멀 타이포.

## 디자인 토큰 (build.py에 내장 — 수정 금지)

- 화이트 배경 + 잉크 `#111111`, 고스트 넘버 `#DCDCDC`, 틴트 블록 `#E9E9E9`, 커버는 다크 `#141414`
- 모든 슬라이드: 외곽 1pt 프레임 + 상단 메타 행(deck 레벨 `project`/`date`/`company`가 자동 표기) + 헤어라인
- 타이틀: Pretendard Black, 자동 대문자화(한글 무관). **타이틀은 마침표로 끝내는 것이 이 스타일의 시그니처** (`"ABOUT\nUS."`)
- 사진 자동 그레이스케일 + 중앙 크롭, 없으면 회색 플레이스홀더. 회색 틴트 사각형이 사진 모서리에 겹치는 연출 내장

## 워크플로

1. **원고 파싱** → 제안서 서사 순서로 매핑: cover → index → section(About) → team → detail/framed/feature(프로젝트 소개·컨셉) → stages → timeline → closing. 고스트 넘버는 "01"부터 섹션 순서대로 붙인다.
2. **spec JSON 작성** — 스크래치패드에 저장. `output` 기본값 `~/Documents/<제목>-proposal.pptx`.
3. **빌드**: `python ~/.claude/skills/proposal-mono-deck/scripts/build.py spec.json`
4. **검증(가능하면)**: PowerPoint COM으로 PNG 내보내기 → 육안 확인 → 수정 후 재빌드.
5. SendUserFile로 전달 + 파일 링크.

## spec JSON 스키마

최상위에 `project`, `date`(예: "01.12.25"), `company` — 모든 슬라이드 헤더에 자동 표기.

```json
{
  "output": "/Users/kbg1023/Documents/plan-proposal.pptx",
  "project": "프로젝트명", "date": "01.12.25", "company": "회사명",
  "slides": [
    {"layout": "cover", "title": "PROJECT\nPROPOSAL.", "body": "소개 문단(회색 밴드 안)",
     "credit": "Created By 김OO\nCEO And Founder", "image": "path"},

    {"layout": "index", "title": "INDEX\nCONTENT", "sub": "Subtitle Here", "body": "설명",
     "items": ["Introduction", "Core Values", "Contact"]},

    {"layout": "section", "title": "ABOUT\nUS.", "number": "01", "body": "본문",
     "sub": "Subtitle Here", "footnote": "작은 각주(선택)", "caption": "사진 밑 캡션(선택)", "image": "path"},

    {"layout": "team", "title": "OUR\nTEAM", "number": "02", "sub": "Subtitle", "body": "팀 소개",
     "items": [{"name": "Subtitle Here", "body": "설명", "image": "path"}]},

    {"layout": "detail", "title": "PROJECT\nNAME.", "number": "03", "sub": "Your Text\nHere",
     "body": "우상단 본문", "body2": "우하단 본문(선택)", "image": "path"},

    {"layout": "framed", "title": "PROJECT\nCONCEPT.", "number": "04", "sub": "Your Text\nHere",
     "body": "본문", "caption": "액자 사진 세로 캡션", "image": "path"},

    {"layout": "stages", "title": "PROJECT\nSTAGES.", "body": "칼럼1", "body2": "칼럼2(선택)",
     "items": [{"head": "Stages 01", "body": "설명", "image": "path"}]},

    {"layout": "feature", "photo_side": "left", "title": "PROGRESS.", "number": "05",
     "sub": "Your Text\nHere", "body": "본문", "note": "박스 인용(선택)", "image": "path"},

    {"layout": "timeline", "title": "PROJECT TIMELINE",
     "items": [{"head": "2022", "sub": "Subtitle Here", "body": "설명"}]},

    {"layout": "closing", "title": "THANK YOU FOR\nVIEWING.", "body": "마무리(선택)",
     "meta": [["Address", "주소"], ["P :", "+00 123 456 7890"], ["E :", "user@example.com"]], "image": "path"}
  ]
}
```

## 분량 가드 (넘침 방지 — 반드시 지킬 것)

- 타이틀 줄당 ≤10자(영문), 최대 2줄, 마침표로 끝맺기. 한글 타이틀은 줄당 ≤7자
- cover.body ≤200자, credit 2줄. index.items ≤8, 각 ≤20자
- section/detail/framed.body ≤300자. stages.items ≤3, body 각 ≤180자
- team.items ≤3, body 각 ≤150자. timeline.items 4~6, body 각 ≤80자
- closing.meta ≤5쌍. feature.note ≤90자
- 원고가 길면 section/detail/framed를 여러 장으로 쪼갤 것.

## 레이아웃 선택 가이드

- 표지 → `cover`(다크) / 목차 → `index` / 회사·팀 소개 챕터 → `section`, `team`
- 프로젝트 개요 → `detail` / 컨셉·작품(액자 연출) → `framed` / 단계 → `stages`
- 진행상황·중간보고(사진 크게) → `feature` (photo_side로 좌우 선택, note로 인용 박스)
- 일정 → `timeline` / 마무리·연락처 → `closing`
