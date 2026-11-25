#!/usr/bin/env python3
"""Fail when a built page points at an internal page or file that does not exist."""
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
missing = []
for page in root.rglob("*.html"):
    for target in re.findall(r'(?:href|src)="?(/[^" >#?]*)', page.read_text(encoding="utf-8")):
        if target.startswith("//"):
            continue
        path = root / target.lstrip("/")
        if not (path.is_file() or (path / "index.html").is_file()):
            missing.append(f"{page.relative_to(root)} -> {target}")

print("\n".join(sorted(set(missing))) or "all internal links resolve")
sys.exit(1 if missing else 0)
