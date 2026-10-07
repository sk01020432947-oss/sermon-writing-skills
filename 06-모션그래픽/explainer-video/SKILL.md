---
name: explainer-video
description: "유튜브 정보성 해설 영상(바이브랩스 스타일)을 대본+내레이션에서 완성 mp4까지 자동 제작하는 스킬. 대본을 장면으로 분할하고, 내레이션 오디오(본인 녹음 또는 edge-tts)에 whisper로 자막 타이밍을 맞추고, codex-image로 장면 일러스트(귀여운 3D 로봇 마스코트 스타일)를 동시 5장씩 배치 렌더한 뒤, Remotion으로 Ken Burns·자막·전환을 조립해 1080p mp4와 썸네일·업로드 메타(제목/설명/타임라인/태그)까지 산출한다. '해설 영상 만들어', '유튜브 영상 제작', '대본으로 영상', '내레이션 영상', '정보성 영상', 'AI 소식 영상', '바이브랩스 스타일'을 요청할 때, 그리고 후속 작업(장면 다시 렌더/자막 수정/썸네일 다시/재조립)에도 반드시 이 스킬을 사용."
---

# Explainer Video — 대본·내레이션 → 완성 유튜브 해설 영상

레퍼런스: 바이브랩스 채널의 Fable 5 해설 영상(rkQaJGSbbak, 12분 37초). 사람은 **대본 작성 + 목소리 녹음**만 하고, 장면 분할·이미지 제작·자막·조립·썸네일은 전부 이 파이프라인이 수행한다.

관련 스킬 (규약 원본 — 중복 기술하지 않고 따른다):
- `remotion` — 조립 엔진. audio / images / import-srt-captions / display-captions / transitions / timing / calculate-metadata / transcribe-captions 규칙을 그대로 사용.
- `webtoon-panel-render` — codex-image 호출 방식·동시 5장 규약·0바이트/md5 검증의 원본. 단 **텍스트 정책은 정반대**(아래 참조).

## 사전 점검 (프로젝트당 1회)

```bash
codex login status        # "Logged in using ChatGPT"
node --version && ffmpeg -version | head -1
edge-tts --list-voices | grep ko-KR   # TTS 대안 쓸 때만
```

## 입력

1. **대본 (필수)** — 사용자가 쓴 내레이션 원고(txt/md). 없으면 주제만 받아 초안을 써 주되, 레퍼런스 영상의 문체를 따른다: 구어체 존댓말, 짧은 문장, "그런데 이상한 순간이 찾아옵니다" 식의 스토리텔링 훅, 구체적 숫자 인용.
2. **내레이션 오디오 (권장)** — 사용자가 대본을 직접 녹음한 mp3/wav. 레퍼런스 영상도 본인 목소리다. 없으면 edge-tts로 생성:
   ```bash
   edge-tts --voice ko-KR-InJoonNeural --rate=-5% -f script.txt --write-media narration.mp3 --write-subtitles narration.srt
   ```
   (남성 InJoon / 여성 SunHi. TTS는 티가 나므로 본인 녹음을 권한다.)
   **edge-tts를 쓰면 `--write-subtitles`가 문장 단위 SRT를 함께 만들어 주므로 2단계의 whisper 전사가 통째로 불필요하다.** whisper는 본인 녹음일 때만 쓴다.

## 작업 폴더

```
video-project/{slug}/
  01_script/script.md, scenes.md
  02_audio/narration.mp3, narration.srt
  03_images/scene_001.png ...
  04_remotion/   (Remotion 프로젝트)
  05_output/final.mp4, thumbnail.png, upload-meta.md
```

## 파이프라인

### 1단계 — 장면 분할 (scenes.md)

대본을 **15~25초 분량 단위**로 잘라 장면 표를 만든다. 10분 영상 기준 30~45장면.

```
### scene_001
- narration: "<이 장면에서 읽히는 대본 원문>"
- keyword: "한 줄 부탁이 100페이지로"      # 화면에 크게 띄울 핵심 한글 문구 (없으면 생략)
- visual: "<이미지 컨셉 1~2문장: 구도, 감정, 소품>"
```

분할 원칙: 화제가 바뀌는 곳에서 자르고, 인트로(채널 인사)와 아웃트로(구독 유도)를 별도 장면으로 둔다. 챕터 경계(나중에 타임라인이 됨)를 `## chapter: 제목`으로 표시한다.

### 2단계 — 오디오 확보 + 타이밍

- 오디오 길이 측정: `ffprobe -v error -show_entries format=duration -of csv=p=0 narration.mp3`
- **자막 전사**: remotion 스킬의 `rules/transcribe-captions.md`(whisper.cpp)로 단어 단위 타임스탬프를 뽑아 `narration.srt` 생성. 전사 결과를 대본 원문과 대조해 오탈자를 대본 기준으로 교정한다(자막은 대본이 정답, whisper는 타이밍만 제공).
- 각 장면의 시작/끝 시각을 SRT에서 찾아 scenes.md에 `start:`/`end:`로 기록한다. 이것이 이미지 표시 구간이다.

### 3단계 — 장면 이미지 렌더 (codex-image)

`webtoon-panel-render`의 동시성·검증 규약을 따르되, 정책 차이에 주의:

- **텍스트는 이미지에 넣지 않는다.** 자막·키워드는 4단계에서 Remotion 오버레이로 얹는다(웹툰의 in-image 베이크와 정반대 — 해설 영상은 자막 수정이 잦고 정확도가 생명). 부정 프롬프트: `no text, no letters, no watermark, no subtitles`.
- **16:9, 1920x1080** 명시.
- **스타일 토큰을 모든 프롬프트에 고정 주입** (일관성 장치). 기본 스타일(바이브랩스 룩, 필요시 사용자와 조정):
  ```
  STYLE: cute 3D rendered white robot mascot with glowing blue eyes, soft studio lighting,
  vibrant blue-purple gradient background, glossy toy-like material, friendly tech explainer
  illustration, high detail, 16:9, 1920x1080
  ```
- 프롬프트 = STYLE + scenes.md의 visual + 감정/구도. 5장씩 배치, `run_in_background: true`, 전역 동시 5 초과 금지:
  ```bash
  codex exec --sandbox workspace-write --skip-git-repo-check \
    --cd <프로젝트 절대경로> -o /tmp/codex-scene-001.md \
    "이미지 생성 도구로 '<프롬프트>' 이미지를 생성하고 ./03_images/scene_001.png 로 저장. 파일 경로만 한 줄로 보고."
  ```
- 렌더 후: 0바이트/손상/md5 중복 검사(webtoon-panel-render의 검증 절차 그대로), 텍스트 혼입 위험이 높은 장면(간판·블록·액자 등)을 표본으로 Read 육안 확인. 미달 장면만 재렌더(최대 3회).
- 소요 시간: 40장 ≈ 8웨이브 ≈ 20~25분. 사용자에게 미리 알린다.
- **Windows 실전 규약(2026-07 실측)**: ① codex 샌드박스가 작업 폴더 복사를 차단할 수 있다 — codex에게 "생성된 원본 PNG의 절대 경로를 마지막 줄에 보고"시키고, 파이썬이 `-o` 로그에서 `generated_images` 경로를 정규식으로 뽑아 직접 복사한다(파일명이 `_image_id_.png` 플레이스홀더일 수 있으니 그 폴더의 *.png를 glob). 이 "로그 샐비지"를 렌더 스크립트의 스킵 판정에 넣으면 실패 배치도 codex 재호출 없이 회수된다. ② 백그라운드 Bash는 10분 제한 — 한 실행당 10장(2웨이브)으로 잘라 완료 통지마다 재실행한다. ③ subprocess는 `shutil.which('codex')`(npm .cmd 심)와 `encoding='utf-8'` 필수(cp949 크래시).

### 4단계 — Remotion 조립

`04_remotion/`에 프로젝트 생성(`npx create-video@latest --blank` 또는 기존 템플릿 재사용). **remotion 스킬의 규칙 파일을 반드시 읽고 따른다.** 구성:

1. **Audio** — narration.mp3 전체를 깔고, `calculate-metadata`로 composition 길이를 오디오 길이에 맞춘다.
2. **장면 시퀀스** — scenes.md의 start/end로 `<Sequence>` 배치. 각 이미지는 느린 Ken Burns(1.0→1.08 스케일 + 약간의 팬)로 정적 이미지의 지루함을 죽인다. 장면 전환은 0.5초 크로스페이드(`transitions.md`).
3. **자막** — `import-srt-captions.md`로 narration.srt 로드, 하단 중앙에 큰 한글 자막(Pretendard/Noto Sans KR Bold, 흰 글자 + 검정 외곽선). `display-captions.md`의 페이지 방식 사용.
4. **키워드 카드** — scenes.md에 keyword가 있는 장면은 등장 시 화면 중앙~상단에 큰 타이포(노랑/빨강 강조, `text-animations.md`의 word-highlight 패턴)를 1~2초 애니메이션으로 띄운다. 레퍼런스 영상의 "큰 한글 문구" 룩이 이것이다.
5. **BGM(선택)** — 사용자가 파일을 주면 내레이션 대비 -18dB로 깔고 인트로/아웃트로에서만 살짝 키운다. 임의로 구해오지 않는다(저작권).
6. 렌더: `npx remotion render <CompId> ../05_output/final.mp4` (1080p, 30fps).

### 5단계 — 썸네일 + 업로드 메타

- **썸네일(권장)**: Remotion에 1280x720 `Thumbnail` 컴포지션을 하나 더 만들어 대표 장면 이미지 + 큰 한글 타이포를 얹고 `npx remotion still Thumbnail thumbnail.png`로 뽑는다 — 한글이 100% 정확하고 재렌더가 공짜다(2026-07 실전 검증). codex 한글 베이크는 대안일 뿐: 쓴다면 1280x720, 깨지면 재렌더 최대 3회 후 텍스트 없는 배경만 뽑아 사용자에게 알린다.
- **upload-meta.md**: 제목(레퍼런스 문법: "~하지 마세요. ~하세요" 식 금지+대안 훅), 설명란(요약 2~3문단 + "이 영상에서 다루는 내용" 불릿 + `00:00` 타임라인 — scenes.md의 chapter 경계에서 자동 생성), 태그 10~15개.

## 검증 (렌더 후 필수)

- final.mp4를 ffprobe로 길이·해상도 확인, 시작/중간/끝 3프레임을 추출(`ffmpeg -ss <t> -i final.mp4 -frames:v 1 f.png`)해 Read로 열어 자막 싱크·이미지 표시를 육안 확인.
- 자막과 내레이션이 2초 이상 어긋나면 SRT 타이밍을 재점검하고 재렌더.
- 완료 보고는 "렌더 성공" 한 줄이 아니라 파일 경로 + 길이 + 확인한 프레임 근거로 한다.

## 안티패턴

- **장면 이미지에 자막/대사 베이크** — 웹툰 규약을 그대로 가져오는 실수. 해설 영상 자막은 항상 Remotion 오버레이.
- **whisper 전사를 자막 원문으로 그대로 사용** — 오탈자가 그대로 실린다. 텍스트는 대본, 타이밍만 whisper.
- **동시 6장+ codex 렌더 / sleep 폴링 / 동일 출력 경로** — webtoon-panel-render 안티패턴 그대로 적용.
- **스타일 토큰 없이 장면별 자유 프롬프트** — 장면마다 그림체가 널뛴다. STYLE 블록을 전 장면에 주입.
- **10분 영상에 이미지 10장** — 장면당 1분은 정적이라 이탈한다. 15~25초당 1장.
- **BGM 임의 다운로드** — 저작권. 사용자 제공 파일만.

## 후속 작업

- "장면 N만 다시" → 해당 프롬프트 보강 후 그 장면만 재렌더 → Remotion 재렌더(이미지 교체는 재조립 불필요, 렌더만).
- "자막 수정" → SRT 편집 → 렌더만 재실행.
- 다음 회차 → 같은 STYLE 블록·Remotion 프로젝트 재사용, scenes/이미지/오디오만 교체.
