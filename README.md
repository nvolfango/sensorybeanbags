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
tools/dist.py                  puts what each host should publish into dist/
legacy/                        archived copy of the old site, served at /legacy/
redirects/                     generated; deployed to the site root, not to /redirects/
.github/workflows/pages.yml    deploys to GitHub Pages on push to main
```

## Hosting

The **preview** is on GitHub Pages, deployed by GitHub Actions on every push to
`main`. The **live site** will be on Cloudflare (decided October 2026):
Cloudflare Pages for the site, Cloudflare DNS, and later Cloudflare Registrar
for the domain. Cloudflare Pages is free, allows business and e-commerce sites
(GitHub Pages does not), sends real redirects, and can run a small server
function if an online checkout is ever added.

`python3 tools/dist.py github|cloudflare` puts exactly what each host should
publish into `dist/`; the two differ only in how old addresses are redirected
and in the `/sensorybeanbags/` prefix the GitHub preview needs.

Moving to Cloudflare, in this order:

1. Nathan creates the Cloudflare account (free plan) and invites Julie as a
   member with the **Super Administrator** role (Manage Account → Members).
   Once she has joined, she adds her own card under Billing, so the domain is
   paid for by her; this must happen before step 8, because the transfer fee
   includes a year's renewal. Nothing moves when she joins — it is the same
   account with her in it — so Nathan can step back to a lesser role later.
2. Workers & Pages → Create → Pages → Connect to Git, and pick this
   repository. Production branch `main`, framework preset None, build command
   `python3 tools/dist.py cloudflare`, build output directory `dist`. If the
   build cannot find Python, add the environment variable `PYTHON_VERSION` =
   `3.11`.
3. Check the `*.pages.dev` address Cloudflare gives: the pages, an old address
   such as `/about-julie-hannon/` (it should redirect), and `/legacy/`.
4. Move the domain's **DNS** to Cloudflare, which keeps showing the old site.
   Pages will not take `sensorybeanbags.com` until Cloudflare runs its DNS:
   Custom domains → Set up a custom domain → Begin DNS transfer, Free plan.
   Cloudflare imports the existing records. Check them against the list at
   Netfronts — keep every `MX` (email) and `TXT` (verification) record — and
   set the records for `sensorybeanbags.com` and `www` that point at Netfronts
   to **DNS only** (grey cloud), so visitors still reach the old site exactly
   as now. Make sure DNSSEC is off at Netfronts, then change the domain's
   nameservers there to the two Cloudflare gives. When Cloudflare shows the
   domain as Active, check the old site still loads and email still arrives.
5. **While the old site is still showing**, make the copy of it — see "The old
   website, kept as a backup" below.
6. Work through "Before going live" in `CONTENT-TO-CONFIRM.md`.
7. **Go live:** in the Pages project → Custom domains, add
   `sensorybeanbags.com` and `www.sensorybeanbags.com`, letting Cloudflare
   replace the old records that point at Netfronts. Cloudflare sets up HTTPS
   itself, usually within minutes. This, not the nameserver change, is the
   moment the new site replaces the old one.
8. Once the new site is live and settled, cancel the Netfronts hosting, turn
   off GitHub Pages for this repository, and transfer the domain registration
   to Cloudflare Registrar, with **Julie as the registrant contact** — that is
   what makes the domain legally hers. It needs the domain unlocked and a
   transfer code from Netfronts, and is not possible within 60 days of a
   registration or a previous transfer. The site does not change when the
   registration moves. Until then the domain renews at Netfronts.

### Old URLs

On Cloudflare every old WordPress address is a real 301 redirect, from a
`_redirects` file `tools/dist.py` writes. GitHub Pages cannot send real
redirects, so for the preview each old address gets a small forwarding page
instead, in `redirects/` (the deploy copies it to the site root):
`redirects/about-julie-hannon/index.html` is served at `/about-julie-hannon/`
and sends the visitor straight to `about.html`. Both come from the same list,
and `tools/build.py` regenerates them, so there is nothing to maintain by hand.

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
