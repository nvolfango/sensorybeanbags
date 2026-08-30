#!/usr/bin/env python3
"""
Build a single-file preview of the whole site, for sending to someone to review.

All five pages go into one HTML file and the navigation switches between them
client side, so the whole site can be shared as a single link with no hosting.
The stylesheet is the site's own, inlined unchanged — what you see is what the
real pages look like.

    python3 tools/build_preview.py [output.html]

This is a review aid only. It is not part of the deployed site.
"""

import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build  # noqa: E402

ROOT = build.ROOT
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "preview.html"

BANNER = """<div class="preview-banner" role="note">
  <strong>Draft preview</strong>
  <span>Not the live site. Prices, photographs and some wording are still to be confirmed &mdash; the dashed orange marks show what is outstanding.</span>
</div>
"""

EXTRA_CSS = """
/* ---- Preview-only styles (not part of the real site) ---- */
.preview-banner {
  background: var(--panel-bg); color: #fff;
  padding: .7rem var(--gut); font-size: .875rem;
  display: flex; flex-wrap: wrap; gap: .15rem .6rem; align-items: baseline;
  justify-content: center; text-align: center;
}
.preview-banner strong { letter-spacing: .04em; text-transform: uppercase; font-size: .78rem; }
.preview-banner span { color: rgba(255,255,255,.82); }
.site-header { top: 0; }
.page[hidden] { display: none; }
"""


def expand(html):
    """Run the same token expansion build.py does."""
    html = html.replace("{{CONTACT}}", build.CONTACT_PANEL)
    html = html.replace("{{PHONE}}", build.PHONE_DISPLAY)
    html = html.replace("{{PHONELINK}}", build.PHONE_LINK)
    html = html.replace("{{EMAIL}}", build.EMAIL)
    for key, svg in build.ICONS.items():
        html = html.replace("{{ICON:%s}}" % key, svg)
    return html


def dark_theme_stamp(css):
    """
    site.css defines its dark tokens inside a prefers-color-scheme query. The
    artifact viewer can also stamp data-theme="dark" explicitly, so re-emit the
    same tokens under that selector. Generated from the source block rather than
    hand-copied, so the two cannot drift apart.
    """
    m = re.search(
        r"@media \(prefers-color-scheme: dark\) \{\s*:root:not\(\[data-theme=\"light\"\]\) \{(.*?)\n  \}\n\}",
        css,
        re.S,
    )
    if not m:
        raise SystemExit("could not find the dark token block in site.css")
    return '\n:root[data-theme="dark"] {%s\n}\n' % m.group(1)


def main():
    css = (ROOT / "assets" / "css" / "site.css").read_text(encoding="utf-8")
    js = (ROOT / "assets" / "js" / "site.js").read_text(encoding="utf-8")

    sections = []
    for href, _label in build.NAV:
        src = (build.SRC / href).read_text(encoding="utf-8")
        body = re.sub(r"^<!--META.*?-->\s*", "", src, flags=re.S)
        slug = href[:-5]
        sections.append(
            '<div class="page" id="page-%s"%s>\n%s\n</div>'
            % (slug, "" if href == "index.html" else " hidden", expand(body).rstrip())
        )

    header = expand(
        build.LAYOUT.split("<main id=\"main\">")[0].split("<body>", 1)[1]
    ).replace("__LOGO__", build.LOGO_SVG).replace("__SITE__", build.SITE_NAME).replace(
        "__TAGLINE__", build.TAGLINE
    ).replace("__NAVITEMS__", build.nav_html("index.html", " " * 8))

    footer = expand(
        build.LAYOUT.split("</main>")[1].split("<script")[0]
    ).replace("__LOGO__", build.LOGO_SVG).replace("__SITE__", build.SITE_NAME).replace(
        "__TAGLINE__", build.TAGLINE
    ).replace("__FOOTERNAV__", build.footer_nav_html(" " * 10)).replace(
        "__PHONELINK__", build.PHONE_LINK
    ).replace("__PHONE__", build.PHONE_DISPLAY).replace("__EMAIL__", build.EMAIL).replace(
        "__YEAR__", "2026"
    )

    nav_js = """
/* Preview only: the five pages live in one file, so navigation swaps sections. */
(function () {
  "use strict";
  var pages = %s;
  function show(slug, push) {
    if (pages.indexOf(slug) === -1) slug = "index";
    pages.forEach(function (p) {
      document.getElementById("page-" + p).hidden = (p !== slug);
    });
    /* Only navigation links carry aria-current, not links in the body copy. */
    document.querySelectorAll('.nav a[data-page]').forEach(function (a) {
      if (a.getAttribute («data-page») === slug) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
    if (push) history.replaceState(null, "", "#" + slug);
    window.scrollTo(0, 0);
    var h = document.querySelector("#page-" + slug + " h1");
    if (h) { h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); }
  }
  document.addEventListener("click", function (e) {
    var a = e.target.closest("a[data-page]");
    if (!a) return;
    e.preventDefault();
    show(a.getAttribute("data-page"), true);
  });
  show((location.hash || "#index").slice(1), false);
})();
""" % (str([h[:-5] for h, _ in build.NAV]).replace("'", '"'))
    nav_js = nav_js.replace("«data-page»", '"data-page"')

    out = []
    out.append("<title>Sensory Beanbags</title>")
    out.append("<style>\n%s\n%s\n%s</style>" % (css, dark_theme_stamp(css), EXTRA_CSS))
    out.append(BANNER)
    out.append(header.strip())
    out.append('<main id="main">')
    out.extend(sections)
    out.append("</main>")
    out.append(footer.strip())
    out.append("<script>\n%s\n%s\n</script>" % (js, nav_js))

    html = "\n".join(out)
    # Internal links become section switches rather than page loads.
    html = re.sub(r'href="([a-z0-9-]+)\.html"', lambda m: 'href="#%s" data-page="%s"' % (m.group(1), m.group(1)), html)

    OUT.write_text(html, encoding="utf-8")
    print("wrote %s (%.0f KB)" % (OUT, OUT.stat().st_size / 1024))


if __name__ == "__main__":
    main()
