#!/usr/bin/env python3
"""
Build the static Sensory Beanbags site.

Page bodies live in src/pages/*.html. This script wraps each one in the shared
header/footer and writes plain .html files to the repository root, which is what
GitHub Pages serves. There is no runtime dependency on this script: the built
HTML is committed and works on its own. Re-run it only after editing the shared
chrome below or a file in src/pages/.

    python3 tools/build.py
"""

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "pages"

SITE_NAME = "Sensory Beanbags"
TAGLINE = "a Julia Hannon original"
EMAIL = "marihannon@gmail.com"
PHONE_DISPLAY = "087 131 9619"
PHONE_LINK = "+353871319619"
BASE_URL = "https://nvolfango.github.io/sensorybeanbags"

NAV = [
    ("index.html", "Home"),
    ("beanbags.html", "Sensory beanbags"),
    ("weighted.html", "Weighted products"),
    ("about.html", "About Julia"),
    ("order.html", "How to order"),
]

LOGO_SVG = (
    '<svg viewBox="0 0 32 32" aria-hidden="true" focusable="false">'
    '<path fill="currentColor" d="M16 3.2c5.5 0 8 4.4 7.2 9 4.8 1.8 7.3 6.2 6.4 10.4'
    '-.8 3.9-5.2 6.2-13.6 6.2S3.2 26.5 2.4 22.6c-.9-4.2 1.6-8.6 6.4-10.4C8 7.6 10.5 3.2 16 3.2Z"/>'
    "</svg>"
)

ICONS = {
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2Z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 7 10 6 10-6"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>',
}

LAYOUT = """<!doctype html>
<html lang="en-IE">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<meta name="description" content="__DESC__">
<link rel="canonical" href="__CANONICAL__">
<meta property="og:type" content="website">
<meta property="og:site_name" content="__SITE__">
<meta property="og:title" content="__TITLE__">
<meta property="og:description" content="__DESC__">
<meta property="og:url" content="__CANONICAL__">
<meta name="theme-color" content="#1F5F5B">
<!-- PREVIEW ONLY: remove this line (and robots.txt) when the site goes live on sensorybeanbags.com -->
<meta name="robots" content="noindex, nofollow">
<link rel="icon" href="data:image/svg+xml,__FAVICON__">
<link rel="stylesheet" href="assets/css/site.css">
</head>
<body>
<a class="skip" href="#main">Skip to main content</a>

<header class="site-header">
  <div class="wrap header-bar">
    <a class="brand" href="index.html">
      __LOGO__
      <span class="brand-text"><b>__SITE__</b><span>__TAGLINE__</span></span>
    </a>

    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="primary-nav">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
      Menu
    </button>

    <nav class="nav" id="primary-nav" aria-label="Primary">
      <ul>
__NAVITEMS__
      </ul>
    </nav>
  </div>
</header>

<main id="main">
__BODY__
</main>

<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a class="brand" href="index.html">
          __LOGO__
          <span class="brand-text"><b>__SITE__</b><span>__TAGLINE__</span></span>
        </a>
        <p style="margin-top:1rem;max-width:34ch">Therapeutic sensory beanbags and weighted products, hand-made in County Cork, Ireland since 2002.</p>
      </div>
      <div>
        <h2>Pages</h2>
        <ul>
__FOOTERNAV__
        </ul>
      </div>
      <div>
        <h2>Get in touch</h2>
        <ul>
          <li><a href="tel:__PHONELINK__">__PHONE__</a></li>
          <li><a href="mailto:__EMAIL__">__EMAIL__</a></li>
          <li>County Cork, Ireland</li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; __YEAR__ __SITE__ &mdash; __TAGLINE__</span>
      <span>Hand-made in Ireland &middot; CE approved</span>
    </div>
  </div>
</footer>

<script src="assets/js/site.js" defer></script>
</body>
</html>
"""

FAVICON = (
    "%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2032%2032'%3E"
    "%3Cpath%20fill='%231F5F5B'%20d='M16%203.2c5.5%200%208%204.4%207.2%209%204.8%201.8%207.3%206.2%206.4%2010.4"
    "-.8%203.9-5.2%206.2-13.6%206.2S3.2%2026.5%202.4%2022.6c-.9-4.2%201.6-8.6%206.4-10.4C8%207.6%2010.5%203.2%2016%203.2Z'/%3E%3C/svg%3E"
)


CONTACT_PANEL = """<section>
  <div class="wrap">
    <div class="contact-panel">
      <div class="grid grid--2" style="gap:2rem;align-items:center">
        <div>
          <h2>Talk to Julia</h2>
          <p>Every beanbag is made to order, so there is always someone to ask before you buy. Questions about sizes, fabrics, weights or delivery are all welcome.</p>
          <div class="btn-row">
            <a class="btn btn--primary" href="tel:{{PHONELINK}}">{{ICON:phone}} {{PHONE}}</a>
            <a class="btn btn--ghost" href="mailto:{{EMAIL}}">{{ICON:mail}} Email Julia</a>
          </div>
        </div>
        <ul class="contact-list">
          <li>{{ICON:phone}}<div><a href="tel:{{PHONELINK}}">{{PHONE}}</a><small>Phone or text</small></div></li>
          <li>{{ICON:mail}}<div><a href="mailto:{{EMAIL}}">{{EMAIL}}</a><small>Usually answered within a day or two</small></div></li>
          <li>{{ICON:pin}}<div>County Cork, Ireland<small>Everything is made here by hand</small></div></li>
        </ul>
      </div>
    </div>
  </div>
</section>
"""

def nav_html(current, indent, cta=True):
    out = []
    for href, label in NAV:
        classes = ""
        if cta and href == "order.html":
            classes = ' class="nav-cta"'
        aria = ' aria-current="page"' if href == current else ""
        out.append('%s<li%s><a href="%s"%s>%s</a></li>' % (indent, classes, href, aria, label))
    return "\n".join(out)


def footer_nav_html(indent):
    out = []
    for href, label in NAV:
        out.append('%s<li><a href="%s">%s</a></li>' % (indent, href, label))
    return "\n".join(out)


def build():
    pages = sorted(SRC.glob("*.html"))
    if not pages:
        raise SystemExit("No page sources found in %s" % SRC)

    for page in pages:
        raw = page.read_text(encoding="utf-8")

        meta = {}
        m = re.match(r"^<!--META\s*(.*?)-->\s*", raw, re.S)
        if not m:
            raise SystemExit("%s is missing its <!--META ... --> block" % page.name)
        for line in m.group(1).strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = raw[m.end():]

        name = page.name
        canonical = BASE_URL + "/" + ("" if name == "index.html" else name)

        html = LAYOUT
        for token, value in [
            ("__TITLE__", meta["title"]),
            ("__DESC__", meta["description"]),
            ("__CANONICAL__", canonical),
            ("__SITE__", SITE_NAME),
            ("__TAGLINE__", TAGLINE),
            ("__LOGO__", LOGO_SVG),
            ("__FAVICON__", FAVICON),
            ("__NAVITEMS__", nav_html(name, " " * 8)),
            ("__FOOTERNAV__", footer_nav_html(" " * 10)),
            ("__PHONE__", PHONE_DISPLAY),
            ("__PHONELINK__", PHONE_LINK),
            ("__EMAIL__", EMAIL),
            ("__YEAR__", "2026"),
            ("__BODY__", body.rstrip()),
        ]:
            html = html.replace(token, value)

        # Shared snippets available inside page bodies
        html = html.replace("{{CONTACT}}", CONTACT_PANEL)
        html = html.replace("{{PHONE}}", PHONE_DISPLAY)
        html = html.replace("{{PHONELINK}}", PHONE_LINK)
        html = html.replace("{{EMAIL}}", EMAIL)
        for key, svg in ICONS.items():
            html = html.replace("{{ICON:%s}}" % key, svg)

        (ROOT / name).write_text(html, encoding="utf-8")
        print("built %s" % name)


if __name__ == "__main__":
    build()
