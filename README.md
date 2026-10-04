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

GitHub Pages cannot issue redirects, so if the old WordPress URLs matter for
search rankings, either put the site behind something that can redirect
(Cloudflare and Netlify both do this on free tiers), or add small HTML files at
the old paths that redirect to the new page. `404.html` catches anything missed.

The old paths worth mapping: `/shop`, `/shop/*`, `/sensory-beanbag-information`,
`/weighted-products-information`, `/frequently-asked-questions-faq`,
`/about-julie-hannon`, `/testimonials`, `/agency-testing-approvals`,
`/reference-articles-autism/*`.
