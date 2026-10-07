---
name: vox-paper-motion
description: Vox식 종이 콜라주 모션그래픽(찢어진 종이·4색 팔레트·주인공 강조·신문 조각·2.5D 패럴랙스·점선 항로·지도 기울이기·망점 마감)을 "이미지는 AI로 몇 장, 영상은 코드로 조립"하는 방식으로 만든다. 원리 60여 개(영상 출처+확장)와 도감 28클립, 장면 합성기(vox_compose: seed·chaos 결정론), 프로젝트 실행기(vox_sequence: 로컬 TTS 내레이션+받아쓰기 검증·전환 4종·가로/세로·자막·썸네일·검수 시트)를 담았다. 트리거 - "Vox 스타일", "복스 스타일", "종이 콜라주 영상", "페이퍼 컷아웃", "다큐 인트로", "역사 인트로", "성경 배경 인트로", "선교 여정 지도 영상", "디오라마 영상", "신문 콜라주 모션", "seed chaos", "사진 몇 장으로 모션". 글자·도형 위주 모션(HTML+GSAP)은 claude-motion-studio, 효과 카드 고르기는 awesome-ai-motion, 주문서 문장은 motion-order-sheet, 박자표·코드vs생성 판단은 opus-motion-playbook, 실사 생성 영상은 media-gen-video.
---

# vox-paper-motion v2

출처: 원카AI 「프롬프트 한 줄로 고퀄 Vox 스타일 모션 그래픽 만드는 법 (클로드 오퍼스 5.5, 힉스필드)」 (youtu.be/a3HPd9wsROU) — 자막·고정댓글·화면 속 제작 지침을 프레임 단위로 읽어 정리.
설명서·도감: `~/Desktop/cysjavis/매뉴얼/영상_이미지도구/Vox종이모션_매뉴얼.html`

핵심: 영상 모델(Seedance 등)로 통째 생성하지 않는다. **소재 이미지 몇 장만 만들고 움직임은 코드로 조립**한다. 고칠 때 이미지만 다시 뽑으면 되고 타이밍·자막·위치 수정은 비용 0.

## 읽을 자료 (필요한 것만)
- 원리 목록과 키 대응: [references/principles.md](references/principles.md) — 도감 번호(A1…H4)와 같다
- 프롬프트 체계(목적 한 줄 + 고정 제작법, 소재·음악 프롬프트): [references/prompt-system.md](references/prompt-system.md)
- 시작 템플릿: [templates/project.json](templates/project.json), [templates/README.md](templates/README.md)

## 작업 순서
1. **목적 한 줄 → 비트표.** 장면 3~5개, 장면마다 주인공 하나, 내레이션 한 문장. 묻지 않고 기본값으로(16:9+9:16, 30fps, hold 2, seed 새로, chaos 0.45).
2. **계획·견적 먼저 보여 주기.** 소재 장수, 생성 수단(로컬 Qwen 장당 약 2~4분 / Higgsfield 장당 1.5크레딧), 예상 길이.
3. **소재 생성.** 배경은 장면당 1장 고정. 주인공·물건은 흰 배경 + 채도 있는 색(흰·크림 옷 금지). 세로판 배경은 세로로 따로. 프롬프트는 prompt-system.md 4절.
4. **내레이션 먼저.** `vox_sequence.py project.json --voice` → 받아쓰기 일치 0.9 미만이면 seed 바꿔 자동 재생성. 문장 길이가 장면 길이를 정한다.
5. **한 장 먼저.** `vox_compose.py 장면.json --still 2 a.png`로 스타일 확인 → 전체.
6. **전체 렌더.** `vox_sequence.py project.json` → `<out>_16x9.mp4`, `<out>_9x16.mp4`, `.srt`, `_썸네일.png`, `검수/시트_*.jpg`, `보고서.md`.
7. **검수.** 시트를 Read로 본다: 글자 잘림·겹침, 주인공 배경 잔여, 강조색이 두 곳인지, 세로판 아래 20% 비었는지, 사실 표기(연도 "경", 경로 "예시", 장절 대조). 고칠 장면만 `--only N`.

## 도구
```bash
S=~/.claude/skills/vox-paper-motion/scripts
python3 $S/vox_compose.py scene.json                 # 장면 하나 렌더
python3 $S/vox_compose.py scene.json --still 2.5 a.png
python3 $S/vox_compose.py scene.json --sheet 8 s.jpg
python3 $S/vox_compose.py --demo <폴더>              # 자체 점검(결정론 포함)
python3 $S/vox_sequence.py project.json [--voice | --only N]
```

## 장면 JSON 요약 (자세히는 vox_compose.py 머리말)
- 최상위: `size fps duration hold bg seed chaos palette{ink,paper,grey,accent} newsprint{count,opacity} focus{depth,strength} finish{grain,vignette,halftone,xerox,chroma} pixelate{block,colors} camera[{t,zoom,x,y,tilt,ease}] audio layers`
- 레이어 소재: `src | frames(+fps,register) | text(+serif,size,color,box,type_jitter) | rect | route{points,dur,arc,dash,width,color}`
- 레이어 처리: `key tol torn rough shadow bw accent(duotone|backing|recolor) recolor_box auto_back blur boil chaos(false로 끄기)`
- 레이어 배치·시간: `fit:"cover" width x y scale rot depth start end enter{type,dur,ease,dist} exit bob drift path{points,dur,arc,rotate,rotate_max}`
- 색 이름 `ink paper grey accent`를 color·box·bg에 그대로 쓸 수 있다.

## 프로젝트 JSON 요약 (vox_sequence)
`formats` `style`(모든 장면 공통) · `voice{engine:omnivoice|none, instruct, language, speed, seed, verify}` · `captions{"9:16":true}` · `transition{type: wipe|whip|leak|fade|cut, dur}` · `music{src, volume, offset}` · `scenes[{say, caption, lead, tail, duration, transition, style(덮어쓰기), camera(t:"end"), layers, layers_v}]`(레이어 `at` = 내레이션 시작 기준 초) · `thumbnail{size,bg,layers}`

## 도구 상태 (2026-10-06 점검)
- 내레이션: VoiceStudio(OmniVoice) `127.0.0.1:3900` — 앱을 켜야 한다(`open -a VoiceStudio`). Voicebox는 서버가 뜨지 않아(10-04 충돌) 대체.
- 받아쓰기 검증: `whisper-cli` + `~/Desktop/cysjavis/KBG-Bible-Labs-Sermon/data/models/ggml-large-v3-turbo-q8_0.bin` (환경변수 `WHISPER_GGML`로 바꿀 수 있음)
- 이미지: `qwen-local-image`(무료). Higgsfield MCP는 미연결(선택) — higgsfield.ai › MCP › Claude › Connect, 계정 연결은 사용자가.

## 금지
- 실존 인물 초상을 사실처럼 만들지 않는다(역사 인물은 판화·일러스트 양식, 필요하면 "재구성" 표기).
- 연도·수치·경로는 출처 있는 값만. 불확실하면 "경"·"예시".
- 원본 영상·채널의 그림·프롬프트 원문을 복제하지 않는다. 양식과 원리만 쓴다.
- 강조색을 두 곳에 쓰지 않는다(주인공이 둘이 됨).

결과물 위치: `~/Desktop/cysjavis/<주제폴더>/<한글이름>/` (project.json · 소재 · mp4 함께).
