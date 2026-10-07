# 샘플 제작 계약 (모든 샘플 공통)

경로: `~/.claude/skills/claude-motion-studio/samples/<NN-slug>/`
산출물: `index.html`, `prompt.md`, 렌더 결과 `clip.mp4` `poster.jpg` `preview.gif` (+ 음악 샘플은 `music.wav`, `clip_audio.mp4`)

## index.html 골격 (awesome-ai-motion 하네스 재사용)

```html
<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><title>한글이름 · English</title>
<link rel="stylesheet" href="../../lib/stage.css">
<style>
  /* 하네스 배경 덮기: 장면 배경은 .scene 안의 전면 div로 칠한다 */
  .frame{background:#0d0f12 !important;background-image:none !important}
  .scene{position:absolute;inset:0;overflow:hidden}
</style></head>
<body data-no="S01" data-cat="스타일 · STYLE" data-ko="한글이름" data-en="English" data-meta="요약" data-dur="12" data-size="1280x720">
<main class="scene"> ... </main>
<script src="../../lib/gsap.min.js"></script><script src="../../lib/stage.js"></script>
<script>
const tl = Motion.timeline();
// 모든 움직임은 tl 위에. 절대 시간(초) 위치 인자로 배치.
Motion.ready();
</script></body></html>
```

규칙
- `../../lib/` 경로를 그대로 쓴다(스킬 루트 `lib`는 awesome-ai-motion/lib 심볼릭 링크, 렌더러도 이 경로를 재작성한다).
- 결정론: `Math.random`·`Date.now`·CSS animation/transition·setTimeout 금지. 난수는 `const r = Motion.rand(7)`. 숫자 카운터·타자기·파형 등은 `tl.to(obj,{v:..., onUpdate(){...}}, t)`로 타임라인에 묶는다(seek 시 onUpdate가 호출됨).
- 크기: `data-size` 기본 1280x720. 정사각 1080x1080, 세로 720x1280 가능. 레이아웃은 그 크기 기준 px.
- 글꼴(로컬 설치됨): `Pretendard`, `Gmarket Sans TTF`, `Noto Sans KR`, `NanumMyeongjo`(세리프, Noto Serif KR은 미설치), `IBM Plex Mono`(lib), `Bodoni Moda`(lib). 외부 네트워크·웹폰트·외부 이미지 금지. 그림은 SVG/CSS로 그린다.
- 마지막 0.8초 이상은 완성 상태를 정지(홀드)시킨다. `data-poster`(초)로 대표 프레임 지정 가능.
- 글자 겹침·잘림 금지. 한 장면 한 초점.
- 하네스 클래스명과 겹치지 말 것: `.cap` `.clock` `.num` `.prog` `.folio` (덮어써진다).
- 세로(720x1280)는 하네스의 `body.portrait .scene{left:40px}`를 `body.portrait .scene{left:0;top:0}`로 덮는다(샘플 14 참고).

## 원본 영상(정밀 참고용)
`~/.claude/skills/claude-motion-studio/references/videos/v1.mp4`(피프), `v2.mp4`(Jay Choi). 지정 구간을 `ffmpeg -ss <초> -t <길이> -i v1.mp4 -vf "fps=2,scale=640:-1,tile=4x4" -frames:v 1 out.jpg`로 뽑아 Read로 본다. 개인 참고용이며 배포하지 않는다.

## 렌더·검증

```bash
cd ~/DEV/awesome-ai-motion
node scripts/render.mjs ~/.claude/skills/claude-motion-studio/samples/<NN-slug>/index.html --embed
# 검증용 콘택트시트 (Read로 확인)
ffmpeg -loglevel error -y -i <폴더>/clip.mp4 -vf "fps=<12/길이>,scale=480:-1,tile=4x3" -frames:v 1 <스크래치>/check.jpg
```
콘택트시트를 직접 Read로 보고 빈 화면·겹침·잘림·의도와 다른 장면이 있으면 고쳐서 재렌더한다(최대 3회).

## 음악 (지정된 샘플만)
python3 표준 라이브러리(wave, math, struct)로 BPM에 맞춘 킥·하이햇·베이스·패드를 합성해 `music.wav`(44.1kHz, 길이=data-dur) 저장 → 
`ffmpeg -y -i clip.mp4 -i music.wav -c:v copy -c:a aac -shortest clip_audio.mp4`. 장면 전환 시각을 박자 격자(60/BPM 초)에 맞춘다.

## prompt.md (같은 결과를 Claude에게 다시 시킬 때 쓰는 프롬프트)
```
# <샘플 이름>
원본: <영상 / 타임코드>  · 재현 또는 발전형
## 한 문장 버전
## 구조 버전
<inputs> 문구·소재·비율·길이 </inputs>
<direction> 분위기·색 HEX·글꼴·움직임 동사·카메라 / 금지: ... </direction>
<structure> 샷/박자별 표 (초, 화면, 움직임) </structure>
<build> HTML 한 파일, GSAP 타임라인 seek, 30fps 렌더, 결정론 </build>
## 바꿔 쓰기 포인트 (소재만 교체할 자리)
```
