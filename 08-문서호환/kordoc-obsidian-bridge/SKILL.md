---
name: kordoc-obsidian-bridge
description: 옵시디언 노트와 한글(HWP/HWPX)·PDF 문서를 kordoc으로 왕복시킨다. "hwp를 옵시디언 노트로", "이 공문 노트로 저장", "노트를 hwpx 공문으로", "옵시디언 노트로 보고서 만들어줘" 요청 시 사용. 일반 파싱·생성 자체는 kordoc MCP 도구를 직접 쓰고, 이 스킬은 노트 규약(경로·frontmatter·첨부)만 정한다.
---

# kordoc ↔ Obsidian 브리지

kordoc MCP(17도구)가 실제 변환을 한다. 이 스킬은 결과를 어디에 어떤 모양으로 두는지만 정한다.

## A. 문서 → 노트
1. `parse_document`(스캔 PDF면 `ocr: true`)로 마크다운 획득. 긴 자료(주석·논문)는 `parse_chunks`.
2. 노트 위치: `~/obsidian/AI 관련자료/<주제>/` 또는 사용자가 지정한 볼트 폴더. 파일명은 한글 문서명 그대로.
3. frontmatter:
   ```yaml
   type: source
   title: <문서 제목>
   source_file: <원본 절대경로>
   format: hwp|hwpx|pdf|...
   parsed_with: kordoc@<버전>
   created: <오늘>
   tags: [<기관>, <문서종류>]
   ```
4. 그림은 kordoc이 만든 `images/<문서명>/`를 노트 옆 폴더로 옮기고 `![[...]]`로 연결.
5. 공문이면 본문 위에 `## 요점`(발신·수신·마감일·제출물) 3~5줄을 덧붙인다. 원문은 고치지 않는다.

## B. 노트 → HWPX
1. 노트의 frontmatter를 떼고 본문만 넘긴다. `[[위키링크]]`는 링크 글자만 남긴다.
2. `lint`(CLI `npx -y kordoc@^4 lint -`) → 표기 위반 고친 뒤 `generate_document`(프리셋: 보고서 기본, 공문은 기안문).
3. `render_document`로 1쪽을 보고 확인, `validate` 통과 후 노트 옆에 `<노트명>.hwpx`로 저장하고 노트에 `![[<노트명>.hwpx]]` 링크 추가.

## 지킬 것
- 원본 파일은 덮어쓰지 않는다(`-o` 새 파일).
- 개인정보가 있으면 노트에 넣기 전 `redact_document` 여부를 사용자에게 묻는다.
- 한글 경로 글롭은 python3으로 처리(맥 NFD).
