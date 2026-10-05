#!/usr/bin/env python3
"""
Put exactly what should be published into dist/.

    python3 tools/dist.py github        # the GitHub Pages preview
    python3 tools/dist.py cloudflare    # Cloudflare Pages

Only public files go in: the built pages, robots.txt, assets/ and legacy/.
src/, tools/ and Julie's documents stay out. Run tools/build.py first; this
only copies.

The two hosts differ in two ways. GitHub Pages cannot redirect, so it gets the
forwarding pages from redirects/ for the old WordPress addresses; Cloudflare
gets a _redirects file of real redirects instead. And the GitHub preview lives
under /sensorybeanbags/, so 404.html carries that prefix; Cloudflare serves the
site from the root of the domain, so there it is removed.
"""

import pathlib
import shutil
import sys

import redirects

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
PREVIEW_PREFIX = "/sensorybeanbags/"
CLOUDFLARE_MAX_BYTES = 25 * 1024 * 1024  # Cloudflare Pages refuses larger files
CLOUDFLARE_MAX_FILES = 20000
CLOUDFLARE_MAX_REDIRECTS = 2000


def assemble(target):
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    for page in ROOT.glob("*.html"):
        shutil.copy2(page, DIST)
    shutil.copy2(ROOT / "robots.txt", DIST)
    shutil.copytree(ROOT / "assets", DIST / "assets")
    if (ROOT / "legacy").is_dir():
        shutil.copytree(ROOT / "legacy", DIST / "legacy")

    if target == "github":
        shutil.copy2(ROOT / ".nojekyll", DIST)
        shutil.copytree(ROOT / "redirects", DIST, dirs_exist_ok=True)
        return []

    rules = redirects.cloudflare_rules()
    (DIST / "_redirects").write_text(rules, encoding="utf-8")
    page = DIST / "404.html"
    page.write_text(page.read_text(encoding="utf-8").replace(PREVIEW_PREFIX, "/"), encoding="utf-8")

    problems = []
    files = [f for f in DIST.rglob("*") if f.is_file()]
    if len(files) > CLOUDFLARE_MAX_FILES:
        problems.append("%d files; Cloudflare Pages takes at most %d" % (len(files), CLOUDFLARE_MAX_FILES))
    for f in files:
        if f.stat().st_size > CLOUDFLARE_MAX_BYTES:
            problems.append("%s is over 25 MB, which Cloudflare Pages refuses" % f.relative_to(DIST))
    count = sum(1 for line in rules.splitlines() if line and not line.startswith("#"))
    if count > CLOUDFLARE_MAX_REDIRECTS:
        problems.append("%d redirects; Cloudflare Pages takes at most %d" % (count, CLOUDFLARE_MAX_REDIRECTS))
    return problems


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("github", "cloudflare"):
        raise SystemExit("usage: python3 tools/dist.py github|cloudflare")
    problems = assemble(sys.argv[1])
    files = sum(1 for f in DIST.rglob("*") if f.is_file())
    print("dist/ ready for %s: %d files" % (sys.argv[1], files))
    for p in problems:
        print("PROBLEM: " + p)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
