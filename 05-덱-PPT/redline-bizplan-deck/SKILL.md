---
name: redline-bizplan-deck
description: 원고를 주면 화이트+레드 액센트+다크 네이비의 비즈니스 플랜 PPTX를 생성. 투톤 타이틀(검정+빨강), 레드 사선 블록, 컬러 사진, 아이콘 서클, 문제/솔루션 넘버링, 팀 그리드, 스킬바, 콘택트 슬라이드가 특징. 사용자가 "비즈니스 플랜 PPT", "사업계획서 발표자료", "레드 비즈니스 덱", "redline bizplan", "/redline-bizplan-deck"을 요청할 때 발동. HTML 덱이 아닌 진짜 .pptx 산출.
---

# redline-bizplan-deck

원고(텍스트)를 받아 레드/네이비 비즈니스 플랜 스타일의 **PPTX**를 생성한다.
레퍼런스: Business Plan 템플릿 룩 — 흰 배경, 레드 `#D93333` 액센트 사선(패럴렐로그램), 다크 네이비 `#2F3244` 패널, 투톤 타이틀.

## 디자인 토큰 (build.py에 내장 — 수정 금지)

- 레드 `#D93333` / 네이비 `#2F3244` / 잉크 `#1A1A1A` / 그레이 `#7A7A80` / 카드 `#F5F5F6`
- 폰트: Pretendard ExtraBold(타이틀) / SemiBold / Regular
- **투톤 타이틀**: `title` 문자열에서 `|` 뒤가 레드로 렌더링됨. 예: `"Team |Leader"` → "Team"(검정)+"Leader"(빨강). `\n` 줄바꿈 지원.
- 사진: 컬러 유지 + 중앙 크롭(흑백 변환 안 함). 없으면 회색 플레이스홀더. 아이콘은 `icon` 필드에 이모지 1개.

## 워크플로

1. **원고 파싱** → 비즈니스 플랜 서사 순서로 매핑: cover → welcome → toc → about → split(미션/비전) → darkcards(핵심 사업) → problems → numphoto(솔루션) → progress → skillbars/team → services → contact.
2. **spec JSON 작성** — 스크래치패드에 저장. `output` 기본값 `~/Documents/<제목>-bizplan.pptx`.
3. **빌드**: `python ~/.claude/skills/redline-bizplan-deck/scripts/build.py spec.json`
4. **검증(가능하면)**: PowerPoint COM으로 PNG 내보내기 → 육안 확인 → 수정 후 재빌드.
5. SendUserFile로 전달 + 파일 링크.

## spec JSON 스키마

공통: 본문 레이아웃은 `"title"`(투톤, `|` 사용)과 `"sub"`(선택)를 받는다. `"image"`는 모두 선택.

```json
{
  "output": "/Users/kbg1023/Documents/plan-bizplan.pptx",
  "slides": [
    {"layout": "cover", "logo_text": "Company Name", "title": "BUSINESS\n|PLAN", "year": "2025",
     "tagline": "Creative idea", "body": "소개 문단", "meta": "123 Street, City", "image": "path"},

    {"layout": "welcome", "title": "WELCOME TO OUR |BUSINESS PLAN", "name": "김OO", "role": "대표",
     "message_head": "Welcome Message", "icon": "💬", "body": "인사말", "image": "path"},

    {"layout": "toc", "title": "TABLE OF |CONTENT", "body": "소개(선택)",
     "items": ["Cover", "Welcome", "About Company"], "image": "path"},

    {"layout": "about", "title": "ABOUT |COMPANY", "body": "회사 소개",
     "items": [{"icon": "🚀", "head": "Title Here", "body": "설명"}], "image": "path"},

    {"layout": "split", "title": "OUR |MISSION & VISION", "badge": "2025",
     "cols": ["미션 문단", "비전 문단"], "footer": "하단 강조(선택)", "image": "path"},

    {"layout": "darkcards", "title": "WHAT |WE DO", "sub": "설명",
     "items": [{"icon": "📈", "head": "Title", "body": "설명"}]},

    {"layout": "problems", "title": "OUR |PROBLEMS", "body": "좌측 설명", "panel_head": "What's the Problem",
     "items": [{"head": "Problem Name", "body": "설명"}], "image": "path"},

    {"layout": "numphoto", "title": "OUR |SOLUTION", "body": "우측 상단 설명",
     "items": [{"head": "Solution Name", "body": "설명"}], "image": "path"},

    {"layout": "progress", "title": "COMPANY |PROGRESS", "body": "설명",
     "items": [{"head": "Progress\nTitle", "body": "설명"}]},

    {"layout": "skillbars", "title": "Team |Leader", "name": "김OO", "role": "직함", "body": "소개",
     "bars": [{"head": "Your Title Here", "pct": 80}], "image": "path"},

    {"layout": "team", "title": "OUR |TEAM", "body": "팀 소개(선택, 있으면 그리드가 우측으로)",
     "items": [{"name": "이름", "role": "직함", "image": "path"}]},

    {"layout": "services", "title": "COMPANY |SERVICE", "body": "설명",
     "items": [{"icon": "🛠", "head": "Service Name", "body": "설명"}], "image": "path"},

    {"layout": "contact", "title": "CONTACT |ME", "body": "마무리 문단",
     "items": [{"icon": "🏠", "head": "Address", "body": "주소"}, {"icon": "📞", "head": "Phone", "body": "번호"}]}
  ]
}
```

## 분량 가드 (넘침 방지 — 반드시 지킬 것)

- cover.title 줄당 ≤10자, 최대 2줄. 투톤 `|`는 슬라이드당 타이틀에 1회만.
- about.items 정확히 3개, body 각 ≤150자. split.cols 정확히 2개, 각 ≤400자
- darkcards.items ≤3, body ≤160자. problems/numphoto.items ≤3, body ≤100자
- progress.items ≤3, head는 `\n`으로 2줄 분절(원 안에 들어감, 줄당 ≤8자), body ≤180자
- skillbars.bars ≤4, head ≤18자. team.items ≤6(이름/직함 ≤14자). services.items ≤4, body ≤70자
- toc.items ≤8, contact.items ≤3
- 원고가 길면 슬라이드를 쪼갤 것(darkcards·numphoto 여러 장 허용).

## 레이아웃 선택 가이드

- 표지 → `cover` / 대표 인사 → `welcome` / 목차 → `toc`
- 회사 개요 → `about` / 미션·비전 등 2단 대비 → `split`
- 핵심 사업·가치(다크 임팩트) → `darkcards` / 문제 정의 → `problems` / 해결책 → `numphoto`
- 연혁·마일스톤 → `progress` / 핵심 인물 → `skillbars` / 팀 전체 → `team`
- 서비스·제품 → `services` / 마무리 → `contact`
