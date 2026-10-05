#!/usr/bin/env python3
"""
Copy the old WordPress site into legacy/ as a static backup.

    python3 tools/mirror_legacy.py            # copy https://sensorybeanbags.com
    python3 tools/mirror_legacy.py --check    # only re-check the links inside legacy/

Every page of the old site is saved under legacy/ at its original path, so
https://sensorybeanbags.com/about-julie-hannon/ is served at
/legacy/about-julie-hannon/. Links between old pages are rewritten to stay
inside legacy/. The images, stylesheets, scripts, fonts and documents the pages
use are saved alongside them; any that came from another host (web fonts, a
CDN) go under legacy/_ext/<host>/.

The parts that only worked with WordPress running behind them -- the cart,
checkout, account pages, search and feeds -- are not copied, and links to them
lead to legacy/_unavailable.html. Forms do not submit.

Every archived page gets a noindex tag, so search engines never rank it above
the new site, and a one-line banner linking to the new site (--no-banner to
leave that out). Each run replaces legacy/ completely, then rewrites
redirects/ so every old address forwards somewhere (see redirects.py). Python 3
with no packages installed is all it needs.
"""

import argparse
import hashlib
import html
import mimetypes
import pathlib
import posixpath
import re
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import deque
from html.parser import HTMLParser

import redirects

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "legacy"
START = "https://sensorybeanbags.com/"
USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/124.0 Safari/537.36 sensorybeanbags-legacy-copy")
MAX_BYTES = 50 * 1024 * 1024  # GitHub refuses any file over 100 MB
MAX_PAGES = 3000

STATIC_EXT = {
    ".css", ".js", ".mjs", ".json", ".xml", ".txt", ".map",
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".svg", ".ico", ".bmp", ".tif", ".tiff",
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".zip",
    ".mp4", ".webm", ".mov", ".m4v", ".mp3", ".wav", ".ogg",
}
EXT_FOR = {
    "text/css": ".css", "text/javascript": ".js", "application/javascript": ".js",
    "application/x-javascript": ".js", "application/json": ".json", "text/plain": ".txt",
    "application/xml": ".xml", "text/xml": ".xml", "image/jpeg": ".jpg", "image/svg+xml": ".svg",
    "image/x-icon": ".ico", "image/vnd.microsoft.icon": ".ico", "font/woff2": ".woff2",
    "font/woff": ".woff", "font/ttf": ".ttf", "font/otf": ".otf",
    "application/font-woff": ".woff", "application/font-woff2": ".woff2",
}
HTML_TYPES = {"text/html", "application/xhtml+xml"}

# What needed WordPress running: never copied, links to it go to _unavailable.html
SKIP_PATH = re.compile(
    r"^/(?:wp-admin|wp-login\.php|wp-json|wp-cron\.php|xmlrpc\.php|wp-signup\.php|"
    r"cart|basket|checkout|my-account|feed|comments/feed)(?:/|$)"
    r"|/(?:feed|trackback|embed)/?$",
    re.I,
)
SKIP_QUERY = re.compile(
    r"(?:^|&)(?:add-to-cart|add_to_wishlist|remove_item|removed_item|undo_item|replytocom|share|"
    r"s|orderby|min_price|max_price|rating_filter|filter_[\w-]+|query_type_[\w-]+|wc-ajax|wc-api|"
    r"action|redirect_to|_wpnonce|preview|customize_[\w-]+|doing_wp_cron|feed)=",
    re.I,
)
ASSET_RELS = {"stylesheet", "icon", "shortcut", "apple-touch-icon", "apple-touch-icon-precomposed",
              "mask-icon", "preload", "modulepreload", "manifest"}
URL_ATTRS = {"href", "src", "poster", "data", "background"}

CSS_URL = re.compile(r"""url\(\s*(?:"([^"]*)"|'([^']*)'|([^)"'\s]*))\s*\)""", re.I)
CSS_IMPORT = re.compile(r"""@import\s+(?:"([^"]*)"|'([^']*)')""", re.I)
TAG = re.compile(r"<[a-zA-Z][^>]*>")
ATTR = re.compile(r"""(\s)([\w:.-]+)(\s*=\s*)("[^"]*"|'[^']*'|[^\s"'=<>`]+)""")
STYLE_BLOCK = re.compile(r"(<style\b[^>]*>)(.*?)(</style>)", re.I | re.S)
LOOSE_URL = re.compile(r"""https?:\\?/\\?/[^\s"'<>()\[\]{},;]+""")
DROP_LINKS = re.compile(
    r"""<link\b[^>]*\brel\s*=\s*["']?(?:canonical|shortlink|alternate|pingback|edituri|wlwmanifest|"""
    r"""https://api\.w\.org/)(?=[\s"'>])[^>]*>[ \t]*\n?""",
    re.I,
)
DROP_ROBOTS = re.compile(r"""<meta\b[^>]*\bname\s*=\s*["']?robots(?=[\s"'>])[^>]*>[ \t]*\n?""", re.I)
HEAD_OPEN = re.compile(r"<head\b[^>]*>", re.I)
BODY_OPEN = re.compile(r"<body\b[^>]*>", re.I)

BANNER = (
    '\n<div role="note" style="position:relative;z-index:2147483647;margin:0;padding:10px 16px;'
    'background:#1F5F5B;color:#fff;font:15px/1.45 system-ui,-apple-system,Segoe UI,sans-serif;'
    'text-align:center">This is an archived copy of the old Sensory Beanbags website, kept as a '
    'backup. <a href="__HOME__" style="color:#fff;font-weight:700;text-decoration:underline">'
    'Go to the current website</a></div>\n'
)
UNAVAILABLE = """<!doctype html>
<html lang="en-IE">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Not in the archive | Sensory Beanbags</title>
<style>
body{max-width:36rem;margin:4rem auto;padding:0 16px;font:17px/1.55 system-ui,sans-serif;color:#1d1d1b;background:#fff}
a{color:#1F5F5B}
</style>
</head>
<body>
<h1>Not part of the archived copy</h1>
<p>This is a static copy of the old Sensory Beanbags website, kept as a backup. The shop's cart,
checkout and account pages, the search and the feeds needed the old WordPress system running
behind them, so they were not copied.</p>
<p><a href="./">Back to the archived home page</a> &middot; <a href="../">Go to the current website</a></p>
</body>
</html>
"""


def is_static(path):
    return posixpath.splitext(path)[1].lower() in STATIC_EXT


def looks_like_file(value):
    v = value.strip()
    if not v or len(v) > 2000 or any(c in v for c in ' \t\n<>{}"'):
        return False
    return is_static(urllib.parse.urlsplit(v).path)


def css_urls(css):
    for m in CSS_URL.finditer(css):
        yield next(g for g in m.groups() if g is not None)
    for m in CSS_IMPORT.finditer(css):
        yield next(g for g in m.groups() if g is not None)


def srcset_urls(value):
    for part in re.split(r",\s+", value.strip()):
        bits = part.split()
        if bits:
            yield bits[0]


def extension_for(ctype):
    return EXT_FOR.get(ctype) or mimetypes.guess_extension(ctype) or ".bin"


class LinkFinder(HTMLParser):
    """Collects (url, kind) pairs from one page; kind is "page" or "asset"."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.found = []
        self.base = None
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        if tag == "style":
            self.in_style = True
        rels = set()
        for name, value in attrs:
            if name == "rel" and value:
                rels = set(value.lower().split())
        for name, value in attrs:
            if not value:
                continue
            if tag == "base" and name == "href":
                self.base = value
            elif name == "href" and tag in ("a", "area"):
                self.found.append((value, "page"))
            elif name == "href" and tag == "link":
                if rels & ASSET_RELS:
                    self.found.append((value, "asset"))
            elif name == "src" and tag in ("iframe", "frame"):
                self.found.append((value, "page"))
            elif name == "style":
                self.found.extend((u, "asset") for u in css_urls(value))
            elif name.endswith("srcset"):
                self.found.extend((u, "asset") for u in srcset_urls(value))
            elif name in URL_ATTRS or looks_like_file(value):
                self.found.append((value, "asset"))

    def handle_endtag(self, tag):
        if tag == "style":
            self.in_style = False

    def handle_data(self, data):
        if self.in_style:
            self.found.extend((u, "asset") for u in css_urls(data))


class Mirror:
    def __init__(self, start, aliases=(), delay=0.3, banner=True):
        if not urllib.parse.urlsplit(start).path:
            start += "/"
        p = urllib.parse.urlsplit(start)
        self.start = start
        self.scheme, self.host = p.scheme, p.netloc.lower()
        bare = self.host[4:] if self.host.startswith("www.") else self.host
        self.hosts = {self.host, bare, "www." + bare} | {a.lower() for a in aliases}
        self.delay = delay
        self.banner = banner
        self.files = {}          # normalised URL -> path under legacy/
        self.pages = {}          # path of each saved page -> URL its links resolve against
        self.styles = {}         # path of each saved stylesheet -> its URL
        self.unavailable = set() # old-site URLs deliberately not copied
        self.failed = {}         # URL -> why it could not be copied
        self.queue = deque()
        self.queued = set()
        self.page_count = 0

    # --- URLs --------------------------------------------------------------

    def norm(self, url):
        p = urllib.parse.urlsplit(url.strip())
        if p.scheme not in ("http", "https") or not p.netloc:
            return None
        host, scheme = p.netloc.lower(), p.scheme
        if host in self.hosts:
            host, scheme = self.host, self.scheme
        path = urllib.parse.quote(urllib.parse.unquote(p.path or "/"), safe="/!$&'()*+,;=:@~-._")
        query = "" if is_static(path) else p.query  # ?ver=… only busts caches
        return urllib.parse.urlunsplit((scheme, host, path, query, ""))

    def is_old_site(self, url):
        return urllib.parse.urlsplit(url).netloc == self.host

    def local_path(self, url, ctype):
        p = urllib.parse.urlsplit(url)
        path = urllib.parse.unquote(p.path) or "/"
        if p.netloc != self.host:
            path = "/_ext/" + p.netloc.replace(":", "_") + path
        is_html = ctype in HTML_TYPES
        if path.endswith("/"):
            path += "index.html" if is_html else "index" + extension_for(ctype)
        elif is_html and posixpath.splitext(path)[1].lower() not in (".html", ".htm"):
            path += "/index.html"
        elif not posixpath.splitext(path)[1]:
            path += extension_for(ctype)
        if p.query:
            stem, ext = posixpath.splitext(path)
            path = "%s__%s%s" % (stem, hashlib.sha1(p.query.encode()).hexdigest()[:8], ext)
        parts = [re.sub(r'[\x00-\x1f"*:<>?\\|]', "_", s) for s in path.split("/") if s not in ("", ".", "..")]
        return "/".join(parts)

    def enqueue(self, url, kind):
        n = self.norm(url)
        if n is None or n in self.queued:
            return
        p = urllib.parse.urlsplit(n)
        if p.netloc == self.host:
            if SKIP_PATH.search(p.path) or SKIP_QUERY.search(p.query):
                self.unavailable.add(n)
                return
            if kind == "page" and is_static(p.path):
                kind = "asset"
            if kind == "page":
                if self.page_count >= MAX_PAGES:
                    return
                self.page_count += 1
        elif kind == "page":
            return  # links to other websites stay as they are
        self.queued.add(n)
        self.queue.append((n, kind))

    # --- copying -----------------------------------------------------------

    def fetch(self, url):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    data = r.read(MAX_BYTES + 1)
                    if len(data) > MAX_BYTES:
                        raise ValueError("larger than %d MB" % (MAX_BYTES >> 20))
                    return r.geturl(), r.headers.get_content_type(), data
            except urllib.error.HTTPError as e:
                if e.code < 500 or attempt == 2:
                    raise
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                if attempt == 2:
                    raise
            time.sleep(2 ** attempt)

    def sitemap_pages(self):
        """Every page the old site's sitemaps list, so pages nothing links to are copied too."""
        todo = [urllib.parse.urljoin(self.start, p) for p in ("/wp-sitemap.xml", "/sitemap_index.xml", "/sitemap.xml")]
        try:
            _, _, robots = self.fetch(urllib.parse.urljoin(self.start, "/robots.txt"))
            todo += re.findall(r"(?im)^\s*sitemap:\s*(\S+)", robots.decode("utf-8", "replace"))
        except Exception:
            pass
        seen, pages = set(), []
        while todo and len(seen) < 200:
            url = todo.pop()
            if url in seen:
                continue
            seen.add(url)
            try:
                root = ET.fromstring(self.fetch(url)[2])
            except Exception:
                continue
            into = todo if root.tag.endswith("sitemapindex") else pages
            into += [e.text.strip() for e in root.iter() if e.tag.endswith("loc") and e.text]
        return pages

    def run(self):
        if OUT.exists():
            shutil.rmtree(OUT)
        OUT.mkdir()
        self.enqueue(self.start, "page")
        for url in self.sitemap_pages():
            self.enqueue(url, "page")
        done = 0
        while self.queue:
            url, kind = self.queue.popleft()
            done += 1
            if done % 50 == 0:
                print("  %d copied, %d to go" % (done, len(self.queue)), flush=True)
            try:
                final, ctype, data = self.fetch(url)
            except Exception as e:
                self.failed[url] = str(e)
                continue
            if self.is_old_site(url):
                time.sleep(self.delay)
            final = self.norm(final) or url
            if final != url and final in self.files:
                self.files[url] = self.files[final]
                continue
            if kind == "page" and not self.is_old_site(final):
                continue  # redirects away from the old site
            path = self.local_path(final, ctype)
            try:
                (OUT / path).parent.mkdir(parents=True, exist_ok=True)
                (OUT / path).write_bytes(data)
            except OSError as e:
                self.failed[url] = "could not save as %s: %s" % (path, e)
                continue
            self.files[url] = self.files[final] = path
            if ctype in HTML_TYPES:
                text = data.decode("utf-8", "replace")
                finder = LinkFinder()
                try:
                    finder.feed(text)
                except Exception as e:
                    self.failed[url] = "could not read all its links: %s" % e
                base = urllib.parse.urljoin(final, finder.base) if finder.base else final
                self.pages[path] = base
                for link, k in finder.found:
                    self.enqueue(urllib.parse.urljoin(base, link), k)
                for m in LOOSE_URL.finditer(text):
                    loose = self.norm(m.group(0).rstrip("\\").replace("\\/", "/"))
                    if loose and self.is_old_site(loose) and is_static(urllib.parse.urlsplit(loose).path):
                        self.enqueue(loose, "asset")
            elif ctype == "text/css":
                self.styles[path] = final
                for link in css_urls(data.decode("utf-8", "replace")):
                    self.enqueue(urllib.parse.urljoin(final, link), "asset")
        self.rewrite()
        (OUT / "_unavailable.html").write_text(UNAVAILABLE, encoding="utf-8")

    # --- rewriting ---------------------------------------------------------

    def map_url(self, value, base, here):
        """The link that reaches `value`'s copy from the file in directory `here`, or `value` unchanged."""
        v = value.strip()
        if not v or v.startswith(("#", "data:", "mailto:", "tel:", "javascript:", "about:", "blob:")):
            return value
        absolute = urllib.parse.urljoin(base, v)
        n = self.norm(absolute)
        if n is None:
            return value
        target = self.files.get(n)
        if target is None:
            if n not in self.unavailable:
                return value
            target = "_unavailable.html"
        rel = posixpath.relpath(target, here or ".")
        if target in self.pages and posixpath.basename(rel) == "index.html":
            rel = rel[: -len("index.html")] or "./"
        rel = urllib.parse.quote(rel, safe="/!$&'()*+,;=:@~-._")
        frag = urllib.parse.urlsplit(absolute).fragment
        return rel + ("#" + frag if frag else "")

    def rewrite_css(self, css, base, here):
        def url(m):
            old = next(g for g in m.groups() if g is not None)
            new = self.map_url(old, base, here)
            return m.group(0) if new == old else 'url("%s")' % new

        def imp(m):
            old = next(g for g in m.groups() if g is not None)
            new = self.map_url(old, base, here)
            return m.group(0) if new == old else '@import "%s"' % new

        return CSS_IMPORT.sub(imp, CSS_URL.sub(url, css))

    def rewrite_tag(self, tag, base, here):
        def attr(m):
            name, raw = m.group(2).lower(), m.group(4)
            quote = raw[0] if raw[0] in "\"'" else '"'
            value = html.unescape(raw[1:-1] if raw[0] in "\"'" else raw)
            if name == "style":
                new = self.rewrite_css(value, base, here)
            elif name.endswith("srcset"):
                parts = [part.split(None, 1) for part in re.split(r",\s+", value.strip())]
                mapped = [[self.map_url(bits[0], base, here)] + bits[1:] for bits in parts if bits]
                changed = any(m[0] != bits[0] for m, bits in zip(mapped, [b for b in parts if b]))
                new = ", ".join(" ".join(m) for m in mapped) if changed else value
            elif name in URL_ATTRS or looks_like_file(value):
                new = self.map_url(value, base, here)
            else:
                return m.group(0)
            if new == value:
                return m.group(0)
            escaped = new.replace("&", "&amp;").replace(quote, "&quot;" if quote == '"' else "&#39;")
            return "%s%s%s%s%s%s" % (m.group(1), m.group(2), m.group(3), quote, escaped, quote)

        return ATTR.sub(attr, tag)

    def rewrite_loose(self, text, base, here):
        """Old-site file URLs left in scripts and JSON, e.g. slider images."""
        def sub(m):
            found = m.group(0).rstrip("\\")
            escaped = "\\/" in found
            new = self.map_url(found.replace("\\/", "/"), base, here)
            if new == found.replace("\\/", "/"):
                return m.group(0)
            return (new.replace("/", "\\/") if escaped else new) + m.group(0)[len(found):]

        return LOOSE_URL.sub(sub, text)

    def mark_archived(self, text, here):
        text = DROP_ROBOTS.sub("", DROP_LINKS.sub("", text))
        noindex = '\n<meta name="robots" content="noindex, nofollow">'
        if HEAD_OPEN.search(text):
            text = HEAD_OPEN.sub(lambda m: m.group(0) + noindex, text, count=1)
        else:
            text = noindex.lstrip() + "\n" + text
        if self.banner:
            home = "../" * (len(here.split("/")) + 1 if here else 1)
            text = BODY_OPEN.sub(lambda m: m.group(0) + BANNER.replace("__HOME__", home), text, count=1)
        return text

    def rewrite(self):
        for path, base in self.pages.items():
            here = posixpath.dirname(path)
            text = (OUT / path).read_bytes().decode("utf-8", "surrogateescape")
            text = TAG.sub(lambda m: self.rewrite_tag(m.group(0), base, here), text)
            text = STYLE_BLOCK.sub(lambda m: m.group(1) + self.rewrite_css(m.group(2), base, here) + m.group(3), text)
            text = self.rewrite_loose(text, base, here)
            text = self.mark_archived(text, here)
            (OUT / path).write_bytes(text.encode("utf-8", "surrogateescape"))
        for path, url in self.styles.items():
            text = (OUT / path).read_bytes().decode("utf-8", "surrogateescape")
            text = self.rewrite_css(text, url, posixpath.dirname(path))
            (OUT / path).write_bytes(text.encode("utf-8", "surrogateescape"))

    def report(self):
        size = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
        hosts = sorted({p.split("/")[1] for p in self.files.values() if p.startswith("_ext/")})
        print("\nCopied %d pages and %d files in all, %.1f MB." % (len(self.pages), len(set(self.files.values())), size / 1e6))
        print("Other hosts copied from: %s" % (", ".join(hosts) or "none"))
        print("Left out on purpose (cart, checkout, feeds…): %d links" % len(self.unavailable))
        if self.failed:
            print("Could not copy %d:" % len(self.failed))
            for url, why in sorted(self.failed.items())[:40]:
                print("  %s  (%s)" % (url, why))


def check(old_hosts):
    """Every relative link inside legacy/ must reach a file. Returns True when none are broken."""
    if not OUT.is_dir():
        print("There is no legacy/ yet: run this without --check to make it.")
        return False
    broken, absolute = [], set()
    files = [f for f in OUT.rglob("*") if f.suffix in (".html", ".css")]
    for f in files:
        text = f.read_text("utf-8", "replace")
        if f.suffix == ".html":
            finder = LinkFinder()
            try:
                finder.feed(text)
            except Exception:
                pass
            refs = [u for u, _ in finder.found]
        else:
            refs = list(css_urls(text))
        for ref in refs:
            p = urllib.parse.urlsplit(ref.strip())
            if p.scheme or ref.startswith(("#", "//")) or not p.path:
                if p.netloc.lower() in old_hosts:
                    absolute.add(ref)
                continue
            if ref.startswith("/"):
                absolute.add(ref)
                continue
            target = (f.parent / urllib.parse.unquote(p.path)).resolve()
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                broken.append("%s -> %s" % (f.relative_to(ROOT), ref))
    print("Checked %d files in legacy/: %d broken links." % (len(files), len(broken)))
    for b in broken[:40]:
        print("  " + b)
    if absolute:
        print("%d links still point at the old site's address or root; after the domain moves they reach"
              " the new site instead:" % len(absolute))
        for a in sorted(absolute)[:20]:
            print("  " + a)
    return not broken


def main():
    ap = argparse.ArgumentParser(description="Copy the old WordPress site into legacy/.")
    ap.add_argument("--start", default=START, help="the old site's address (default %(default)s)")
    ap.add_argument("--alias", action="append", default=[], help="another host name the old site answers on")
    ap.add_argument("--delay", type=float, default=0.3, help="seconds between requests to the old site")
    ap.add_argument("--no-banner", action="store_true", help="leave out the 'archived copy' banner")
    ap.add_argument("--check", action="store_true", help="only check the links inside the existing legacy/")
    args = ap.parse_args()
    mirror = Mirror(args.start, args.alias, args.delay, not args.no_banner)
    if not args.check:
        print("Copying %s into %s/" % (mirror.start, OUT.relative_to(ROOT)), flush=True)
        mirror.run()
        mirror.report()
        print("Wrote %d forwarding pages for old addresses in redirects/." % redirects.write())
    sys.exit(0 if check(mirror.hosts) else 1)


if __name__ == "__main__":
    main()
