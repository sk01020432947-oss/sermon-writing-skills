#!/usr/bin/env python3
"""catalog.json + samples/* → 도감 폴더(정본) + references/guide.md

정본: ~/Desktop/cysjavis/모션그래픽/웹모션스택_도감/웹모션스택_도감.html  (자료: samples/, lib/ 같은 폴더)
사용: python3 ~/.claude/skills/web-motion-stack/scripts/build.py
"""
import json, re, shutil
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
OUT = Path.home() / "Desktop/cysjavis/모션그래픽/웹모션스택_도감"
LIB = Path.home() / "DEV/awesome-ai-motion/lib"
cat = json.loads((SKILL / "references/catalog.json").read_text())

# 샘플 메타(data-*)는 각 index.html의 body에서 읽는다 — 한 곳에서만 관리
for s in cat["samples"]:
    html = (SKILL / "samples" / s["dir"] / "index.html").read_text()
    body = re.search(r"<body([^>]*)>", html).group(1)
    for k in ("no", "ko", "en", "meta", "dur", "cat"):
        m = re.search(rf'data-{k}="([^"]*)"', body)
        s[k] = m.group(1) if m else ""

# 1) 자료 복사
(OUT / "lib").mkdir(parents=True, exist_ok=True)
for f in ("gsap.min.js", "stage.js", "stage.css"):
    shutil.copy2(LIB / f, OUT / "lib" / f)
shutil.copytree(LIB / "fonts", OUT / "lib/fonts", dirs_exist_ok=True)
for s in cat["samples"]:
    src, dst = SKILL / "samples" / s["dir"], OUT / "samples" / s["dir"]
    dst.mkdir(parents=True, exist_ok=True)
    for f in ("index.html", "clip.mp4", "poster.jpg", "three.min.js"):
        if (src / f).exists():
            shutil.copy2(src / f, dst / f)

# 2) guide.md (Claude가 읽는 텍스트판)
g = [f"# web-motion-stack 가이드 (catalog.json에서 생성)\n\n출처: [{cat['source']['title']}]({cat['source']['url']}) — {cat['source']['channel']}, {cat['source']['duration']}\n\n{cat['source']['summary']}\n"]
g.append("## 웹 기술 7층\n\n| 층 | 역할 | 잘하는 것 | 규모 | 렌더 주의 | 샘플 |\n|---|---|---|---|---|---|")
for l in cat["layers"]:
    g.append(f"| {l['id']} {l['name']} | {l['role']} | {l['good']} | {l['scale']} | {l['render']} | {l['sample']} |")
for gid, gname in cat["groups"].items():
    g.append(f"\n## {gid}. {gname}\n")
    for p in [p for p in cat["principles"] if p["g"] == gid]:
        t = f" ({p['t']//60}:{p['t']%60:02d})" if p["t"] is not None else ""
        g.append(f"### {p['id']} {p['title']}{t}\n{p['body']}")
        if p["prompt"]: g.append(f"- 프롬프트: {p['prompt']}")
        if p["apply"]: g.append(f"- 응용: {p['apply']}")
        g.append("")
g.append("## 샘플 20\n\n| 폴더 | 이름 | 층 | 쓰임 | 바꿔 쓸 곳 |\n|---|---|---|---|---|")
for s in cat["samples"]:
    g.append(f"| {s['dir']} | {s['ko']} ({s['meta']}) | {s['layer']} | {s['use']} | {s['swap']} |")
g.append("\n## 프롬프트 레시피\n")
for r in cat["recipes"]:
    g.append(f"### {r['id']} {r['name']} — {r['when']}\n```\n{r['text']}\n```\n")
g.append("## 응용\n")
for a in cat["applications"]:
    g.append(f"### {a['area']}\n" + "\n".join(f"- {i['name']}: {i['how']}" + (f" (`{i['sample']}`)" if i['sample'] else "") for i in a["items"]) + "\n")
(SKILL / "references/guide.md").write_text("\n".join(g))

# 3) 도감 HTML
tpl = (SKILL / "scripts/dogam_template.html").read_text()
html = tpl.replace("/*DATA*/", json.dumps(cat, ensure_ascii=False).replace("</", "<\\/"))
(OUT / "웹모션스택_도감.html").write_text(html)
print("OK", OUT / "웹모션스택_도감.html", f"{len(html)//1024}KB")
