# Content to confirm with Julie — working notes

Round one of Julie's feedback arrived on 2 September 2026 as a Word document
(`Sensory Beanbags that help children settle.docx` in the repository root).
Everything she answered clearly has been applied. This file records what is
still open and the answers that were applied, so nobody re-asks them.

The `to confirm` chips and the `.tbd` CSS rule are gone: nothing on the site is
marked unconfirmed any more.

## 0. What Julie sees

**Do not send her this file.** It is working notes.

Her copy is a page on the preview site itself:

    https://nvolfango.github.io/sensorybeanbags/notes.html

It now reads as a "Round two" page: what changed from her answers, and the
short list of things still open. Not in the navigation; send her the link
directly. Source is `src/pages/notes.html`; keep it in step with this file.

## 1. Still open

- **Lycra price.** Julie wrote "Lycra beanbags are 20 euro more" and nothing
  else. She does not say more than what: it could be €20 over the fleece price
  (Large €245, X-Large €280) or €20 over the €250 / €285 the live site shows
  (€270 / €305). The site keeps €250 / €285 until she says.
- **Logo.** She sent a photo of a screen showing an "SB+ Sensory Beanbags +
  More" logo. Unusable as-is; the original file is needed. Also unclear
  whether "Sensory Beanbags + More" is a rename — it would change the site
  name in the header, footer, page titles and `tools/build.py`.
- **15-year guarantee.** Her draft home-page copy says "Fleece and lining that
  survives real life 15-year guarantee". Not on the site yet: a guarantee is a
  commitment and its scope needs a sentence from her. The softer, factual line
  (no parent has come back with a rip in years) is on the home page.
- **Courier cost.** She says "10/15 euro courier". The site says "€10–15"
  without saying what decides it (size? distance?).
- **Northern Ireland.** She said "delivery outside of Ireland: not at the
  moment". The site says "within Ireland only". Whether that means the island
  or the Republic is unconfirmed.
- **PayPal.** Her list of ways to pay was "online, cash on delivery, bank
  transfer, Revolut" and she says most people don't use PayPal. PayPal has
  been dropped from the site accordingly. Easy to put back if she wants it.
- **Shopping cart.** She wants one, "more fluid" than WooCommerce, and asked
  about Stripe: pay-as-you-go, is it a lot to set up. This is a conversation
  to have with her, not a page change. Nothing has been built.
- **Google reviews.** She is considering a Google Business listing for reviews
  without showing her address, and has schools she could ask. When it exists,
  link it from the About page.
- **Returns wording.** She said there has never been a return in twenty years
  and corrections were gladly covered, and asked for "the proper way to say
  that". The FAQ on `order.html` is a first draft of that; the cancellation
  sentence ("get in touch as soon as you can") is ours, not hers.
- **Home page photo.** In her document the purple beanbag with the snake sits
  directly under the title "Sensory Beanbags that help children settle",
  labelled "photo". She may have meant it as the home page hero. It is on the
  snake card on `weighted.html`; the hero still uses the old cut-out.
- **Naming the school.** She labelled the hall photo "Douglas Boys school".
  The photo is on the home page but the school is not named. Ask her, and if
  yes, check the school is happy to be named.
- **Weighted blanket CE.** The live "Agency Testing / Approvals" page says the
  weighted blanket technical file was "being assembled" in 2017. The
  Declaration of Conformity covers beanbags only. The footer says "CE
  approved" on every page. Ask whether the blanket file was completed.
- **"Online" as a way to pay.** Her list was "Online or cash on delivery bank
  transfer Revolut". "Online" presumably means card payment through the site,
  which does not exist until the Stripe question is settled.
- **Shop photos.** She asked for the shop's snake and lap pad photos to be
  transferred. Her own newer photos of the same two products are used instead
  (higher quality). The shop originals were downloaded and can be swapped in
  if she prefers them; they are not in the repo.
- **Words of hers left out.** "A clinically designed tool for sensory
  regulation", "engineered through hundreds of hours of design" and "school
  and classroom approved" are not on the site. The first two read as claims
  that would be hard to substantiate; the third is vague. "OT recommended"
  and "targeted sensory input where an ordinary cushion fails" are in.
- **Lap pad dimensions.** From her photo captions: 4 lb is 15 × 90 cm, 6 lb is
  38 × 8.5 in. The site says "roughly 90 cm long and 15–20 cm wide". Worth a
  glance from her.

## 2. Answered (applied)

- XXX-Large is **€425**.
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
XXX-Large 56 in / 143 cm €425.

Lycra beanbags: made on request by email, Large €250, X-Large €285 (see open
question above).

Weighted blankets €170–€330 — Medium 72×92 cm, Large 92×122 cm,
X-Large 102×158 cm, 4–14 lb. Lap pads €60–€85, 3–6 lb, blue / rainbow check /
request a colour. Snakes €75–€95, 4–6 lb, short/wide or long/narrow, mid grey /
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

Write real alt text — many visitors use screen readers. If any new photograph
shows an identifiable child, get the parent's written permission first.

## 5. Legal

There is no privacy or cookie policy, because the site sets no cookies, runs no
analytics and has no forms — nothing is collected. If analytics, a contact form
or a checkout (see the Stripe question) is added, a privacy policy becomes
necessary, and Stripe's own terms will need linking.

## 6. Before going live

- [ ] Settle the shop question with Julie (Stripe or no cart) and decide from there
- [ ] Settle the logo / "Sensory Beanbags + More" name question
- [ ] Delete `robots.txt` (it currently blocks all indexing — correct for a preview, wrong for the real site)
- [ ] Remove the `noindex` meta tag from `tools/build.py`, then rebuild
- [ ] Update `BASE_URL` in `tools/build.py` to the real domain
- [ ] Update the paths in `404.html` (they assume the `/sensorybeanbags/` preview subdirectory)
- [ ] Set up redirects from the old WordPress URLs — see `README.md`. Add `/agency-testing-approvals` to the list; it is now the safety FAQ on `order.html`.
