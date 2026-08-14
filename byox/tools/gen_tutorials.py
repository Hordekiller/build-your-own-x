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
    "observablehq.com/@galletti94/functional-blockchain": "functional-blockchain-ats",
    "write-your-own-blockchain-and-pow-algorithm-using-crystal": "blockchain-crystal-pow",
    "jeiwan.net/posts/building-blockchain-in-go-part-1": "blockchain-go-jeiwan",
    "code-your-own-blockchain-in-less-than-200-lines-of-go": "blockchain-go-200lines",
    "create-simple-blockchain-java-tutorial-from-scratch": "blockchain-java-first",
    "github.com/conradoqg/naivecoin": "naivecoin-js",
    "github.com/nambrot/blockchain-in-js": "blockchain-js-nambrot",
    "learn-build-a-javascript-blockchain-part-1": "blockchain-js-learn-build",
    "github.com/SavjeeTutorials/SavjeeCoin": "savjeecoin-js",
    "how-to-launch-your-own-production-ready-cryptocurrency": "cryptocurrency-js-production",
    "cryptocurrency-blockchain-node-js": "blockchain-node-smashing",
    "implement-a-cryptocurrency-in-kotlin-part-1": "blockchain-kotlin",
    "learn-blockchains-by-building-one": "blockchain-python-learn",
    "ecomunsing.com/build-your-own-blockchain": "blockchain-python-ecomunsing",
    "intro-blockchain-bitcoin-python": "blockchain-python-adilmoujahid",
    "lets-build-the-tiniest-blockchain": "blockchain-python-tiniest",
    "github.com/yukimotopress/programming-blockchains-step-by-step": "blockchain-ruby-book",
    "simple-actor-based-blockchain": "blockchain-scala-actor",
    "lhartikk.github.io": "naivecoin-ts",
    "naivecoinstake.learn.uno": "naivecoinstake-ts",
    "building-a-blockchain-in-rust-and-substrate": "blockchain-rust-substrate",
    "Roll_your_own_IRC_bot": "haskell-irc",
    "making-a-telegram-bot": "telegram-bot-node",
    "discordjs.guide": "discord-js-guide",
    "gifbot-github-integration": "gifbot-github",
    "ai-chatbot-web-speech-api-node-js": "chatbot-web-speech",
    "build-first-slack-bot-python": "slack-bot-python",
    "build-a-slack-bot-with-python": "slack-bot-django",
    "build-a-reddit-bot-part-1": "reddit-bot-python",
    "watch?v=krTUf7BpTc0": "reddit-bot-youtube",
    "how-to-create-a-telegram-bot-using-python": "telegram-bot-python",
    "creating-a-twitter-bot-in-python-with-tweepy": "twitter-bot-tweepy",
    "playlist?list=PLIFBTFgFpoJ9vmYYlfxRFV6U_XhG-4fpP": "reddit-bot-praw",
    "build-a-cryptocurrency-trading-bot-with-r": "crypto-trading-bot-r",
    "habr.com/en/post/436254": "starcraft-bot-rust",
    "go-git-contributions": "go-git-contributions",
    "go-tutorial-lolcat": "go-lolcat",
    "go-tutorial-cowsay": "go-cowsay",
    "go-tutorial-fortune": "go-fortune",
    "day06_nistow": "nim-nistow",
    "create-your-own-cli-tool": "node-cli-tool",
    "rust-cli.github.io": "rust-cli-book",
    "writing-cli-app-rust": "rust-cli-mattgathu",
    "rebuild-x.github.io": "zig-cli",
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
            page = os.path.join(HERE, "..", "tutorials", slug + ".html")
            if os.path.exists(page):
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