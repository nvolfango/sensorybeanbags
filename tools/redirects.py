#!/usr/bin/env python3
"""
Forwarding pages for the old WordPress addresses.

GitHub Pages cannot send real redirects, so each old address gets a tiny page
that sends the visitor straight on. They are written to redirects/, which the
deploy copies to the site root: redirects/about-julie-hannon/index.html is
served at /about-julie-hannon/ and forwards to about.html. Cloudflare Pages can
redirect, so tools/dist.py gives it the same list as a _redirects file instead.

The old site's main pages are in OLD, its shop filters in SECTIONS. Every
other page in the copy in legacy/ gets a forwarding page too: shop and product
pages go to the matching new page, and anything with no equivalent on the new
site (the reference articles, image pages, the videos page) goes to its
archived copy.

tools/build.py and tools/mirror_legacy.py both run this, so there is no need to
run it by hand.
"""

import pathlib
import re
import shutil
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "redirects"
LEGACY = ROOT / "legacy"

OLD = {
    "shop": "beanbags.html",
    "online-store": "beanbags.html",
    "sensory-beanbag-information": "beanbags.html",
    "product-information": "beanbags.html",
    "product-information/price-list": "beanbags.html",
    "sensory-products-sizes-and-prices": "beanbags.html",
    "choosing-fabric-colours": "beanbags.html",
    "weighted-products-information": "weighted.html",
    "frequently-asked-questions-faq": "order.html",
    "agency-testing-approvals": "order.html",
    "refunds-and-returns": "order.html",
    "contact-julie-hannon": "order.html",
    "order-form": "order.html",
    "order-tracking": "order.html",
    "thank-you-for-your-order": "order.html",
    "online-worldpay-3ds": "order.html",
    "cart": "order.html",
    "checkout": "order.html",
    "my-account": "order.html",
    "about-julie-hannon": "about.html",
    "testimonials": "about.html",
}
# The shop's option filters (weight, colour, size), whole sections at a time
SECTIONS = {
    "weightedblanket-weight": "weighted.html",
    "weighted-blanket-size": "weighted.html",
    "wt-blnkt-col-in": "weighted.html",
    "wt-blnkt-col-out": "weighted.html",
    "attribute-snake-colour": "weighted.html",
    "attribute-snake-size": "weighted.html",
    "beanbag-colour": "beanbags.html",
}
SHOP_SECTIONS = {"shop", "product", "product-category", "product-tag"}
WEIGHTED = re.compile(r"weight|blanket|lap|snake", re.I)
NOT_OLD_PAGES = {"_ext", "wp-content", "wp-includes", "wp-admin", "wp-json"}

PAGE = """<!doctype html>
<html lang="en-IE">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>This page has moved | Sensory Beanbags</title>
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url=__HREF__">
<script>location.replace("__HREF__");</script>
</head>
<body>
<p>This page has moved. <a href="__HREF__">Continue to the new page</a>.</p>
</body>
</html>
"""


def old_pages():
    """Every old address to forward, as a path without leading or trailing slash."""
    paths = set(OLD)
    if LEGACY.is_dir():
        for page in LEGACY.rglob("index.html"):
            path = page.parent.relative_to(LEGACY).as_posix()
            if path != "." and path.split("/")[0] not in NOT_OLD_PAGES:
                paths.add(path)
    return paths


def destination(path):
    if path in OLD:
        return OLD[path]
    if path.split("/")[0] in SECTIONS:
        return SECTIONS[path.split("/")[0]]
    if path.split("/")[0] in SHOP_SECTIONS:
        return "weighted.html" if WEIGHTED.search(path) else "beanbags.html"
    if (LEGACY / path / "index.html").exists():
        return "legacy/%s/" % path
    return "index.html"


def forwards():
    """(old path, new destination) pairs, leaving out any path the new site itself uses."""
    taken = {p.name for p in ROOT.iterdir()} - {OUT.name}
    for path in sorted(old_pages()):
        if path.split("/")[0] not in taken:
            yield path, destination(path)


def write():
    """Rewrites redirects/ from scratch. Returns how many forwarding pages it wrote."""
    if OUT.exists():
        shutil.rmtree(OUT)
    count = 0
    for path, dest in forwards():
        href = "../" * (path.count("/") + 1) + dest
        target = OUT / path / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(PAGE.replace("__HREF__", href), encoding="utf-8")
        count += 1
    return count


def cloudflare_rules():
    """The same forwards as a Cloudflare Pages _redirects file: real 301 redirects."""
    lines = ["# Old WordPress addresses to their new pages. Made by tools/redirects.py."]
    for path, dest in forwards():
        dest = "/" + (dest[: -len(".html")] if dest.endswith(".html") else dest)
        dest = "/" if dest == "/index" else dest  # Cloudflare serves about.html at /about
        old = "/" + urllib.parse.quote(path)
        lines += ["%s %s 301" % (old, dest), "%s/ %s 301" % (old, dest)]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    print("wrote %d forwarding pages in redirects/" % write())
