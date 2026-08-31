# Content to confirm with Julie — working notes

The first draft of this site was written without access to sensorybeanbags.com
(the live site was unreachable from the build machine), so the copy was
reconstructed from search-engine results. **It has since been checked against
the live site**, and the prices, dimensions, colours, delivery terms and lead
times below are now taken from sensorybeanbags.com itself rather than guessed.

Two of the reconstructed prices were wrong — Large was shown as €245 against an
actual €225, and X-Large as €280 against €260. Both are now corrected. That is
worth knowing when reading anything else that is still marked unconfirmed.

Anything still unconfirmed is marked in the pages with an orange dashed
`to confirm` chip, so it is obvious on screen. Search the built HTML for
`class="tbd"` to find them all. Once a value is filled in, delete the
`<span class="tbd">…</span>` wrapper; when they are all gone, delete the
`.tbd` rule at the bottom of `assets/css/site.css`.

## 0. What Julie sees

**Do not send her this file.** It is working notes — it assumes you can open a
Markdown file and read talk of build scripts and CSS classes.

Her copy is a page on the preview site itself:

    https://nvolfango.github.io/sensorybeanbags/notes.html

Plain English, no jargon, opens in any browser on any phone or laptop, nothing
to download. It carries the same asks as the sections below — photographs, the
two prices that disagree, the discontinued products, the shop question and the
missing policies — written for someone who does not build websites, and it
explains up front that the draft is private and her real site is untouched.

It is not in the site's navigation, so a casual visitor will not find it. Send
her the link directly. Source is `src/pages/notes.html`; keep the two in step
when either changes.

## 1. Still open

- **XXX-Large price.** The shop says **€425**; the price-list page says **€415**.
  The site currently shows €425. Which is right?
- **Colour range.** The price list and the shop dropdowns disagree. The price
  list gives Royal Blue, Purple, Bottle Green, Chocolate Brown, Mid Grey,
  Mid Tan, Wine, Fire Engine Red, Cerise Pink, Turquoise, Emerald Green and
  Orange — that is what the site shows. The shop instead offers Mid Blue and
  Pale Lavender, and omits Mid Grey, Emerald and Orange. Which list is current?
- **Returns / cancellations.** Nothing is stated on the live site either.
  Made-to-order goods are exempt from the usual EU distance-selling cooling-off
  period, but the policy still has to be written down.
- **Safety wording.** "CE approved" is carried over from the old site. Confirm
  what the certification actually covers, and whether fire-retardancy wording
  should appear. There is a Declaration of Conformity dated 2017 on the old
  site that has not been carried across.
- **Delivery outside Ireland.** Not mentioned anywhere. Northern Ireland, UK?
- **Weighted-product washing instructions.** Still a sensible guess, not
  sourced from the live site.
- **More testimonials.** Only one survived (Tania, on her son Mark). Julie is
  said to have a folder of them.

## 2. Confirmed from the live site

Beanbags (fleece): Medium 24 in / 61 cm €195 · Large 30 in / 76 cm €225 ·
X-Large 36 in / 92 cm €260 · XX-Large 46 in / 117 cm €345 ·
XXX-Large 56 in / 143 cm €425.

Lycra beanbags: made on request by email, Large €250, X-Large €285.

Weighted blankets €170–€330 — Medium 72×92 cm, Large 92×122 cm,
X-Large 102×158 cm, 4–14 lb. Large suits children of about seven and under.
Lap pads €60–€85, 3–6 lb. Snakes €75–€95, 4–6 lb, short/wide or long/narrow.

Delivery €15 by courier anywhere in Ireland, next day after dispatch.
Beanbags five to seven working days to make; custom weighted products around
ten days. Payment by PayPal, bank transfer, or cash on delivery in Cork city.

The spelling is **Julie**, not Julia — confirmed by her own banner,
"A Julie Hannon Original". The first draft had this wrong throughout.

## 3. Photographs

Photographs have been taken from the live site, resized for the web and
committed to `assets/img/`. Her WordPress media library holds **134 items**,
far more than the pages actually use, and the best of them have been pulled in.
They are adequate for review, but they are old — most date from 2011 to 2015 —
and **better originals from Julie would improve the site more than anything
else on this list.**

### The lycra beanbag — still missing, and worth asking about

Nothing in the 134-item media library is identifiably a lycra beanbag. Nothing
is named for it, and the lycra range is described as "new" in an FAQ written
years after the newest beanbag photograph was uploaded.

There are a few shiny turquoise and blue beanbags in the older group shots that
could plausibly be lycra, but they date from 2011–2013 and calling one lycra
would be a guess. Since lycra is a *cooling, slippery* fabric sold precisely on
how different it feels from fleece, a photo of the wrong fabric is worse than
no photo. The placeholder stays until Julie sends one.

**This is the single most useful photograph she could take** — it is the only
product on the site with nothing to show for it.

### Also still missing

- **A photograph of Julie.** There is none anywhere on the old site.

### Products the rebuild does not cover

The media library shows two products that appear nowhere in this rebuild, and
neither is in the current shop either:

- **Mini beanbags** and **small hand beanbags** — small, textured, clearly a
  distinct product.
- A **Small** beanbag size, below the Medium the price list starts at.

Are these discontinued, or just never carried over? If she still makes them,
they need a place on the site.

### Other things in the library worth a decision

- A **CE mark** graphic and a signed **Declaration of Conformity** dated 2017.
  The site claims "CE approved" in the footer with nothing to back it — if that
  claim stays, the certificate should probably be visible.
- **Older fleece swatches** from 2015 including a camouflage "Jungle" print,
  which is not in the colour list the site currently shows.
- Scanned **price lists from 2014 and 2015**, useful only as history.

### Adding a photograph

```html
<img src="assets/img/beanbag-large.jpg"
     alt="A child lying back in a large purple fleece sensory beanbag"
     width="1200" height="900" loading="lazy">
```

Write real alt text — many visitors to this site use screen readers or have
children who do. The photographs carried over show an identifiable child; they
were already public on the live site, but if any new photograph shows an
identifiable child, get the parent's written permission first.

## 4. The shop — questions for Julie

The live site is **WooCommerce** and has a working cart, taking PayPal, bank
transfer and cash on delivery in Cork city. This rebuild dropped the checkout
and says to order by phone or email. That was a guess made when the live site
could not be read, and it is not a decision to make on her behalf.

Nothing here blocks the preview. These are questions to put to her along with
her feedback on the design:

- **Has anyone actually checked out through the website?** Roughly how many
  orders a year come through the cart, versus phone and email? This is the
  number that decides everything else.
- **Would she miss it?** Every product is made to order in a chosen size,
  weight and colour, which is a conversation more than a transaction. If she is
  already having that conversation on the phone, the cart may be doing very
  little.
- **If she wants a checkout, can it be replaced wholesale?** Stripe (or a
  similar provider) can take over payments entirely. Card details would never
  touch her site, and beanbags map cleanly onto it because the price depends
  only on size — colour comes free. Weighted products are fiddlier, because the
  price moves on a size-by-weight grid.
- **What does she pay today?** PayPal fees are already coming out of every cart
  order, so moving to another provider is a fee swap rather than a new cost.

Worth knowing while she thinks about it: none of the options require this site
to be private, and none of them require moving off free hosting. The simplest
route adds no running cost at all beyond the transaction fee.

## 5. Legal

There is no privacy or cookie policy, because the site sets no cookies, runs no
analytics and has no forms — nothing is collected. If analytics, a contact form
or a checkout is ever added, a privacy policy becomes necessary.

## 6. Before going live

- [ ] Get Julie's answers on the shop, section 4, and decide from there
- [ ] Delete `robots.txt` (it currently blocks all indexing — correct for a preview, wrong for the real site)
- [ ] Remove the `noindex` meta tag from `tools/build.py`, then rebuild
- [ ] Update `BASE_URL` in `tools/build.py` to the real domain
- [ ] Update the paths in `404.html` (they assume the `/sensorybeanbags/` preview subdirectory)
- [ ] Set up redirects from the old WordPress URLs — see `README.md`
