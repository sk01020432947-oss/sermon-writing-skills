#!/usr/bin/env python3
"""~/.claude/skills에서 주제별 스킬을 다시 복사하고 README를 새로 만든다.
사용: python3 update.py  → 확인 후 git add -A && git commit && git push"""
import re, shutil, pathlib

H = pathlib.Path.home()
S = H / '.claude/skills'
DST = pathlib.Path(__file__).resolve().parent
names = sorted(p.name for p in S.iterdir() if p.is_dir())

def m(*pats):
    return [n for n in names if any(re.fullmatch(p, n) for p in pats)]

cats = {
    '01-설교': m(r'sermon-.*', r'dwelling-sermon-coach', r'kangjunmin-sermon-writing-coach',
                r'churchplan-sermon-planner-52.*', r'small-group-questions', r'midweek-devotional'),
    '02-성경연구-주해': m(r'pbs-.*', r'bible-study-lesson-plan', r'romans-meditation-study',
                     r'pauline-law-hermeneutics', r'next-gen-ministry-bible'),
    '03-글쓰기': m(r'.*writing-coach', r'my-writing-master-prompt', r'writing-analytical-essay', r'reading-craft',
                 r'korean-slang-writing', r'copywriting', r'script-writer.*', r'bookwriting-.*'),
    '04-퇴고-교정': m(r'toego-korean', r'korean-spell-check', r'ste-korean', r'humanize.*',
                   r'korean-humanizer', r'korean-character-count'),
    '05-덱-PPT': m(r'.*-deck', r'claude-ppt', r'html-ppt', r'my-ppt', r'ppt-maestro', r'pptx-design-styles',
                  r'kbg-infographic'),
    '06-모션그래픽': m(r'awesome-ai-motion', r'claude-motion-studio', r'opus-motion-playbook', r'motion-order-sheet',
                   r'web-motion-stack', r'vox-paper-motion', r'remotion', r'manim-video', r'explainer-video', r'animate'),
    '07-법령정보': m(r'korean-law-search', r'korean-privacy-terms'),
    '08-문서호환': m(r'hwp', r'hwpx.*', r'new-hwpx-master.*', r'read-hwp', r'rhwp-.*', r'kordoc-obsidian-bridge',
                 r'officecli', r'nudocs', r'korean-doc-corpus', r'gongik-seosik'),
}
cats['03-글쓰기'] = [n for n in cats['03-글쓰기'] if n not in cats['01-설교']]

skip = shutil.ignore_patterns('.git', 'node_modules', '__pycache__', '.venv', 'venv', '.DS_Store', '*.pyc',
                              '.env', '.env.*', '*.mp4', '*.mov', '*.wav', '*.mp3', '*.m4a')
# 카테고리 폴더만 지운다 (.git·README·이 스크립트는 그대로)
for d in DST.glob('0[0-9]-*'):
    shutil.rmtree(d)
for c, ns in cats.items():
    for n in ns:
        shutil.copytree(S / n, DST / c / n, ignore=skip, ignore_dangling_symlinks=True)

ex = next((H / '.claude/plugins/synced').glob('*/ask-exegesis-pipeline'), None)
if ex:
    shutil.copytree(ex, DST / '02-성경연구-주해/ask-exegesis-pipeline', ignore=skip)
    cats['02-성경연구-주해'].append('ask-exegesis-pipeline (플러그인, 9개 스킬)')

def desc(p):
    f = p / 'SKILL.md'
    if not f.exists():
        return ''
    mm = re.search(r'^description:\s*(.+)$', f.read_text(errors='ignore'), re.M)
    d = mm.group(1).strip().strip('"\'') if mm else ''
    return (d[:90] + '…' if len(d) > 90 else d).replace('|', '/')

L = ['# 설교·글쓰기·문서 스킬 모음', '',
     'Claude Code용 스킬을 주제별로 묶은 저장소입니다. 각 폴더를 `~/.claude/skills/`에 복사하면 바로 쓸 수 있습니다.', '',
     '> 동영상·음성 샘플(mp4·mov·wav·mp3)은 용량 문제로 저장소에서 뺐습니다. '
     '라이선스·출처는 아래 [라이선스·출처](#라이선스출처) 단락과 [CREDITS.md](CREDITS.md)를 보세요.', '']
for c, ns in cats.items():
    L += [f'## {c} ({len(ns)})', '', '| 스킬 | 설명 |', '|---|---|']
    for n in ns:
        k = n.split(' ')[0]
        L.append(f'| [`{n}`]({c}/{k}) | {desc(DST / c / k)} |')
    L.append('')
L += ['## 설치', '',
      '### 방법 1. Claude Code에 맡기기', '',
      '아래 문구를 그대로 복사해서 Claude Code에 붙여 넣으세요.', '',
      '```text',
      '아래 GitHub 저장소의 스킬을 내 Claude Code에 설치해줘.', '',
      '저장소: https://github.com/sk01020432947-oss/sermon-writing-skills', '',
      '1. 저장소를 임시 폴더에 git clone한다.',
      '2. 01-설교 ~ 08-문서호환 폴더 안의 스킬 폴더(SKILL.md가 있는 폴더)를 각각 ~/.claude/skills/ 아래로 복사한다.',
      '   - 예: 01-설교/sermon-pipeline → ~/.claude/skills/sermon-pipeline',
      '   - 02-성경연구-주해/ask-exegesis-pipeline은 플러그인 구조다. 그 안의 skills/ 하위 폴더 9개를 ~/.claude/skills/로 복사한다.',
      '3. 같은 이름의 스킬이 이미 있으면 덮어쓰지 말고, 목록을 보여주고 나에게 물어본다.',
      '4. 다 끝나면 설치한 스킬 수를 카테고리별로 알려주고, 새 세션을 시작하면 스킬이 보인다고 안내한다.',
      '5. 임시 폴더는 지운다.',
      '```', '',
      '### 방법 2. 직접 설치 (macOS·Linux)', '',
      '전체 설치 (같은 이름의 스킬이 있으면 건너뜁니다):', '',
      '```bash',
      'git clone --depth 1 https://github.com/sk01020432947-oss/sermon-writing-skills.git /tmp/sws',
      'mkdir -p ~/.claude/skills',
      'for d in /tmp/sws/0*/*/ /tmp/sws/02-*/ask-exegesis-pipeline/skills/*/; do',
      '  [ -f "$d/SKILL.md" ] || continue',
      '  n=$(basename "$d"); [ -e ~/.claude/skills/"$n" ] && echo "건너뜀: $n" || cp -R "$d" ~/.claude/skills/"$n"',
      'done',
      'rm -rf /tmp/sws',
      '```', '',
      '스킬 하나만 설치하려면 해당 폴더만 복사합니다:', '',
      '```bash', 'cp -R 01-설교/sermon-pipeline ~/.claude/skills/', '```', '',
      '설치 후 Claude Code 새 세션을 시작하면 스킬이 보입니다.', '',
      '## 라이선스·출처', '',
      '이 저장소는 여러 제작자의 스킬을 모은 것이라 **저장소 전체에 하나의 라이선스를 붙이지 않았습니다.** '
      '각 스킬의 권리는 원 제작자에게 있습니다.', '',
      '- 스킬별 원 저장소·라이선스·참고 자료: [CREDITS.md](CREDITS.md)',
      '- 쓰거나 다시 배포하기 전에 각 폴더의 `LICENSE`·`SKILL.md`를 확인하세요.',
      '- 권리자이신데 삭제나 출처 수정을 원하시면 '
      '[이슈](https://github.com/sk01020432947-oss/sermon-writing-skills/issues)로 알려 주세요.', '',
      '## 갱신', '', '로컬 스킬을 고친 뒤 이 저장소를 맞추려면:', '', '```bash', 'python3 update.py',
      'git add -A && git commit -m "스킬 갱신" && git push', '```', '']
(DST / 'README.md').write_text('\n'.join(L))
for c, ns in cats.items():
    print(c, len(ns))
