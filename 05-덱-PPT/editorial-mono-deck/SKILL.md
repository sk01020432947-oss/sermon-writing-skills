---
name: editorial-mono-deck
description: 원고를 주면 흑백 편집 매거진(에디토리얼) 스타일 PPTX를 생성. 웜 오프화이트 종이+잉크 블랙, 초대형 헤비 대문자 타이틀, 그레이스케일 사진, 넘버 서클·헤어라인 룰·메타 행이 특징. 사용자가 "에디토리얼 덱", "흑백 매거진 PPT", "잡지 스타일 발표자료", "editorial mono", "/editorial-mono-deck"을 요청할 때 발동. HTML 덱이 아닌 진짜 .pptx 산출.
---

# editorial-mono-deck

원고(텍스트)를 받아 흑백 편집 매거진 스타일의 **PPTX**를 생성한다.
레퍼런스: 볼드 그로테스크 대문자 타이포 + 흑백 사진 + 크림 종이 배경의 resume/portfolio 프레젠테이션 룩.

## 디자인 토큰 (build.py에 내장 — 수정 금지)

- 종이 `#F1EFE9` / 잉크 `#141414` / 그레이 `#6E6C66`, 다크 슬라이드는 반전
- 디스플레이: Pretendard Black(한/영 모두), 자간 -100~-150, 행간 0.88
- 본문: Pretendard Regular 9~11.5pt, 라벨: Medium + 자간 +150 대문자
- 영문은 자동 대문자화됨(한글 무관). 사진은 자동 그레이스케일 + 중앙 크롭, 없으면 회색 플레이스홀더

## 워크플로

1. **원고 파싱** → 섹션을 아래 레이아웃에 매핑. 슬라이드 순서 권장: cover → toc → section(dark) → 본문(columns/feature/listphoto/table/strip 혼합) → closing. 다크 슬라이드를 3~4장에 1장꼴로 섞어 리듬을 만든다.
2. **spec JSON 작성** — 스크래치패드에 `spec.json` 저장. 출력 경로(`output`)는 사용자가 지정하지 않으면 `~/Documents/<제목>-editorial.pptx`.
3. **빌드**: `python ~/.claude/skills/editorial-mono-deck/scripts/build.py spec.json`
4. **검증(가능하면)**: PowerPoint COM으로 슬라이드 PNG 내보내기 후 육안 확인, 넘침·겹침 발견 시 텍스트 축약 후 재빌드. COM 불가 시 생략.
5. SendUserFile로 pptx 전달 + 파일 링크.

## 사진

- 사용자가 이미지 경로를 주면 그대로 `image` 필드에 (자동 흑백 변환).
- 없으면 `image` 생략(플레이스홀더 박스). 사용자가 원하면 media-gen-image로 흑백 인물/오브제 사진을 생성해 넣을 수 있다고 제안만 하고, 기본은 플레이스홀더.

## spec JSON 스키마

```json
{
  "output": "/Users/kbg1023/Documents/my-deck-editorial.pptx",
  "slides": [
    {"layout": "cover", "title": "RE-\nSUME", "kicker": "PRESENTATION", "sub": "한 문단 소개(선택)",
     "credit": "CREATED BY ...", "image": "path(선택)",
     "meta": [["CLIENT", "값"], ["PROJECT", "값"], ["DATE", "값"]]},

    {"layout": "toc", "title": "CONTENTS", "items": ["Experience", "Education", "Skills"], "image": "path"},

    {"layout": "section", "dark": true, "title": "ABOUT ME", "number": "3",
     "body": "소개 문단", "image": "path", "meta": [["NAME", "값"]]},

    {"layout": "columns", "title": "EXPERIENCE", "note": "우상단 박스 코멘트(선택)",
     "image": "path", "summary": "좌하단 요약(선택)",
     "items": [{"label": "1", "head": "2020-2021", "sub": "JANUARY-FEBRUARY", "body": "설명"}]},

    {"layout": "feature", "badge": "A", "head": "COMPANY NAME", "period": "2022-2023",
     "sub": "Job / Position Title", "cols": ["칼럼1 텍스트", "칼럼2 텍스트"],
     "title": "JOB POSITION", "image": "path", "dark": false, "intro": "상단 소개(선택)"},

    {"layout": "listphoto", "title": "EDUCATION", "intro": "소개(선택)", "image": "path",
     "items": [{"label": "1", "head": "기관명", "body": "설명"}]},

    {"layout": "table", "title": "TECHNICAL SKILLS", "intro": "소개(선택)", "image": "path",
     "rows": [["Python", "90%"], ["Figma", "75%"]], "footnote": "각주(선택)"},

    {"layout": "strip", "title": "VOLUNTEER WORK", "intro": "소개(선택)",
     "cells": [{"head": "제목", "image": "path", "body": "설명(선택)"}]},

    {"layout": "closing", "title": "GET IN TOUCH", "badge": "E", "image": "path",
     "body": "마무리 문단(선택)", "meta": [["EMAIL", "값"], ["PHONE", "값"]]}
  ]
}
```

## 분량 가드 (넘침 방지 — 반드시 지킬 것)

- cover.title: 줄당 ≤7자(영문 기준), 최대 2줄. 긴 단어는 `RE-\nSUME`처럼 하이픈 분절. 한글이면 `title_size`를 80~96으로 낮춘다.
- section/listphoto/table/closing.title: ≤12자. table.title은 "두 단어"(첫 공백에서 좌/우 분리 배치됨).
- columns.items ≤4개, body 각 ≤160자. feature.cols ≤3개, 각 ≤280자. listphoto.items ≤4개, body ≤120자.
- table.rows ≤6행, strip.cells ≤4개, meta ≤5쌍, toc.items ≤6개.
- 원고가 길면 슬라이드를 늘려라(feature 여러 장). 한 슬라이드에 욱여넣지 말 것.

## 레이아웃 선택 가이드

- 시기별/단계별 나열 → `columns` (넘버 서클 타임라인)
- 프로젝트·경력·기관 하나를 깊게 → `feature` (배지 + 초대형 하단 타이틀, 다크 변형 가능)
- 항목 리스트 + 사진 1장 → `listphoto`
- 수치·비율·스펙 → `table`
- 사진 여러 장 나열 → `strip`
- 챕터 전환 → `section` (기본 dark)
