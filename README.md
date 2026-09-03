# ADanMan.github.io

Personal site / resume for Danila Katalshov, served via GitHub Pages at
https://adanman.github.io. Neubrutalist design shared with
[frontier-wire](https://github.com/ADanMan/frontier-wire).

- `index.html` — bilingual (RU/EN) resume one-pager
- `publications.html` — generated list of posts/TIL/guides pulled from
  [agentic-frontier](https://github.com/ADanMan/agentic-frontier)
- `scripts/build_site.py` — stdlib-only Python script that rebuilds
  `publications.html` from the agentic-frontier repo tree; run with
  `python3 scripts/build_site.py`. Caches fetched markdown under `data/cache/`
  and the last-known repo tree under `data/tree.json`, and never fails the
  build — on a fetch error it falls back to the cache, or leaves
  `publications.html` untouched.

MIT licensed, see `LICENSE`.
