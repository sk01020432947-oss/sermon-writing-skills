---
name: web-motion-stack
description: 웹 기술 7층(CSS·JS·GSAP·SVG·Canvas·Three.js·WebGL/WebGPU)으로 "코드로 만드는 영상"을 짓는 스킬. 장면마다 어느 층을 쓸지 고르고(결정표), 한 줄 주제·기획서·대본을 요청문으로 바꾸고, 말로 부분 수정 → 눈으로 검수·자기검토 루프 → 4K 60fps MP4(또는 라이브 HTML) 출력까지 진행한다. 결정론 렌더가 되는 샘플 20개(기술 8 · 영상 연출 문법 10 · 사역 응용 2: 셰이더 배경, 6만 파티클 은하, 3D 카메라 돌리인, 캔버스 물리 입자, SVG 선 그리기·모핑, 챕터 카드, 코드↔결과, 픽셀 vs 벡터, 자기검토 루프, 개념 관계도, 3D 성경 여정 지도)를 틀로 쓴다. 출처 - 코드깎는노인 「이제 영상까지 바이브 코딩으로 만듭니다」. 트리거 - "웹 기술로 모션그래픽", "코드로 영상", "셰이더 배경 영상", "캔버스 파티클", "Three.js 카메라 영상", "3D 지도 영상", "개념 관계도 영상", "4K 60fps로 뽑아줘", "어느 기술로 만들지", "코드깎는노인 영상처럼", "웹모션 도감". 효과 카드 고르기는 awesome-ai-motion, 대사·음악 입력 모드는 claude-motion-studio, 박자표·코드vs생성 판단은 opus-motion-playbook, 실사 생성은 media-gen-video.
---

# web-motion-stack

출처: [코드깎는노인 「이제 영상까지 바이브 코딩으로 만듭니다 | 클로드」](https://www.youtube.com/watch?v=p8rphwT9g-A) (9:07, 2026-10-06 분석). 영상 전체가 코드로 만든 모션그래픽이다.

이 스킬은 **어떤 웹 기술 층으로 장면을 짓는가**와 **영상 속 연출 문법**을 맡는다. 겹치는 일은 넘긴다.

| 단계 | 담당 |
|---|---|
| 층 고르기·Canvas/3D/셰이더 장면·4K 선명도·영상 연출 문법 | **이 스킬** |
| 효과 하나 고르기(637 카드), 기본 렌더러 `render.mjs` | `awesome-ai-motion` |
| 대사+초·음악·나레이션 입력 모드, 25개 GSAP 샘플, `render_hq.mjs` | `claude-motion-studio` |
| BPM 박자표, 프로젝트 지침 8섹션, 코드 vs 생성형 판단 | `opus-motion-playbook` |
| 주문서 문장만 | `motion-order-sheet` |

발표자료(설교 덱·영상·쇼츠)로 쓸 때는 CLAUDE.md 규칙 8대로 시작 전에 `awesome-ai-motion` 사용 여부를 한 번 묻는다.

## 웹 기술 7층 결정표

무엇이 **몇 개** 움직이는지로 고른다. 한 장면에 층을 겹쳐도 시간은 GSAP 타임라인 하나.

| 층 | 고를 때 | 렌더 주의 | 샘플 |
|---|---|---|---|
| L1 CSS | 글자·도형 수십 개의 나타나기·이동·크기·회전 | `@keyframes`는 seek 불가 → 같은 속성을 GSAP가 움직인다 | 01 |
| L2 JavaScript | 수식·규칙 배치(점이 꽃이 되는 등) | 상태를 `draw(t)` 순수함수로 | 02 |
| L3 GSAP | 순서·겹침·타이밍 — 모든 층의 시계 | paused 타임라인 + 절대 시각(초) | 03 |
| L4 SVG | 선 그리기, 아이콘, 모핑, 도식 | 모핑은 점 개수 같은 path의 `attr:{d}` 보간(플러그인 불필요) | 04 |
| L5 Canvas 2D | 입자 수백~수천, 튕김·반응 | 백버퍼 ×devicePixelRatio, 물리는 로드 시 미리 계산 | 05 |
| L6 Three.js | 3D 물체·조명·카메라 이동, 지형·경로 | `preserveDrawingBuffer`, `setPixelRatio(DPR)`, 카메라 경로 = t 함수 | 06, 20 |
| L7 WebGL/WebGPU | 빛·왜곡·물결 셰이더, 수만 파티클 | uniform으로 t 전달. **월드 단위 크기엔 DPR을 곱하지 않는다**(4K에서 뭉침) | 07, 08 |

## 작업 순서

1. **입력 정리** — 한 줄 주제 / 기획서(메시지·대상·톤·장면 구성·스타일·길이) / 대본 중 무엇인지. 비면 기본값: 10초, 1920×1080(작업 무대 1280×720), 30fps, 배경 #0b1012 + 강조 #3ee6a8 + 경고 #ff5d4f. 묻지 않는다.
2. **층 고르기** — 위 표로 장면마다 층을 정하고, 가장 가까운 샘플을 작업 폴더로 복사한다. 작업 폴더는 `~/Desktop/cysjavis/모션그래픽/<한글이름>/`. 샘플이 `../../lib/`를 참조하므로 작업 폴더 안에 `lib` 심볼릭 링크를 두거나 경로를 고친다(렌더러는 `lib/` 경로를 자동으로 awesome-ai-motion/lib로 돌린다). Three.js 샘플은 폴더 안 `three.min.js`도 함께 복사.
3. **짓기** — 골격은 `claude-motion-studio/samples/CONTRACT.md`와 같다. 이 스킬 샘플은 `<style>` 맨 앞의 공통 토큰(.bg .tag .panel .chip .code)을 쓴다. Canvas·3D·셰이더는 `tl.to(st,{t:DUR,duration:DUR,ease:'none',onUpdate:draw},0)`로 시간을 받는다. 문구·색·초는 맨 위 CONFIG로 모아 두면 다음 영상은 값만 바꾼다.
4. **빠른 렌더 + 검수**
   ```bash
   cd ~/DEV/awesome-ai-motion && node scripts/render.mjs <작업폴더> --embed
   ffmpeg -loglevel error -y -i <작업폴더>/clip.mp4 -vf "fps=6/<길이>,scale=480:-1,tile=3x2" -frames:v 1 <스크래치>/check.jpg
   ```
   콘택트시트를 직접 Read로 보고 고친다(최대 3회): 움직임 어색 · 글자 작음(1080p 기준 24px 미만)·잘림·겹침 · 너무 빠름 · 빈 화면 · 사라진 요소.
5. **말로 부분 수정** — 사용자가 "2번 장면 해 색만"처럼 말하면 해당 값만 고친다. 미리보기 장치(상·하단 설명, 재생 바)는 최종본에 넣지 않는다(`--embed`).
6. **출력**
   ```bash
   node ~/.claude/skills/claude-motion-studio/scripts/render_hq.mjs <작업폴더> --scale 3 --fps 60   # 3840×2160 60fps, 모션블러 서브프레임 4
   ffprobe -v error -show_entries stream=width,height,r_frame_rate:format=duration -of compact <작업폴더>/clip_hq.mp4
   ```
   Canvas·3D가 있으면 4K 한 프레임을 잘라 확대해 선명도·점 크기를 확인한다. 예배 대기 화면·키오스크는 MP4 대신 `index.html`을 전체화면으로 띄운다(라이브 모드 자동 반복).

## 샘플 20

`samples/<폴더>/index.html`(브라우저로 열면 반복, `?t=3` 정지, `?embed=1` 장면만) · `clip.mp4` · `poster.jpg` · `preview.gif`.

| # | 폴더 | 내용 |
|---|---|---|
| W01–W08 | 01-css-basics … 08-galaxy-particles | 기술 층별 데모(CSS 4동작, 수식 꽃, 타임라인 트랙, SVG 선·모핑, 캔버스 물리, 3D 카메라, 셰이더 4효과, 6만 점 은하) |
| G01–G10 | 09-hyperspace-title … 18-visual-qa | 영상 연출 문법(워프 오프닝, 챕터 카드, 코드↔결과, 픽셀 vs 벡터, IN→OUT, 말로 수정·4K 출력, 자기검토 루프, 굵기 물결+오타 게이지, 제약→직접 만든 글꼴, 눈으로 검수) |
| X01–X02 | 19-concept-constellation, 20-journey-map-3d | 응용(설교 개념 관계도, 성경 지리 3D 여정 — 지형은 예시) |

## 필요한 자료만 읽기

- [guide.md](references/guide.md) — 원리 44개(A 관점 6 · B 제작 흐름 7 · C 장점 6 · D 연출 문법 16 · E 확장 9, 영상 시각 포함), 7층 표, 샘플 표, 프롬프트 레시피 10개(R1 한 줄 주제형 ~ R10 개념 B롤형), 응용 4분야.
- [catalog.json](references/catalog.json) — 위 내용의 정본. 고친 뒤 `python3 ~/.claude/skills/web-motion-stack/scripts/build.py`로 guide.md와 도감을 다시 만든다.

## 도감

정본: `~/Desktop/cysjavis/모션그래픽/웹모션스택_도감/웹모션스택_도감.html` (자료 `samples/`, `lib/` 같은 폴더). 흐름 6단계 · 7층 결정표 · 샘플 갤러리(영상/라이브 HTML/샘플 프롬프트) · 원리 44 · 레시피 10 · 프롬프트 조립대 · 응용 · 스킬 사용법.
아티팩트: https://claude.ai/artifact/2Cw8bQ1sL89juw58caot8n — 재발행은 반드시 이 URL로(`url` 파라미터, `files`에 도감 폴더의 samples·lib 포함).

## 지킬 것

- 시간은 타임라인 하나. `Math.random`·`Date.now`·CSS animation·setTimeout 금지, 난수는 `Motion.rand(seed)`.
- 외부 다운로드 금지가 걸린 작업이면 그림·글자를 코드로 그린다(영상 B3: Claude가 글꼴을 직접 그려 OFL을 붙임). 글꼴은 OFL 또는 로컬 설치본만.
- 한글은 이 맥에 설치된 OFL 글꼴을 이름으로 지정한다: 제목·성경 본문 `Gowun Batang`, 본문·설명 `Noto Sans KR` 또는 `Gowun Dodum`, 나눔 계열(`~/Library/Fonts`). 렌더 전에 `document.fonts.check('16px "Noto Sans KR"')`로 실제 로드를 확인한다. 직접 그린 글꼴(B3)은 라틴 몇 자 장식에만.
- 화면 글자는 이미지가 아니라 텍스트로(오타 방지). 통계는 출처 있는 값만, 없으면 화면에 "예시". 지도·지형이 개략이면 화면에 밝힌다.
- 남의 영상 화면을 복제하지 않는다. 구조·문법만 빌린다.
- 번쩍임 초당 3회 이하.
