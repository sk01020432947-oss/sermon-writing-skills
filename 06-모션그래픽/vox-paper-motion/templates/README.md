# 템플릿 쓰는 법

1. 작업 폴더를 만든다: `~/Desktop/cysjavis/<주제폴더>/<한글이름>/`
2. `project.json`을 복사하고 `소재/` 폴더에 PNG를 넣는다(배경 1장 + 주인공·물건은 흰 배경).
3. 장면마다 `say`(읽을 문장)와 `layers`만 바꾼다. 세로판 배치가 다르면 `layers_v`.
4. `python3 ~/.claude/skills/vox-paper-motion/scripts/vox_sequence.py project.json --voice` → 길이·받아쓰기 확인
5. `python3 ~/.claude/skills/vox-paper-motion/scripts/vox_sequence.py project.json` → 가로·세로·썸네일·자막·검수 시트
6. 고칠 장면만: `--only 2`

이 템플릿의 실제 렌더 결과: `~/Desktop/cysjavis/매뉴얼/영상_이미지도구/Vox종이모션_예제/쇼케이스/`
소재 예시: `~/Desktop/cysjavis/매뉴얼/영상_이미지도구/Vox종이모션_예제/도감소재/`
