#!/usr/bin/env python3
"""Build the molasp-lab static site (blog + designs + research-log) into _site/.

Reads the markdown the lane maintains and renders a deployable static site:

  blog/*.md          -> <date>-<slug>.html   (post pages, hero art if present)
  designs/*.md       -> designs/<name>.html  (design docs, plain layout)
  research-log/*.md  -> research-log/<name>.html (working notes, plain layout)
  blog/index.md      -> index.html           (timeline of posts + sections)

Uses the `markdown` package when importable (CI installs it); falls back to
escaping raw text so a build never silently produces garbage HTML.

Usage: python3 tools/build_blog.py
"""

import html as H
import re
import shutil
import sys
from pathlib import Path

try:
    import markdown as MD
except ImportError:  # stdlib fallback keeps the build reproducible anywhere
    MD = None

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "blog"
DESIGNS = ROOT / "designs"
RLOG = ROOT / "research-log"
ASSETS = BLOG / "assets"
OUT = ROOT / "_site"

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
          "Oct", "Nov", "Dec")

NAV = (
    '<header class="site"><a class="brand" href="index.html">molasp-lab</a>'
    '<nav><a href="index.html">Posts</a>'
    '<a href="index.html#designs">Designs</a>'
    '<a href="index.html#research-log">Research log</a>'
    '<a href="https://github.com/SonniaAI/molasp-lab">Repository</a></nav></header>'
)

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · molasp-lab</title>
<link rel="stylesheet" href="{css}">
</head>
<body>
{nav}
<main>
{body}
</main>
<footer>
<p>molasp-lab · research notes on compiling answer-set programs to molecular
substrates · Sonnia AI Limited</p>
</footer>
</body>
</html>
"""


def to_html(text):
    if MD is not None:
        html = MD.markdown(text, extensions=["fenced_code", "tables"])
    else:
        html = "<pre>" + H.escape(text) + "</pre>"
    # Relative cross-links to raw .md files resolve on GitHub but not on the
    # rendered site: point section cross-links at their .html sibling and send
    # raw daily-log links to the repository (working notes stay in the repo).
    html = re.sub(r'href="\.\./log/([^"]+?)\.md"',
                  r'href="https://github.com/SonniaAI/molasp-lab/blob/main/'
                  r'log/\1.md"', html)
    html = re.sub(r'href="\.\./(designs|research-log)/([^"]+?)\.md"',
                  r'href="\1/\2.html"', html)
    return re.sub(r'href="(?!https?://)([^"]+?)\.md"', r'href="\1.html"',
                  html)


def parse_post(path):
    """Return dict with title, date, slug, meta, tldr, body for one md file."""
    m = DATE_RE.match(path.name)
    date = m.group(1) if m else ""
    slug = path.stem
    lines = path.read_text(encoding="utf-8").splitlines()
    title = slug.replace("-", " ").title()
    meta = ""
    start = 0
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        start = 1
    if start < len(lines):
        second = lines[start].strip()
        # A meta line is the short byline under the title ("Oct 6, 2026 · … · 8 min"
        # or "*2026-10-07 — molasp-lab*"); anything else starts the body.
        if second and not second.startswith("#") and (
                second.strip("*").startswith(MONTHS)
                or second.strip("*").startswith(date)
                or " · " in second):
            meta = second.strip("*").strip()
            start += 1
    body = "\n".join(lines[start:])
    tldr = ""
    mt = re.search(r"\*\*TL;DR\.\*\*\s*(.+?)(?:\n\s*\n|$)", body, re.S)
    if mt:
        tldr = re.sub(r"\s+", " ", mt.group(1)).replace("**", "").strip()
    else:
        paras = [p.strip() for p in body.split("\n\n") if p.strip()]
        para = next((p for p in paras
                     if not re.match(r"^\*?\d{4}-\d{2}-\d{2} — ", p)),
                    paras[0] if paras else "")
        para = re.sub(r"[`*]", "", para)
        tldr = (para[:220] + "…") if len(para) > 220 else para
    return {"title": title, "date": date, "slug": slug, "meta": meta,
            "tldr": tldr, "body": body}


def page(title, body, depth=0):
    css = "assets/theme.css" if depth == 0 else "../assets/theme.css"
    nav = NAV if depth == 0 else NAV.replace('href="index.html',
                                             'href="../index.html')
    return PAGE.format(title=H.escape(title), css=css, nav=nav, body=body)


def hero_for(path):
    img = ASSETS / (path.stem + ".png")
    if img.exists():
        return ('<figure class="hero"><img src="assets/{}" alt="" '
                'loading="lazy"></figure>'.format(img.name))
    return ""


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    posts = []
    for path in sorted(BLOG.glob("*.md")):
        if path.name == "index.md":
            continue
        post = parse_post(path)
        hero = hero_for(path)
        body = (hero
                + '<h1 class="post-title">{}</h1>\n<p class="meta">{}</p>\n{}'
                .format(H.escape(post["title"]), H.escape(post["meta"]),
                        to_html(post["body"])))
        (OUT / (post["slug"] + ".html")).write_text(
            page(post["title"], body), encoding="utf-8")
        posts.append(post)

    posts.sort(key=lambda p: p["date"], reverse=True)

    def doc_section(folder, folder_name, anchor):
        files = sorted(folder.glob("*.md")) if folder.exists() else []
        if not files:
            return ""
        items = "".join(
            '<li><a href="{}/{}.html">{}</a></li>'.format(
                folder_name, f.stem, H.escape(f.stem))
            for f in files)
        return ('<section id="{anchor}"><h2>{name}</h2><ul class="docs">'
                "{items}</ul></section>".format(
                    anchor=anchor, name=folder_name.replace("-", " ").title(),
                    items=items))

    cards = []
    for p in posts:
        cards.append(
            '<article class="card"><time>{}</time><h3><a href="{}.html">'
            "{}</a></h3><p>{}</p></article>".format(
                H.escape(p["meta"] or p["date"]), p["slug"],
                H.escape(p["title"]), H.escape(p["tldr"][:400])))

    banner = ""
    if (ASSETS / "banner.png").exists():
        banner = ('<figure class="hero"><img src="assets/banner.png" alt="" '
                  "loading=\"lazy\"></figure>")

    index_body = banner + (
        '<h1 class="site-title">molasp-lab</h1>\n'
        '<p class="lede">Working notes on compiling answer-set programs to '
        "molecular substrates — designs, measurements and demolitions, written "
        "for the people who run them. Everything here is also in the "
        '<a href="https://github.com/SonniaAI/molasp-lab">repository</a>; '
        "this site is the reading copy.</p>\n"
        '<section id="posts"><h2>Posts</h2>' + "".join(cards) + "</section>\n"
        + doc_section(DESIGNS, "designs", "designs")
        + doc_section(RLOG, "research-log", "research-log"))
    (OUT / "index.html").write_text(page("molasp-lab", index_body),
                                   encoding="utf-8")

    for folder_name, folder in (("designs", DESIGNS), ("research-log", RLOG)):
        if not folder.exists():
            continue
        outdir = OUT / folder_name
        outdir.mkdir(exist_ok=True)
        for path in sorted(folder.glob("*.md")):
            doc = parse_post(path)
            body = ('<h1 class="post-title">{}</h1>\n<p class="meta">{}</p>\n{}'
                    .format(H.escape(doc["title"]), H.escape(doc["meta"]),
                            to_html(doc["body"])))
            (outdir / (path.stem + ".html")).write_text(
                page(doc["title"], body, depth=1), encoding="utf-8")

    (OUT / "assets").mkdir(exist_ok=True)
    if ASSETS.exists():
        for png in ASSETS.glob("*.png"):
            shutil.copy2(png, OUT / "assets" / png.name)
    theme = ROOT / "tools" / "theme.css"
    if theme.exists():
        shutil.copy2(theme, OUT / "assets" / "theme.css")

    n = sum(1 for _ in OUT.rglob("*.html"))
    print("built {} html pages into {}".format(n, OUT))


if __name__ == "__main__":
    build()
