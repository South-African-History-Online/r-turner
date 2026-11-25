#!/usr/bin/env python3
"""Fail when a built page points at a missing internal page or file, or when a
built page cannot be reached by following links from the home page."""
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
missing = []
links = {}
for page in root.rglob("*.html"):
    url = "/" + str(page.relative_to(root)).replace("index.html", "")
    links[url] = set()
    for target in re.findall(r'(?:href|src)="?(/[^" >#?]*)', page.read_text(encoding="utf-8")):
        if target.startswith("//"):
            continue
        path = root / target.lstrip("/")
        if (path / "index.html").is_file():
            links[url].add(target if target.endswith("/") else target + "/")
        elif not path.is_file():
            missing.append(f"{page.relative_to(root)} -> {target}")

reached, queue = set(), ["/"]
while queue:
    url = queue.pop()
    if url in reached or url not in links:
        continue
    reached.add(url)
    queue.extend(links[url])

orphans = sorted(url for url in links if url not in reached and url != "/404.html")
for line in sorted(set(missing)):
    print("missing:", line)
for url in orphans:
    print("unreachable from the home page:", url)
if not missing and not orphans:
    print(f"{len(links)} pages: all internal links resolve and every page is reachable from the home page")
sys.exit(1 if missing or orphans else 0)
