#!/usr/bin/env python3
"""BYOX-EN — generate byox-en/assets/js/tutorials-en.js

Source of truth: root README.md (the English upstream catalog).
Joined with the Persian byox/assets/js/tutorials.js by normalized URL so
English pages reuse the same ids and know which tutorials have a Persian
translation (`fa` flag).

Usage:
    python3 tools/gen_en_data.py

Author a new wave of English pages, add their ids to byox-en/en-done.json,
then re-run this script.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(ROOT, "README.md")
FA_JS = os.path.join(ROOT, "byox", "assets", "js", "tutorials.js")
OUT = os.path.join(ROOT, "byox-en", "assets", "js", "tutorials-en.js")
DONE_JSON = os.path.join(ROOT, "byox-en", "en-done.json")

CATEGORY_ICONS = {
    "Distributed Systems": "🧵",
    "3D Renderer": "🎨",
    "AI Model": "🤖",
    "Augmented Reality": "🥽",
    "BitTorrent Client": "🧲",
    "Blockchain / Cryptocurrency": "⛓️",
    "Bot": "🤖",
    "Command-Line Tool": "⌨️",
    "Database": "🗄️",
    "Docker": "🐳",
    "Emulator / Virtual Machine": "🧮",
    "Front-end Framework / Library": "🧩",
    "Game": "🕹️",
    "Git": "🌿",
    "Memory Allocator": "🧠",
    "Network Stack": "🌐",
    "Neural Network": "🧬",
    "Operating System": "💾",
    "Physics Engine": "⚙️",
    "Processor": "⚡",
    "Programming Language": "💬",
    "Regex Engine": "🔍",
    "Search Engine": "🕵️",
    "Shell": "🖥️",
    "Template Engine": "🧾",
    "Text Editor": "📝",
    "Visual Recognition System": "👁️",
    "Voxel Engine": "🧊",
    "Web Browser": "🧭",
    "Web Server": "🛰️",
    "Uncategorized": "📦",
}


def norm_url(u):
    u = u.strip()
    u = u.rstrip("/")
    u = u.replace("https://", "http://")
    return u


def parse_readme(path):
    """Yield (category, lang, title, url, is_video) from README.md."""
    text = open(path, encoding="utf-8").read()
    cat = None
    pattern = re.compile(
        r"\[\*\*(?P<lang>.+?)\*\*\s*:\s*_?(?P<title>.+?)_?\s*\]\((?P<url>[^)\s]+)\)"
    )
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"#### Build your own `(.+?)`", line)
        if m:
            cat = m.group(1)
            continue
        if not line.strip().startswith("* ["):
            continue
        m = pattern.search(line)
        if not m:
            print("SKIP unparsed:", line.strip()[:100])
            continue
        url = m.group("url").rstrip(".")
        is_video = bool(re.search(r"\[video\]", line)) or bool(
            re.search(r"\[video\]", lines[i + 1] if i + 1 < len(lines) else "")
        )
        yield cat, m.group("lang"), m.group("title").strip(), url, is_video


def main():
    fa_items = []
    fa_js = open(FA_JS, encoding="utf-8").read()
    for block in re.findall(r"\{[^{}]*?\}", fa_js):
        d = dict(re.findall(r'"(\w+)":\s*("(?:[^"\\]|\\.)*"|true|false)', block))
        if "id" not in d:
            continue
        d = {k: json.loads(v) for k, v in d.items()}
        fa_items.append(d)
    fa_by_url = {norm_url(t["url"]): t for t in fa_items}
    print("fa items:", len(fa_items), "unique ids:", len({t["id"] for t in fa_items}))

    done = set()
    if os.path.exists(DONE_JSON):
        done = set(json.load(open(DONE_JSON, encoding="utf-8")))

    items = []
    seen_urls = set()
    for cat, lang, title, url, is_video in parse_readme(SRC):
        u = norm_url(url)
        if u in seen_urls:
            continue  # a few README rows repeat; keep the first
        seen_urls.add(u)
        fa = fa_by_url.get(u)
        items.append({
            "id": fa["id"] if fa else f"en-{len(items) + 1:03d}",
            "category": cat,
            "lang": fa["lang"] if fa else lang.strip("()"),
            "title": title,
            "url": url,
            "video": is_video or bool(fa and fa.get("video")),
            "fa": bool(fa),
            "done": fa["id"] in done if fa else False,
            "file": None if not (fa and fa["id"] in done) else fa["id"] + ".html",
        })

    print("README items:", len(items))
    print("no fa counterpart:", sum(1 for t in items if not t["fa"]))
    for t in items:
        if not t["fa"]:
            print("   no-fa:", t["title"][:70], "|", t["url"][:60])
    print("en done:", sum(1 for t in items if t["done"]))

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("window.TUTORIALS = [\n")
        for t in items:
            f.write("  " + json.dumps(t, ensure_ascii=False) + ",\n")
        f.write("];\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()