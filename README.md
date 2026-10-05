# Sensory Beanbags — static site

A static rebuild of [sensorybeanbags.com](https://sensorybeanbags.com), replacing
the WordPress site. Plain HTML and CSS: no framework, no build tooling required
to deploy, no database, no server-side code, nothing to keep patched.

**This is a draft for review.** Read `CONTENT-TO-CONFIRM.md` before showing it
to anyone. Prices, dimensions, colours, delivery terms and photographs have been
checked against the live site and corrected, but a handful of things still need
Julie's confirmation — and the rebuild drops the WooCommerce checkout the live
site has, which is a decision she has to make rather than a detail.

## What changed from the old site

The old site had around fourteen pages, several of which covered the same ground.
This one has five, each with a clear job:

| Page | Replaces |
|---|---|
| `index.html` | Home |
| `beanbags.html` | Shop, individual product pages, Sensory Beanbag Information |
| `weighted.html` | Weighted Products Information |
| `about.html` | About Julie, Testimonials |
| `order.html` | FAQ, ordering and delivery information |
| `schools.html` | New in October 2026 — the two-week trial for schools and professionals in Cork; no old-site equivalent |

Dropped: the four long "reference articles on autism" pages. They read as search
filler rather than something a buyer needs, and the genuinely useful parts (how
children actually use the beanbags, how to pick a weight) were folded into the
product pages instead.

Other changes:

- **Phone number and email on every page**, tapping to call on a phone.
- **One clear route to ordering.** Ordering was always really by phone or email,
  so the site now says that plainly instead of implying a checkout that fights you.
- **A real size guide** with dimensions and prices side by side — the first thing
  anyone wants and previously spread across several pages.
- **Weight guidance for the weighted products** on the page itself, with a note
  to check with an occupational therapist.
- **Accessible.** WCAG AA contrast in light and dark themes (verified), keyboard
  navigable, skip link, correct heading order, landmarks, screen-reader friendly
  tables. The audience includes disabled visitors and this matters more than usual.
- **Fast.** No WordPress, no jQuery, no external requests, no cookies, no tracking.
  Each page is a single HTML file plus one shared stylesheet.
- **Mobile first.** The size table restacks into cards on small screens so the
  price never hides behind a sideways scroll.
- **Dark mode**, following the visitor's system setting by default, with a
  light / auto / dark switch in the header that is remembered per browser.

## Editing it

Page content lives in `src/pages/*.html`. Each file is the body of one page plus
a small metadata block at the top for its title and description. The shared
header, footer, navigation and contact panel live in `tools/build.py`.

After editing anything in `src/pages/` or the chrome in `tools/build.py`:

```bash
python3 tools/build.py
```

That regenerates the `.html` files at the repository root, which are what get
served. Python 3 with no packages installed is all it needs.

The built HTML is committed, so **deployment never runs the build script** — if
you only need a one-off text change and Python is inconvenient, editing the
built `.html` directly works fine. Just make the same change in `src/pages/` or
the next build will overwrite it.

To preview locally:

```bash
python3 -m http.server 8000
```

## Layout

```
index.html, beanbags.html, …   built pages — these are what get served
404.html                       not-found page
robots.txt                     blocks indexing (PREVIEW ONLY — delete before launch)
assets/css/site.css            the entire stylesheet
assets/js/site.js              mobile menu toggle, and nothing else
assets/img/                    product photographs — see assets/img/README.md
assets/docs/                   the 2017 safety test reports, linked from the FAQ
src/pages/                     page content, edit these
tools/build.py                 wraps page content in the shared header and footer
tools/mirror_legacy.py         copies the old WordPress site into legacy/
tools/redirects.py             forwarding pages for the old addresses (run by build.py)
legacy/                        archived copy of the old site, served at /legacy/
redirects/                     generated; deployed to the site root, not to /redirects/
.github/workflows/pages.yml    deploys to GitHub Pages on push to main
```

## Hosting

Currently on GitHub Pages, free, deployed by GitHub Actions on every push to
`main`. Suitable for the live site too — GitHub Pages serves a custom domain
over HTTPS at no cost.

To point sensorybeanbags.com at it later:

1. Work through the "Before going live" checklist in `CONTENT-TO-CONFIRM.md`.
2. Add a `CNAME` file at the repository root containing `sensorybeanbags.com`.
3. At the domain registrar, point the apex `A` records at GitHub's addresses
   (`185.199.108.153`, `.109.153`, `.110.153`, `.111.153`) and `www` at
   `<user>.github.io`.
4. Enable "Enforce HTTPS" in the repository's Pages settings.

### Old URLs

GitHub Pages cannot send real redirects, so every old WordPress address gets a
small forwarding page instead, in `redirects/` (the deploy copies it to the
site root): `redirects/about-julie-hannon/index.html` is served at
`/about-julie-hannon/` and sends the visitor straight to `about.html`.
`tools/build.py` regenerates them, so there is nothing to maintain by hand.

Where they go is set in `tools/redirects.py`. The old addresses already known
— `/shop`, `/sensory-beanbag-information`, `/weighted-products-information`,
`/frequently-asked-questions-faq`, `/agency-testing-approvals`,
`/about-julie-hannon`, `/testimonials`, and the cart, checkout and account
pages — go to their new equivalents. Once `legacy/` exists, every page in it
gets a forwarding page as well: shop and product pages go to the beanbags or
weighted products page, depending on the product, and pages the new site has
no equivalent for, such as the reference articles, go to their archived copy.
`404.html` catches anything else.

## The old website, kept as a backup

`legacy/` holds a static copy of the old WordPress site, served at `/legacy/`
with every page at its original path: `sensorybeanbags.com/about-julie-hannon/`
is kept as `sensorybeanbags.com/legacy/about-julie-hannon/`, and links between
old pages stay inside `/legacy/`. To make or refresh it:

```bash
python3 tools/mirror_legacy.py
```

It reads the live WordPress site, so **run it before the domain moves** — after
that, sensorybeanbags.com answers with the new site. It replaces `legacy/`
completely each time, then checks every link inside the copy and prints any
that are broken. Commit `legacy/` afterwards; the deploy picks it up.

What it does and does not keep:

- Pages, images (every size in `srcset`), stylesheets, scripts, fonts and the
  PDFs and documents the pages link to. Files from other hosts, such as web
  fonts, go under `legacy/_ext/<host>/`.
- Not the cart, checkout, account pages, search or feeds: they only worked
  with WordPress running. Links to them lead to `legacy/_unavailable.html`.
  Forms, including add-to-cart buttons, do nothing.
- Each page gets `noindex`, so search engines never rank the archive above the
  new site, and a one-line banner linking to the new site
  (`--no-banner` leaves it out). Do not block `/legacy/` in `robots.txt`:
  search engines have to be able to fetch a page to see its `noindex`.
