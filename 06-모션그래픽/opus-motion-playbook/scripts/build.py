#!/usr/bin/env python3
"""principles.json(정본) → references/principles.md + 정본 HTML 도감."""
import json, os, re

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(HERE, "references")
OUT = os.path.expanduser("~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감.html")


def fmt(sec):
    return f"{sec // 60}:{sec % 60:02d}"


def src_md(d, v, t):
    V = d["videos"][v]
    return f"[{v} {fmt(t)}](https://www.youtube.com/watch?v={V['id']}&t={t}s)" if "id" in V else f"[{v}]({V['url']})"


MAIN_PURPOSES = [
    {"name": "15초 브랜드·채널 인트로", "thumbs": ["D24", "D21", "D19"], "topic": "우리 교회 소개 15초 인트로 영상",
     "hint": "박자에 맞춰 글자가 튀어나오는 키네틱 타이포. 지침·출처·검증까지 한 세트",
     "ids": ["A2", "A3", "A4", "B1", "B2", "B3", "D3", "D21", "D24", "C8", "D14"]},
    {"name": "제품·서비스 광고", "thumbs": ["D17", "D1", "E11"], "topic": "교회 앱 새 기능 소개 광고",
     "hint": "한 물체 변신, 큰 글자 뒤 제품, 숫자 카운트업. 실물이 필요하면 생성형을 붙임",
     "ids": ["A7", "D1", "D2", "D15", "D17", "D19", "E1", "E3", "E11", "D14"]},
    {"name": "개념·과정 설명", "thumbs": ["D5", "D10", "D22"], "topic": "성찬 순서 안내 애니메이션",
     "hint": "단계 진행바, 줌으로 이어지는 이야기, 말을 그림 은유로. 실제 계산으로 시각화",
     "ids": ["A5", "D5", "D7", "D10", "D22", "D4", "D6", "C8"]},
    {"name": "가사·뮤직비디오", "thumbs": ["B8", "D25", "B7"], "topic": "찬양 가사 영상",
     "hint": "마디=가사 줄, 박=핵심 단어. 반복 타일, 손그림 떨림, 음악까지 코드로",
     "ids": ["B1", "B2", "B3", "B7", "B8", "D16", "D25", "C2", "G1"]},
    {"name": "실사 예고편·소개 영상", "thumbs": ["E1", "E7", "D18"], "topic": "수련회 예고편 60초",
     "hint": "사람·공간은 생성형, 글자는 코드. 이미지 먼저, 레퍼런스 유지, 시작·끝 프레임",
     "ids": ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "D13", "D18", "G1"]},
    {"name": "3D·미니어처 장면", "thumbs": ["C11", "D8", "D10"], "topic": "성막 미니어처 3D 장면",
     "hint": "Three.js 누적 피사계심도, 여러 거리에서 보기, 인물 동작은 모션 라이브러리",
     "ids": ["C11", "D8", "D10", "E8", "E9", "C9"]},
]


def main():
    d = json.load(open(os.path.join(REF, "principles.json")))
    # 1) principles.md
    md = [f"# 원리 {len(d['items'])} — opus-motion-playbook", "",
          "정본은 principles.json. 이 파일과 HTML 도감은 `scripts/build.py`가 생성한다.", "", "## 출처", ""]
    for k, v in d["videos"].items():
        link = f"https://www.youtube.com/watch?v={v['id']}" if "id" in v else v["url"]
        md.append(f"- **{k}** [{v['title']}]({link}) — {v['by']}. {v['gist']}")
    for c, cname in d["cats"].items():
        md += ["", f"## {c}. {cname}", ""]
        for i in (x for x in d["items"] if x["cat"] == c):
            md += [f"### {i['id']} {i['name']}", "", i["rule"], "",
                   f"- 프롬프트: `{i['prompt']}`", f"- 응용: {i['apply']}",
                   "- 출처: " + " · ".join(src_md(d, v, t) for v, t in i["src"])]
            if "frame" in i:
                md.append(f"- 원본 장면: {src_md(d, *i['frame'])} → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/{i['id']}.jpg`")
            md.append("")
    md += ["## 하이브리드 실측 (V4)", "", "| 예시 | 코드 단독 | Higgsfield 연결 | 크레딧 | 채택 | 이유 |", "|---|---|---|---|---|---|"]
    md += [f"| {c['task']} | {c['code']} | {c['hybrid']} | {c['credits']} | {c['pick']} | {c['why']} |" for c in d["costs"]]
    open(os.path.join(REF, "principles.md"), "w").write("\n".join(md) + "\n")

    # 2) HTML 데이터 보강
    inst = open(os.path.join(REF, "project-instruction.md")).read()
    blocks = re.findall(r"```text\n(.*?)```", inst, re.S)
    d["instruction"], d["firstMsg"], d["revMsg"] = blocks[0].strip(), blocks[1].strip(), blocks[2].strip()
    apps = open(os.path.join(REF, "applications.md")).read()
    d["apps"] = [[c.strip() for c in row.strip("|").split("|")]
                 for row in re.findall(r"^\|(?! 만들 것|---)(.+)\|$", apps, re.M)]
    d["ways"] = [re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", w) for w in re.findall(r"^\d+\. (.+)$", apps, re.M)]
    ids = {i["id"] for i in d["items"]}
    d["purposes"] = [dict(p, group="main") for p in MAIN_PURPOSES] + [
        {"name": r[0], "ids": [x for x in r[1].split() if x in ids], "hint": r[2], "group": "ministry"} for r in d["apps"]]
    bad = [(p["name"], x) for p in MAIN_PURPOSES for x in p["ids"] + p["thumbs"] if x not in ids]
    assert not bad, bad
    readme = open(os.path.join(REF, "opus-video-prompts", "README.md")).read()
    d["prompts17"] = [{"id": a, "name": b, "by": c, "type": t, "file": f}
                      for a, b, c, t, f in re.findall(r"^\| (\d\d) \| (.+?) \| (.+?) \| (.+?) \| \[열기\]\((prompts/.+?)\) \|$", readme, re.M)]
    d["skillUse"] = ("# Claude Code에서\n"
                     "opus-motion-playbook 스킬로 설교 제목 인트로 15초 만들어 줘.\n"
                     "출처: 주보 PDF 첨부. 128BPM 8마디, 코드만.\n\n"
                     "# 박자표 먼저\n"
                     "python3 ~/.claude/skills/opus-motion-playbook/scripts/beatgrid.py --duration 15 --bars 8 --scenes 8\n\n"
                     "# 렌더 후 강박 시트 검수\n"
                     "python3 ~/.claude/skills/opus-motion-playbook/scripts/beatgrid.py --bpm 128 --duration 15 --sheet clip.mp4")
    fr = os.path.join(os.path.dirname(OUT), "오퍼스_모션원리_도감_자료", "frames")
    d["ver"] = int(max((os.path.getmtime(os.path.join(fr, f)) for f in os.listdir(fr)), default=0)) if os.path.isdir(fr) else 0
    assert len(d["prompts17"]) == 17 and len(blocks) >= 3 and d["apps"] and d["ways"]
    html = open(os.path.join(HERE, "assets", "dogam_template.html")).read()
    html = html.replace("__DATA__", json.dumps(d, ensure_ascii=False).replace("</", "<\\/"))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w").write(html)
    print(f"principles.md · {len(d['items'])}개 원리\nHTML → {OUT} ({len(html) // 1024} KB)")


if __name__ == "__main__":
    main()
