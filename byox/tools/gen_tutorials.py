#!/usr/bin/env python3
"""BYOX — generate assets/js/tutorials.js from ../README-fa.md
استفاده: python3 tools/gen_tutorials.py
هر دسته جدید ترجمه شد: لینک‌ها را به DONE اضافه کن و دوباره اجرا کن.
"""
import re, json, html, os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "README-fa.md")
OUT = os.path.join(HERE, "..", "assets", "js", "tutorials.js")

DONE = {
    "scratchapixel.com/lessons/3d-basic-rendering/introduction-to-ray-tracing": "scratchapixel-raytracing-intro",
    "github.com/ssloy/tinyrenderer": "tinyrenderer",
    "lodev.org/cgtutor/raycasting": "lodev-raycasting",
    "pbr-book.org": "pbr-book",
    "raytracing.github.io": "raytracing-in-one-weekend",
    "scratchapixel.com/lessons/3d-basic-rendering/rasterization": "scratchapixel-rasterization",
    "davrous.com/2013/06/13": "davrous-3d-soft-engine",
    "avik-das.github.io": "avik-3d-renderer",
    "blog.rogach.org/2015/08": "rogach-java-3d-render",
    "gabrielgambetta.com/computer-graphics-from-scratch": "gambetta-computer-graphics",
    "aosabook.org/en/500L/a-3d-modeller": "aosabook-3d-modeller",
    "youtube.com/watch?v=uXNjNcqW4kY": "ar-vuforia-unity",
    "youtube.com/playlist?list=PLKIKuXdn4ZMjuUAtdQfK1vwTZPQn_rgSv": "ar-unity-arcore",
    "youtube.com/playlist?list=PLPCqNOwwN794Gz5fzUSi1p4OqLU0HTmvn": "ar-unity-portal",
    "youtube.com/watch?v=qTSDPkPyPqs": "ar-dragon-arcore",
    "youtube.com/watch?v=Z5AmqMuNi08": "ar-arkit-portal",
    "bitesofcode.wordpress.com/2017/09/12": "ar-python-opencv",
    "seanjoflynn.com/research/bittorrent": "bittorrent-csharp",
    "blog.jse.li/posts/torrent": "bittorrent-go",
    "xmonader.github.io/nimdays/day02_bencode": "bencode-parser-nim",
    "allenkim67.github.io/programming/2016/05/04": "bittorrent-node",
    "markuseliasson.se/article/bittorrent-in-python": "bittorrent-python",
}

EN2FA = {"Distributed Systems": "سیستم\u200cهای توزیع\u200cشده"}

line_re = re.compile(r"^[-*] \[\*\*(.+?)\*\*: _(.+)_\]\((https?://[^\s)]+)\)(\s*\[(.+?)\])?$")

tutorials = []
category = None
for raw in open(SRC, encoding="utf-8"):
    line = raw.rstrip("\n")
    if line.startswith("#### "):
        head = line.replace("#### ", "").strip()
        inner = re.search(r"`(.+?)`", head)
        name = inner.group(1) if inner else head
        category = EN2FA.get(name, name)
        continue
    m = line_re.match(line)
    if not m:
        continue
    t = {
        "id": "",
        "category": category,
        "lang": m.group(1),
        "title": html.unescape(m.group(2)),
        "url": m.group(3),
        "video": (m.group(5) or "") == "ویدئو",
        "done": False,
        "file": "",
    }
    for needle, slug in DONE.items():
        if needle in t["url"]:
            t["done"] = True
            t["file"] = "tutorials/" + slug + ".html"
            t["id"] = slug
            break
    tutorials.append(t)

with open(OUT, "w", encoding="utf-8") as f:
    f.write("window.TUTORIALS = ")
    f.write(json.dumps(tutorials, ensure_ascii=False, indent=0))
    f.write(";\n")

print("total:", len(tutorials), "| done:", sum(1 for t in tutorials if t["done"]))
print("written:", OUT)