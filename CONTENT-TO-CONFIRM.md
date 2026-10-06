# Content to confirm with Julie — working notes

Round one of Julie's feedback arrived on 2 September 2026 as a Word document
(`Sensory Beanbags that help children settle.docx` in the repository root).
Round two arrived on 4 October 2026 as a PDF (`Natan_response_Round_2.pdf`,
also in the root): change requests in red, answers to the round-one questions,
and new photographs, all applied the same day. This file records what is
still open and the answers that were applied, so nobody re-asks them.

The `to confirm` chips and the `.tbd` CSS rule are gone: nothing on the site is
marked unconfirmed any more.

## 0. What Julie sees

**Do not send her this file.** It is working notes.

Her copy is a page on the preview site itself:

    https://nvolfango.github.io/sensorybeanbags/notes.html

It now reads as a "Round three" page: what changed from her answers, and the
short list of things still open. Not in the navigation; send her the link
directly. Source is `src/pages/notes.html`; keep it in step with this file.

## 1. Still open

- **Google review button.** She asked for a "Google Review link button". No
  Google Business listing / review link exists yet (or none was sent). The
  button cannot go on without the URL; when it arrives, put it on `about.html`
  beside the testimonials and on `schools.html`.
- **Logo.** Round two: the sample image she has is the same unusable screen
  photo; she will follow up with the designer for the correct file, "but I can
  leave it for now". Parked. The possible "Sensory Beanbags + More" rename
  question is parked with it.
- **Guarantee: 12 or 15 years.** Her answer: "Can't decide whether to put 12
  or 15. In reality they haven't broken in 21 years… whichever sounds
  believable." Her own home-page paragraph says 12, so **12 is on the site**.
  She may still switch to 15.
- **Lycra price figures.** Round two: "15 euro more instead of 20 euro on
  large and xlarge." Read as fleece price + €15, so Large €240 and X-Large
  €275 are on the site (was €250 / €285 from the old site). Flagged on the
  notes page for her to confirm the two figures.
- **School reference wording.** The reference is on `schools.html` in full,
  signed Maureen Lucey, Clonakilty Community College, April 2026, as she sent
  it. (Her "Naming the school: leave it out" answered the Douglas Boys
  hall-photo question, not this.) The teacher wrote "Sensory Products" twice;
  both read "[Sensory Beanbags]". Open: brackets, word for word, or ask Maureen.
- **"Best used for" row.** Her round-two lines ("gentle gradual sink-in",
  "flops" / "instant deep sink-in") were added in front of the existing row
  text. She may have meant them to replace it; if so the order-page FAQ on
  fleece vs lycra should follow.
- **Swatch offer.** She wrote "5 fabric swatches for $5"; the site says €5.
  How to order them, whether postage is included and whether the €5 comes off
  a later order are not stated; the note on `beanbags.html` says none of it.
- **Sizes for the new lap pad photo.** Pink 108 × 21 cm, 5 lb; turquoise
  lycra/fleece 90 × 19 cm, 4 lb. Not shown anywhere: the home card has no
  caption, and the lap pad card keeps her page-nine "roughly 90 cm long to
  15–20 wide". Could be a "Pictured: …" line on the card.
- **Held-back photos.** Three of her "more photos" are not used (see
  section 4). She left it to us.
- **Northern Ireland.** Unchanged from round one: the site says "within
  Ireland only"; whether that means the island or the Republic is unconfirmed.
- **Weighted blanket CE.** Unchanged from round one and not answered in round
  two: was the weighted blanket technical file ever completed? The footer says
  "CE approved" on every page; the Declaration covers beanbags.
- **Returns wording.** Unchanged: the cancellation sentence on `order.html`
  ("get in touch as soon as you can") is ours, not hers.
- **Card payments: dropped for now (October 2026).** Nathan: forget Stripe;
  Julie sorts payment out with customers by bank transfer. The site keeps
  listing Revolut, bank transfer, cash on delivery in Cork, and invoicing for
  schools (ETB registered). No online checkout. If card payments come back:
  Julie could not get past Stripe's verification, and the business must not be
  run through Nathan's own Stripe account — Stripe requires the account holder
  to be the business being paid, and pays out only to a bank account in that
  holder's name. The fee comparison in the round-two document still stands.
- **Shop shape, decided October 2026.** Every order goes through Julie: the
  customer emails or calls, she agrees size, colour, weight and price, then
  sends payment details. `weighted.html` has an "Email Julie to order" button
  with a pre-filled email listing what she needs for a weighted product. If an
  online checkout is ever wanted, it would be for beanbags only (a cart with
  Stripe Checkout behind a small Cloudflare function); weighted products stay
  with Julie.
- **Hosting, decided October 2026:** Cloudflare — Pages for the site, DNS,
  and later the Registrar. Steps in `README.md` under "Hosting". Nathan sets
  up the account and invites Julie as Super Administrator; she pays (her card
  under Billing, in place before the domain transfer) and is the registrant
  contact on the domain.
- **Trial logistics.** The schools page says Julie calls back after the two
  weeks (her flyer text says "I'll call back in two weeks"). Nothing on the
  page about deposits or collection — if the trial needs conditions, she
  should say.

## 2. Answered (applied)

**From round two (October 2026):**

- Home page h1 helps "children **and adults**" (her ask) and ends "…regulate"
  (Nathan's ask, October 2026 — was "settle").
- "Made one at a time by Julie Hannon **and her team**" — home page lede and
  the About page closing line.
- Her **12-year guarantee paragraph** is the third card on the home page,
  nearly word for word, under her round-one heading "Fleece and lining that
  survive real life" (she said add, so her heading stays). It replaces the
  softer "no rips in years" body text.
- Ordering page lede no longer says "made to order by one person", which
  contradicted "Julie and team".
- About page: "…watching how children use movement and play **to explore
  their physical capabilities and make sense of the world around them**."
- **XXX-Large is €415** (was €425). **Lycra is €15 more than fleece**: Large
  €240, X-Large €275.
- **Delivery is €10–15 depending on weight, by courier or An Post** (her
  answer was headed "Courier/An post") — home, ordering steps, FAQ, schools.
- Comparison table: fleece is "**medium stretch**" (was "limited"); best used
  for now leads with "a gentle, gradual sink-in" + **flops** (fleece) and "an
  instant, deep sink-in" (lycra). See Still open.
- Fleece washing: she said remove the second and third sentences, which were
  "The cover also comes off easily on its own…" and "In an industrial
  machine, put the whole thing in as one piece." They are replaced with her
  two: "the cover is easily removed for washing"; "a Medium beanbag can be
  washed in your washing machine and tumble dried as one unit — the beads
  stay in the bag". ("Beeds… tumble tried" read as beads/dried.) The first
  sentence stays; the fourth now opens "For the larger sizes" so it does not
  contradict the Medium line. Lycra: "wash it on its own" removed; "Unlike
  fleece" (from her own care sheet) kept. Weighted items: "**soaking
  overnight** or hand washing" inserted. The order-page FAQ matches.
- **Forest Green** swatch added (her photo).
- **Fabric sample swatches** offer under the colours: up to five for €5.
- **New page `schools.html`** ("For schools" in the nav): two-week trial for
  schools and professionals in Cork, her trial story (suggested 2025, begun
  spring 2026), calm/focus/regulation bullets, her "I'd love you to try it"
  quote, the new Sinead Moynihan quote, the Clonakilty school reference,
  **Request a quote** / **Request a visit** mailto buttons, **ETB registered**,
  **discounts when you purchase more than one product**. Home page and
  ordering page link to it. Her "I'll call back in two weeks" became "Julie
  calls back" (website voice).
- ETB registered + the multi-product discount are also in the ordering page's
  schools note and "How do I pay?" FAQ.
- **The photo under the title is fine** (child reading a book) — hero stays.
- **Naming the school: leave out** until she makes contact. That answered the
  round-two question about the Douglas Boys hall photo, which stays unnamed.
  It does not cover the Clonakilty reference, which she sent with its
  attribution.
- **Rainbow blanket photo kept** — she offered a replacement (blanket on
  grass) but said keep the rainbow one if better, and it is better.
- **"The picture under weighted blankets laps and snakes"** is the image on
  the home page card of that name (Nathan confirmed, October 2026): it now
  shows her pink/turquoise lap pads with the navy snake, replacing the old
  `weighted-group.jpg`. The lap pad figure on `weighted.html` keeps her
  round-one photo (`lap-pads-fleece-lycra.jpg`), which she did not ask to
  change. The two items are lap pads: her round-one caption for the same kind
  was "4lb lap Lycra/fleece", and she labels snakes as snakes.
- Her new photos: see section 4. Three used, four held back by design.

**From round one (September 2026):**

- XXX-Large is ~~€425~~ (superseded in round two: €415).
- The **colour range** shown (the price-list version) is fine "for now".
- **Mini and small beanbags are discontinued.** Left off.
- **No photo of Julie** on the site. Placeholder removed.
- **Lycra photo**: she sent one (three lycra beanbags in a sensory room),
  plus a turquoise one on artificial grass. Both are in.
- **Snake and lap pad** carry the descriptions from the live shop. Her new
  photos are used (same products as the shop photos, better quality).
- **CE**: she went through the CE process in 2017, sending fabrics to the UK
  for testing. The live site's "Agency Testing / Approvals" page has the
  signed Declaration of Conformity (beanbags, Toy Safety Directive, EN 71-1/2/3)
  and three SATRA test reports (EN 71-2 fire on beanbag and weighted blanket,
  EN 71-3 chemical on fleece and lycra). All four are now in `assets/img/`
  and `assets/docs/` and linked from the safety FAQ.
- **Care and washing**: two PDFs were embedded in her document (lycra beanbag
  care; weighted blanket care). Both applied, lightly shortened.
- **Delivery**: Ireland only. Free in Cork city. €10–15 courier elsewhere.
- **Payment**: Revolut, bank transfer, cash on delivery in Cork city.
- **Testimonials**: the live Testimonials page has around forty. Twelve are
  on `about.html`; the rest can be swapped in on request.
- **Home page copy**: her phrases ("not a pillow", rough and tumble, running
  into it from a distance, jumping from a trampoline or swing, rolling around
  and underneath, hand-made in Cork, matched to each child) are folded in.
  "Clinically designed tool" and "engineered through hundreds of hours" were
  left out as claims that are hard to stand behind; "OT recommended" and
  "used in schools and therapy spaces" are in.
- **Fleece vs lycra comparison**: her table is on `beanbags.html` under the
  two fabric cards. She was unsure whether to have both; both are in, easy to
  remove.
- Business context, for copy decisions: she sells mostly fleece and very few
  lycra; weighted blankets and lap pads; not really to the domestic market.
  Most orders come from OT recommendations and school visits, so customers
  have usually heard of the product before they arrive.

## 3. Confirmed from the live site

Beanbags (fleece): Medium 24 in / 61 cm €195 · Large 30 in / 76 cm €225 ·
X-Large 36 in / 92 cm €260 · XX-Large 46 in / 117 cm €345 ·
XXX-Large 56 in / 143 cm €415 (round two; the live site still says €425).

Lycra beanbags: made on request by email, €15 over the fleece price — Large
€240, X-Large €275 (round two; see open question above).

Weighted blankets €170–€330 — Medium 72×92 cm, Large 92×122 cm,
X-Large 102×158 cm, 4–14 lb. Lap pads €60–€85, 3–6 lb, blue / rainbow check /
request a colour; roughly 90–108 cm long, 15–21 cm wide (her round-two photo
captions: pink long 108 × 21 cm at 5 lb, turquoise lycra/fleece 90 × 19 cm at
4 lb). Snakes €75–€95, 4–6 lb, short/wide or long/narrow, mid grey /
royal blue / rainbow check.

Beanbags five to seven working days to make; custom weighted products around
ten days.

The spelling is **Julie**, not Julia.

## 4. Photographs

`assets/img/README.md` lists what each file is. New from Julie in September
2026: `beanbag-lycra-room.jpg`, `beanbag-lycra-turquoise.jpg`,
`school-hall.jpg` (Douglas Boys school), `beanbag-snake.jpg`,
`lap-pads-fleece-lycra.jpg`, `lap-pad-royal-blue.jpg`. She says she does not
have a great variety; anything more is welcome but nothing is blocking.

New from Julie in October 2026 (embedded in her round-two PDF; extracted with
`pdfimages`): `swatch-forest-green.jpg` (colour range), `lap-pads-snake-group.jpg`
(home page weighted card, replacing `weighted-group.jpg`) and
`sensory-room-lycra.jpg` (`schools.html`). She asked "add if it would benefit
the website or be too much… whatever you think"; four were held back to keep
the pages uncluttered — the blanket on grass (rainbow photo kept instead), the
navy 4 lb lycra/fleece snake, three snakes (pink, spotted, rainbow stripe) on
a green fleece beanbag, and a close-up of a pink snake head on a rainbow-check
body. All are in her PDF if wanted.

Write real alt text — many visitors use screen readers. If any new photograph
shows an identifiable child, get the parent's written permission first.

## 4a. DNS and the domain at Netfronts

- Netfronts hosts the old site (cPanel server `64.92.125.36`) and is the
  domain's registrar. Original nameservers: `dns1.validns.com`,
  `dns2.validns.com` — putting these back at Netfronts undoes the move to
  Cloudflare DNS.
- **No email at @sensorybeanbags.com is used** (Nathan, October 2026). The
  MX, `mail`, SPF, DKIM, SRV and caldav/carddav records Cloudflare imported
  from cPanel are leftovers; delete them with everything else pointing at
  `64.92.125.36` once Netfronts is cancelled. No email routing needed.
- Until go-live, the imported records for `sensorybeanbags.com` and `www`
  stay DNS only (grey cloud) so the old site keeps loading through
  Cloudflare DNS.
- Keep Auto Renew on at Netfronts until the registration is transferred.

## 4b. The old WordPress site

WordPress 5.0 and WooCommerce 3.5 (2018), Twenty Ten theme. Two posts appeared
on it in 2026 by an author "Oliver": "0xc14fa6a5" (13 May) and "0x9a0aa386"
(29 June), each saying only "Testing …" and tagged with its own title. On
software this old that looks like automated probing — something checking it
can publish — rather than anything Julie wrote. They are in the archived copy
as they were (sidebar "Archives: June 2026, May 2026"). Worth checking who
"Oliver" is in the WordPress users, and changing the admin passwords; the site
should be switched off soon after the move rather than left running.

## 5. Legal

There is no privacy or cookie policy, because the site sets no cookies, runs no
analytics and has no forms — nothing is collected. If analytics, a contact form
or a checkout is ever added, a privacy policy becomes necessary, and a payment
provider's own terms will need linking.

## 6. Before going live

- [x] Copy of the old site in `legacy/`, made 5 October 2026 with `python3 tools/mirror_legacy.py --start https://www.sensorybeanbags.com/`: 190 pages, 600 files, 65 MB, no broken links. Only 28 are real pages and 8 products; the rest are pages WordPress makes by itself (83 image pages, 59 shop filter pages, archives). Missing on the old site too, so not copied: `/author`, `/product-information/order-form-2`, two zoom-plugin images. To refresh it, run the same command while the old site is still up.
- [ ] Nathan to browse `/legacy/` on the preview before the domain moves.
- [x] Shop question settled (October 2026): no cart or card payments at launch; orders by phone or email, paid by bank transfer, Revolut or cash on delivery in Cork
- [ ] Settle the logo / "Sensory Beanbags + More" name question
- [x] `robots.txt` now lets search engines in, with a sitemap, and does not block `/legacy/` (those pages carry their own `noindex`, which search engines only see if they can fetch them). The GitHub preview gets a robots file that shuts everything out instead (`tools/dist.py github`).
- [x] `noindex` removed from the built pages; `tools/dist.py github` adds it back to every page of the GitHub preview, so the preview never competes with the real site
- [x] `BASE_URL` is `https://sensorybeanbags.com`; canonical links use Cloudflare's addresses without `.html`
- [ ] Go live: once Cloudflare shows the domain Active and this is on `main`, attach `sensorybeanbags.com` and `www.sensorybeanbags.com` in the Pages project → Custom domains
- [x] Paths in `404.html` assume the `/sensorybeanbags/` preview subdirectory — `tools/dist.py cloudflare` removes the prefix for the live site, so nothing to do
- [x] Forwarding pages from the old WordPress addresses to the new pages — `redirects/`, made by `tools/redirects.py`; see "Old URLs" in `README.md`. Only the ten known addresses until `legacy/` exists; making the copy adds the rest automatically.
