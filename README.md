# Sensory Beanbags — static site

A static rebuild of [sensorybeanbags.com](https://sensorybeanbags.com), replacing
the WordPress site. Plain HTML and CSS: no framework, no build tooling required
to deploy, no database, and the only server-side code is one small function
behind the PayPal checkout (see "Online checkout" below).

**This is a draft for review.** Read `CONTENT-TO-CONFIRM.md` before showing it
to anyone. Prices, dimensions, colours, delivery terms and photographs have been
checked against the live site and corrected, but a handful of things still need
Julie's confirmation. The online checkout the old site had is back, through
Julie's existing PayPal account, but it stays switched off until her PayPal
credentials are in place.

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
| `cart.html` | The WooCommerce cart and checkout — a basket for fleece beanbags, paid through PayPal |
| `privacy.html` | Privacy policy — short, and true |

Dropped: the four long "reference articles on autism" pages. They read as search
filler rather than something a buyer needs, and the genuinely useful parts (how
children actually use the beanbags, how to pick a weight) were folded into the
product pages instead.

Other changes:

- **Phone number and email on every page**, tapping to call on a phone.
- **Ordering online, simply.** Fleece beanbags can be ordered and paid for
  online by card or PayPal, as on the old site, but through a small basket
  under the size table instead of a WooCommerce shop. Everything else — lycra,
  weighted products, school orders — is ordered by phone or email, which is how
  most orders happen anyway. See "Online checkout" below.
- **A real size guide** with dimensions and prices side by side — the first thing
  anyone wants and previously spread across several pages.
- **Weight guidance for the weighted products** on the page itself, with a note
  to check with an occupational therapist.
- **Accessible.** WCAG AA contrast in light and dark themes (verified), keyboard
  navigable, skip link, correct heading order, landmarks, screen-reader friendly
  tables. The audience includes disabled visitors and this matters more than usual.
- **Fast.** No WordPress, no jQuery, no cookies, no tracking, and no external
  requests except PayPal's script on the basket page. Each page is a single
  HTML file plus one shared stylesheet.
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
robots.txt                     lets search engines in (the preview gets one that shuts them out)
assets/css/site.css            the entire stylesheet
assets/js/site.js              mobile menu toggle and theme switch, and nothing else
assets/js/shop.js              the basket: the order form, the basket page and PayPal's buttons
assets/data/catalogue.json     prices, sizes, colours and the delivery charge for the online shop
assets/img/                    product photographs — see assets/img/README.md
assets/docs/                   the 2017 safety test reports, linked from the FAQ
functions/api/checkout/        the Cloudflare Pages Function behind the checkout (deployed by Cloudflare, not copied to dist/)
tests/                         tests for that function, with a stand-in for PayPal
src/pages/                     page content, edit these
tools/build.py                 wraps page content in the shared header and footer, fills the order form from the catalogue
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
   `3.11`. The checkout's PayPal variables go in the same place; see
   "Online checkout" below.
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
8. **Transfer the registration** to Cloudflare Registrar any time after the
   domain shows as Active in Cloudflare — no need to wait for go-live or for
   the renewal date: the time left carries over and the transfer adds a year.
   At Netfronts turn off Registrar Lock and use Get EPP Code (it goes to the
   account holder's email); in Cloudflare, Domain Registration → Transfer
   Domains, enter the code, and give **Julie's details as the registrant
   contact** — that is what makes the domain legally hers. The fee is a
   year's renewal on the account's card, so add Julie's card first. Netfronts
   may email her to approve; otherwise it completes in about five days. Do
   not change the owner details at Netfronts beforehand (that can lock the
   domain against transfer for 60 days), keep Auto Renew on there until the
   transfer is done, and renew first if expiry is within a couple of weeks.
9. Once the new site is live and settled, cancel the Netfronts hosting and
   delete the DNS records that still point at its server. GitHub Pages can
   stay as a private preview: `tools/dist.py github` keeps every page of it
   out of search engines.

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

## Online checkout

Fleece beanbags can be ordered and paid for on the site, by PayPal or by debit
or credit card through PayPal's guest checkout, using Julie's existing PayPal
business account — the same account the old shop paid into. Lycra beanbags and
weighted products stay as they were: ordered through Julie by phone or email.

How it works:

- `beanbags.html` has an "Order a fleece beanbag online" form under the size
  table: size, colour, quantity, "Add to basket". The basket is kept in the
  visitor's browser (`localStorage`), and a "Basket" link in the header shows
  how many beanbags are in it.
- `cart.html` lists the basket, offers two delivery choices (courier or An
  Post at €15 per beanbag, or free delivery in Cork city) and shows PayPal's
  buttons. PayPal collects the delivery address. After payment the page shows
  a thank-you with the PayPal reference; PayPal emails the buyer a receipt and
  Julie a "payment received" notice listing the items, colours and address.
  There is no other order record: Julie works from PayPal, as she did before.
  Refunds are done in PayPal too (Activity → the payment → Refund).
- `functions/api/checkout/[[path]].js` is a Cloudflare Pages Function. The
  browser sends it the basket (sizes, colours, quantities, delivery choice);
  it prices the basket from `assets/data/catalogue.json`, creates the PayPal
  order, and later captures the payment. The amount is never taken from the
  browser, so nobody can change a price by editing the page. Before taking the
  money it checks the address PayPal collected: Ireland only, and County Cork
  when free Cork delivery was chosen; otherwise the buyer is told and nothing
  is charged.
- `assets/data/catalogue.json` is the one place the shop's prices, sizes,
  colours and delivery charge live. `tools/build.py` fills the order form from
  it and refuses to build if a price in the hand-written size table disagrees.
  `assets/js/shop.js` does the browser side.

The GitHub Pages preview has no functions, so there the basket works but the
pay box says online payment is not switched on and offers to email the order
to Julie instead. Cloudflare's own preview deployments (one per branch) run
the function with the Preview environment's variables, so a branch can be
tried against PayPal's sandbox before it reaches `main`.

### Switching it on (once)

1. **PayPal credentials.** Log in at <https://developer.paypal.com/dashboard/>
   with Julie's PayPal account. It has to be a Business account (the old shop
   needed one too; upgrading a personal account is free, under Account
   Settings). Go to Apps & Credentials, switch the toggle to **Live**, and
   either open the Default Application or Create App (name it "Sensory
   Beanbags website"; if asked for a type, Merchant). Copy the **Client ID**
   and the **Secret**. For testing first, do the same under **Sandbox**: the
   dashboard also provides a sandbox business account to receive with and a
   sandbox personal account to pay with (Testing Tools → Sandbox Accounts).
2. **Guest card payments.** In Julie's PayPal account: Account Settings →
   Website payments → Website preferences → **PayPal account optional: On**.
   That is what puts the "Debit or Credit Card" button on the page. While
   there, check that payment notification emails are on, so she hears about
   every order.
3. **Cloudflare.** Workers & Pages → the project → Settings → Variables and
   Secrets. For **Production**: `PAYPAL_ENV` = `live`, `PAYPAL_CLIENT_ID` = the
   live client ID, `PAYPAL_CLIENT_SECRET` = the live secret, marked as a secret.
   For **Preview**: the same three with `sandbox` and the sandbox app's
   values, so branch previews never take real money. Variables apply to the
   next deployment, so redeploy afterwards (Deployments → Retry deployment).
4. **Check.** `https://sensorybeanbags.com/api/checkout/config` should answer
   with the client ID and `"env": "live"`; if it says `NOT_CONFIGURED`, a
   variable is missing or `PAYPAL_ENV` is not exactly `live` or `sandbox`.
   Then make one real order for a Medium beanbag and refund it from PayPal, to
   see the whole thing end to end, including what lands in Julie's inbox.

### Changing prices, colours or the delivery charge

Edit `assets/data/catalogue.json` — the `price` and `delivery` figures on each
size, and the `colours` list — and change the matching figure in the size
table in `src/pages/beanbags.html`, then run `python3 tools/build.py`. The
function reads the same file from the deployed site, so there is nothing else
to change.

### Running the checkout locally

```bash
python3 tools/build.py && python3 tools/dist.py cloudflare
npx wrangler pages dev dist --port 8788 \
  -b PAYPAL_ENV=sandbox -b PAYPAL_CLIENT_ID=... -b PAYPAL_CLIENT_SECRET=...
```

Those three can go in a `.dev.vars` file instead (git-ignored). Then
<http://localhost:8788/cart> shows the real PayPal sandbox buttons, paid with a
sandbox personal account. The function's own tests stand in for PayPal and
need no credentials:

```bash
node --test tests/checkout.test.mjs
```

They also run in the GitHub workflow before every preview deploy.

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
