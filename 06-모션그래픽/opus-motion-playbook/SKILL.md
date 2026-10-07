---
name: opus-motion-playbook
description: Claude Opus 5.5로 모션그래픽을 만드는 원리 74개 플레이북. 프로젝트 지침 8섹션(고정 규칙/변수 분리·제작 전 검증 관문), 박자 계층(128BPM 8마디=15초, 강박·박·8분·16분·히트), seek(t) 렌더 공학(순수함수·닫힌형 스프링·서브프레임 블러·콘택트 시트), 쇼케이스 연출 문법(한 물체 변신·타이포 위계·과정 진행바·카메라 줌 서사·픽셀 양자화), 코드 vs 생성형(Higgsfield·ElevenLabs·After Effects·Blender) 분업 판단과 실측 비용, 공개 프롬프트 17개를 담았다. 트리거 - "모션그래픽 원리", "오퍼스 모션", "박자에 맞춰", "BPM 계산", "프로젝트 지침으로 영상", "코드로 할까 생성으로 할까", "Higgsfield 붙일까", "키네틱 타이포 지침", "모션 프롬프트 17", "모션 도감". 장면 코드 작성·렌더는 claude-motion-studio, 효과 카드는 awesome-ai-motion, 주문서 문장은 motion-order-sheet, 종이 콜라주는 vox-paper-motion, 실사 생성은 media-gen-video로 넘긴다.
---

# opus-motion-playbook

출처 영상 5편(2026-10-05 분석): V1 GPT PARK「Claude로 15초 모션그래픽 만들기」 · V2 닥또리「Claude랑 ChatGPT만으로 이런 모션그래픽이?」 · V3 성공지식백과「클로드 오퍼스 5.5의 미친 모션그래픽 방법 총정리」 · V4 Dante's Datalab「클로드 Opus 5.5 영상 자동화 실전 × Higgsfield」 · V5 구름모찌「클로드로 만든 영상, 이 정도까지 왔습니다」. 보강: R = V4가 공개한 [opus-video-prompts](references/opus-video-prompts/README.md) 저장소, P = PDoomVideo ANIMATION_GUIDE.

이 스킬은 **무엇을 왜 그렇게 하는가(원리·판단)**를 맡는다. 손을 움직이는 일은 아래 스킬로 넘긴다.

| 단계 | 담당 |
|---|---|
| 원리·지침·박자표·코드/생성 판단·검수 기준 | **이 스킬** |
| 장면 코드 작성·렌더·음악 합성(render_hq.mjs) | `claude-motion-studio` |
| 효과 하나 고르기(637 카드) | `awesome-ai-motion` |
| 주문서 문장 | `motion-order-sheet` |
| AI 스틸 + 코드 조립 종이 콜라주 | `vox-paper-motion` |
| 실사 영상·이미지 생성 | `media-gen-video`, `media-gen-image` |

## 작업 순서

1. **판단(E1·E2)** — 화면이 글자·도형·그래프 위주면 코드만. 사람·실공간·표정·실물이 필요하면 하이브리드. 하이브리드라도 코드 초안을 먼저 만들고 실사 필요 컷과 예상 크레딧을 보고한 뒤 승인받는다.
2. **출처와 변수(A2·A3)** — 공식 URL·문서를 출처로 받는다. 반복 영상이면 [8섹션 지침](references/project-instruction.md)을 고정하고 변수만 받는다. 비면 기본값: 16:9 1920×1080, 30fps, 15초, 128BPM, 색 2+배경 1.
3. **박자표(B1·B2·A5)** — 길이와 마디로 BPM을 역산하고 장면 경계를 강박에 둔다.
   ```bash
   python3 ~/.claude/skills/opus-motion-playbook/scripts/beatgrid.py --duration 15 --bars 8 --scenes 8
   ```
4. **검증 관문(A4)** — 코드 전에 화면 문구 표(문구·출처·창작 여부)와 디자인 제안(색·글꼴·도형·모션 + 근거)을 보여 준다. "진행"이 오면 끝까지 묻지 않는다.
5. **음악 먼저(B3)** — 상업 이용 가능 곡, 없으면 코드 합성. 생성 음악은 박을 분석해 컷에 맞춘다(B6).
6. **제작** — `claude-motion-studio` 샘플 골격으로 짓는다. 규칙: seek(t) 순수함수(C1), hash 난수(C2), 닫힌형 스프링(C3), 금지 목록(D14), 글자는 항상 코드(E3), 얼굴 위 글자 금지(D13).
   컷이 이미 있는 영상이면 `--snap 5.0,9.1`로 컷과 박의 차이를 본다.
7. **검수(C8)** — 강박 시트를 직접 본다. 완료 보고에 ffprobe 결과를 붙인다.
   ```bash
   python3 ~/.claude/skills/opus-motion-playbook/scripts/beatgrid.py --bpm 128 --duration 15 --sheet <clip.mp4>
   ffprobe -v error -show_entries stream=codec_type,width,height,r_frame_rate:format=duration -of compact <clip.mp4>
   ```
8. **기록(G2·G3)** — NOTES.md에 도구·외부 호출·생성 파일·기존 소재 구분·시간·토큰·크레딧을 적는다. 수정은 장면 번호 단위(A10).

## 필요한 자료만 읽기

- [principles.md](references/principles.md) — 원리 74개(작업 흐름 13 · 박자와 소리 8 · 렌더 공학 11 · 시각 문법 25 · 코드+생성형 14 · 윤리와 비용 3). 영상 프레임으로 확인한 원본 장면 62장. 각 항목: 원리 · 프롬프트에 넣을 문장 · 출처 영상 시각 · 응용. 정본은 `principles.json`.
- 원본 장면 62장: `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/<ID>.jpg`. 영상 프레임을 직접 보고 각 원리와 맞는 순간을 골랐다(2026-10-05). 연출을 설명할 때 Read로 열어 보여 준다.
- [project-instruction.md](references/project-instruction.md) — Claude 프로젝트에 붙일 8섹션 지침 + 첫 메시지·수정 메시지 틀.
- [applications.md](references/applications.md) — 사역·교육 응용 13종, 작업 방식 확장 10가지.
- [opus-video-prompts/](references/opus-video-prompts/README.md) — 한국어 프롬프트 17개, 공개 사례 53건, 제작 방식 9가지. 상세 템플릿은 `prompts/15-ui-morph-loop.md`, `16-high-end-product-video.md`(4블록: inputs·direction·structure·build·gotchas·start).

## 하이브리드 실측 (V4, 각 1회 실행이라 참고값)

| 예시 | 코드 단독 | Higgsfield 연결 | 크레딧 | 채택 |
|---|---|---|---|---|
| 출시 영상 | 29분 · 18만 토큰 | 15분 · 6만 토큰 · 실사 4컷 | 240 | 연결 |
| 음악·효과음 | 13분 · 19/20 컷 1ms 이내 | (오디오는 음성 전용) | 0 | 코드/ElevenLabs |
| 3D 작업실 | 32분 · 빛 우수 · 인물 마네킹 | 62분 · 인물 동작 자연 | 54 | 연결 |
| 예고편 60초 | 28분 · 실루엣 | 25분 · 실사 9컷 | 145 | 연결 |
| 회사 소개 | — | 14분 · 이미지→영상 16회 | 970 | 초안용 |

## 도감 쓰는 법

도감은 1단계 목적 고르기(6개 일반 목적 + 응용 표의 사역·교육 목적) → 2단계 그림 갤러리(마우스를 올리면 데모, 누르면 상세·원본 장면·이전/다음) → 3단계 하단 막대의 프롬프트 조립대로 쓴다. 일반 목적 세트는 `scripts/build.py`의 `MAIN_PURPOSES`, 사역·교육 목적은 `references/applications.md` 표에서 만든다.

## 도감 재생성

`principles.json`을 고친 뒤:
```bash
python3 ~/.claude/skills/opus-motion-playbook/scripts/build.py
```
→ `references/principles.md`와 정본 HTML `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감.html`을 다시 만든다. 아티팩트는 기록된 URL로 재발행한다(새 URL 금지): https://claude.ai/artifact/P4zvd5bBFCPi2Un7YgeUHB

## 지킬 것

- 통계 수치는 출처 있는 값만. 없으면 화면에 "예시".
- 남의 로고·인물 사진·원곡은 권리 있는 파일만(G1). 기존 소재를 모델이 만들었다고 소개하지 않는다.
- 프로그램 설치·유료 API 호출 전에는 확인(A13).
- 결과물 정본은 `~/Desktop/cysjavis/모션그래픽/<한글이름>/`.
