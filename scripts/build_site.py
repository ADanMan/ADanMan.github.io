#!/usr/bin/env python3
"""Generate publications.html from ADanMan/agentic-frontier's tree.

Stdlib-only. Fetches the repo tree via the GitHub API, pulls raw markdown for
posts/til/guides entries, parses frontmatter + the RU title, and renders
publications.html with the same site chrome as index.html. Never crashes:
falls back to a cached tree, then to leaving publications.html untouched.
"""
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
CACHE_DIR = os.path.join(DATA_DIR, "cache")
TREE_CACHE = os.path.join(DATA_DIR, "tree.json")
OUT_FILE = os.path.join(ROOT, "publications.html")

REPO = "ADanMan/agentic-frontier"
TREE_URL = f"https://api.github.com/repos/{REPO}/git/trees/main?recursive=1"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/main/"
BLOB_BASE = f"https://github.com/{REPO}/blob/main/"

PATH_RE = re.compile(r"^(posts|til|guides)/([^/]+(?:/[^/]+)*)$")


def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "adanman-site-builder"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def local_af_dir():
    """A local clone of agentic-frontier, if present (AF_DIR env or ./_af).

    The cloud routine's sandbox blocks api.github.com but can `git clone` over
    the git channel, so the routine clones the repo and points AF_DIR at it.
    """
    for cand in (os.environ.get("AF_DIR"), os.path.join(ROOT, "_af")):
        if cand and os.path.isdir(os.path.join(cand, "posts")):
            return cand
    return None


def tree_from_local(af):
    paths = []
    for stream in ("posts", "til", "guides"):
        base = os.path.join(af, stream)
        for dirpath, _dirs, files in os.walk(base):
            if "index.md" in files:
                rel = os.path.relpath(os.path.join(dirpath, "index.md"), af)
                paths.append(rel.replace(os.sep, "/"))
    return {"tree": [{"path": p, "type": "blob"} for p in paths]}


def get_tree():
    af = local_af_dir()
    if af:
        return tree_from_local(af)
    try:
        data = json.loads(fetch(TREE_URL))
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(TREE_CACHE, "w") as f:
            json.dump(data, f)
        return data
    except Exception as e:
        print(f"warning: live tree fetch failed ({e}), trying cache", file=sys.stderr)
    if os.path.exists(TREE_CACHE):
        with open(TREE_CACHE) as f:
            return json.load(f)
    return None


def parse_frontmatter(md):
    meta = {}
    if md.startswith("---"):
        end = md.find("\n---", 3)
        if end != -1:
            block = md[3:end]
            for line in block.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta


def ru_title(md, slug):
    idx = md.find("## Русская версия")
    if idx != -1:
        m = re.search(r"^#\s+(.+)$", md[idx:], re.MULTILINE)
        if m:
            return m.group(1).strip()
        m = re.search(r"^##\s+(.+)$", md[idx + len("## Русская версия"):], re.MULTILINE)
        if m:
            return m.group(1).strip()
    return slug.replace("-", " ").title()


def get_markdown(path):
    af = local_af_dir()
    if af:
        try:
            with open(os.path.join(af, path)) as f:
                return f.read()
        except OSError:
            return None
    cache_path = os.path.join(CACHE_DIR, path)
    if os.path.exists(cache_path):
        with open(cache_path) as f:
            return f.read()
    try:
        md = fetch(RAW_BASE + path).decode("utf-8", "replace")
    except Exception as e:
        print(f"warning: failed to fetch {path}: {e}", file=sys.stderr)
        return None
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "w") as f:
        f.write(md)
    return md


CARD = """<li class="pub-item">
  <span class="pub-date">{date}</span>
  <a href="{url}">{title}</a>
</li>"""

SECTION_TITLES = {
    "posts": ("Посты", "Posts"),
    "til": ("TIL", "TIL"),
    "guides": ("Гайды", "Guides"),
}


def render(entries):
    by_kind = {"posts": [], "til": [], "guides": []}
    for kind, path, title, date in entries:
        by_kind[kind].append((date, title, path))
    for kind in by_kind:
        by_kind[kind].sort(reverse=True)

    sections = []
    total = 0
    for kind in ("posts", "til", "guides"):
        items = by_kind[kind]
        if not items:
            continue
        total += len(items)
        ru, en = SECTION_TITLES[kind]
        cards = "\n".join(
            CARD.format(date=date or "", url=BLOB_BASE + path, title=title)
            for date, title, path in items
        )
        sections.append(
            f'<h2 class="section-title">{ru}/{en}</h2>\n<ul class="pub-list">\n{cards}\n</ul>'
        )

    body = "\n".join(sections) if sections else '<p class="lang-ru">Пока пусто.</p><p class="lang-en">Nothing yet.</p>'

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Публикации — Данила Катальшов</title>
<meta name="description" content="Посты, TIL и гайды Данилы Катальшова из agentic-frontier.">
<link rel="icon" href="assets/logo.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=IBM+Plex+Serif:ital,wght@0,400;0,600;1,400&display=swap">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<div class="loader" id="loader" aria-hidden="true"><span></span><span></span><span></span></div>
<header class="masthead">
  <a class="brand" href="index.html"><img class="logo" src="assets/logo.svg" alt="">ДК<span>/</span>DK</a>
  <nav>
    <a href="index.html" class="nav-link"><span class="lang-ru">Резюме</span><span class="lang-en">Resume</span></a>
    <a href="https://github.com/ADanMan/agentic-frontier" class="nav-link">GitHub</a>
    <button id="langToggle" class="lang-toggle" aria-label="Switch language">EN</button>
  </nav>
</header>
<main>
<h1 class="page-title"><span class="lang-ru">Публикации</span><span class="lang-en">Writing</span></h1>
{body}
</main>
<footer>
  <span class="lang-ru">© 2026 Данила Катальшов ·</span><span class="lang-en">© 2026 Danila Katalshov ·</span>
  <a href="https://github.com/ADanMan/ADanMan.github.io">GitHub</a>
</footer>
<script src="assets/site.js"></script>
</body>
</html>
"""
    with open(OUT_FILE, "w") as f:
        f.write(html)
    return total


def main():
    tree = get_tree()
    if tree is None:
        print("no tree available (live fetch and cache both failed) — leaving publications.html untouched")
        return 0

    paths = [
        item["path"]
        for item in tree.get("tree", [])
        if item.get("type") == "blob" and PATH_RE.match(item["path"]) and item["path"].endswith("index.md")
    ]
    # also accept flat .md files under til/guides
    paths += [
        item["path"]
        for item in tree.get("tree", [])
        if item.get("type") == "blob"
        and PATH_RE.match(item["path"])
        and item["path"].endswith(".md")
        and item["path"] not in paths
    ]
    paths = sorted(set(paths))

    entries = []
    for path in paths:
        m = PATH_RE.match(path)
        kind = m.group(1)
        md = get_markdown(path)
        if md is None:
            continue
        meta = parse_frontmatter(md)
        slug = path.split("/")[-2] if path.endswith("index.md") else os.path.splitext(path.split("/")[-1])[0]
        title = ru_title(md, slug)
        date = meta.get("date", "")
        if not date:
            m2 = re.search(r"(\d{4}-\d{2}-\d{2})", path)
            date = m2.group(1) if m2 else ""
        entries.append((kind, path, title, date))

    count = render(entries)
    print(f"build_site.py: rendered publications.html with {count} publication(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
