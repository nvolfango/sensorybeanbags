#!/usr/bin/env python3
"""
Put exactly what should be published into dist/.

    python3 tools/dist.py github        # the GitHub Pages preview
    python3 tools/dist.py cloudflare    # Cloudflare Pages

Only public files go in: the built pages, robots.txt, assets/ and legacy/.
src/, tools/ and Julie's documents stay out. Run tools/build.py first; this
only copies.

Cloudflare serves the real site, sensorybeanbags.com, from the main branch.
That build gets a _redirects file of real redirects for the old WordPress
addresses, a sitemap.xml, the robots.txt that lets search engines in,
404.html without the preview's /sensorybeanbags/ prefix, no notes.html
(Julie's review notes), and a _routes.json so that only /api/* (the
checkout, in functions/) runs code. Cloudflare deploys functions/ itself
from the repository root; it is not copied here.

Cloudflare also builds every other branch, as a preview at
<branch>.<project>.pages.dev; the stage branch is the one with a name of its
own, stage.sensorybeanbags.com (see "Staging site" in README.md). Cloudflare
tells the build which branch it is on in CF_PAGES_BRANCH, and for any branch
but main this makes a test copy: every page noindexed, a robots.txt that
shuts crawlers out, no sitemap, notes.html kept, and a banner on every page
saying it is the test copy. To try that locally:

    CF_PAGES_BRANCH=stage python3 tools/dist.py cloudflare

GitHub Pages serves the older preview, which must never compete with the
real site either: it gets the same noindex, robots.txt and banner. GitHub
Pages cannot redirect, so it gets the forwarding pages from redirects/
instead of a _redirects file.
"""

import os
import pathlib
import re
import shutil
import sys

import build
import redirects

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
PRODUCTION_BRANCH = "main"
PREVIEW_PREFIX = "/sensorybeanbags/"
CLOUDFLARE_MAX_BYTES = 25 * 1024 * 1024  # Cloudflare Pages refuses larger files
CLOUDFLARE_MAX_FILES = 20000
CLOUDFLARE_MAX_REDIRECTS = 2000
NOT_IN_SITEMAP = {"404.html", "notes.html", "cart.html"}
# Only the checkout API invokes the Pages Function; everything else is a plain file.
ROUTES = '{"version": 1, "include": ["/api/*"], "exclude": []}\n'
PREVIEW_ROBOTS = """# PREVIEW SITE: a staging copy of sensorybeanbags.com for review only.
# It must never be indexed, or it would compete with the real site.
User-agent: *
Disallow: /
"""
NOINDEX = '<meta name="robots" content="noindex, nofollow">'
BANNER = ('<div class="stage-banner" role="note">Test copy of the website (__WHICH__). '
          'Changes are tried out here before they go live. '
          '<a href="https://sensorybeanbags.com/">The real website</a></div>')


def hide_from_search():
    """A noindex tag on every page and a robots.txt that keeps crawlers out."""
    (DIST / "robots.txt").write_text(PREVIEW_ROBOTS, encoding="utf-8")
    for page in DIST.glob("*.html"):
        text = page.read_text(encoding="utf-8")
        if 'name="robots"' not in text:
            text = re.sub(r"(<head[^>]*>)", lambda m: m.group(1) + "\n" + NOINDEX, text, count=1)
            page.write_text(text, encoding="utf-8")


def add_banner(which):
    """The test-copy banner at the top of every page, after the skip link so
    keyboard users still reach "Skip to main content" first."""
    banner = BANNER.replace("__WHICH__", which)
    for page in DIST.glob("*.html"):
        text = page.read_text(encoding="utf-8")
        skip = re.search(r'<a class="skip"[^>]*>.*?</a>\n?', text)
        if skip:
            text = text[: skip.end()] + banner + "\n" + text[skip.end():]
        else:
            text = re.sub(r"(<body[^>]*>\n?)", lambda m: m.group(1) + banner + "\n", text, count=1)
        page.write_text(text, encoding="utf-8")


def assemble(target, branch=None, commit=None):
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
        hide_from_search()
        add_banner("GitHub preview")
        return []

    if is_test_copy(branch):
        hide_from_search()
        add_banner("%s branch, %s" % (branch, commit[:7]) if commit else "%s branch" % branch)
    else:
        (DIST / "notes.html").unlink()
        urls = [build.BASE_URL + "/" + ("" if p.name == "index.html" else p.stem)
                for p in sorted(ROOT.glob("*.html")) if p.name not in NOT_IN_SITEMAP]
        (DIST / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "".join("  <url><loc>%s</loc></url>\n" % u for u in urls)
            + "</urlset>\n", encoding="utf-8")

    rules = redirects.cloudflare_rules()
    (DIST / "_redirects").write_text(rules, encoding="utf-8")
    (DIST / "_routes.json").write_text(ROUTES, encoding="utf-8")
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


def is_test_copy(branch):
    """Cloudflare builds every branch; only main is the real site."""
    return bool(branch) and branch != PRODUCTION_BRANCH


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("github", "cloudflare"):
        raise SystemExit("usage: python3 tools/dist.py github|cloudflare")
    target = sys.argv[1]
    branch = os.environ.get("CF_PAGES_BRANCH") if target == "cloudflare" else None
    problems = assemble(target, branch, os.environ.get("CF_PAGES_COMMIT_SHA"))
    files = sum(1 for f in DIST.rglob("*") if f.is_file())
    what = target
    if is_test_copy(branch):
        what += " (test copy for the %s branch: noindex, banner, notes kept)" % branch
    elif target == "cloudflare":
        what += " (the real site)"
    print("dist/ ready for %s: %d files" % (what, files))
    for p in problems:
        print("PROBLEM: " + p)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
