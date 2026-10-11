/*
 * Tests for the checkout function, with PayPal stood in for by mock-paypal.mjs.
 *
 *   node --test tests/
 */
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { pathToFileURL } from "node:url";
import { startMockPayPal } from "./mock-paypal.mjs";

const ROOT = new URL("../", import.meta.url);
const catalogue = JSON.parse(await readFile(new URL("assets/data/catalogue.json", ROOT), "utf8"));
const checkout = await import(pathToFileURL(new URL("functions/api/checkout/[[path]].js", ROOT).pathname).href);

let mock;
before(async () => { mock = await startMockPayPal(); });
after(async () => { await mock.close(); });

function env(overrides) {
  return Object.assign({
    PAYPAL_ENV: "sandbox",
    PAYPAL_CLIENT_ID: "test-client-id",
    PAYPAL_CLIENT_SECRET: "test-secret",
    PAYPAL_API_BASE: mock.base,
    ASSETS: { fetch: async () => new Response(JSON.stringify(catalogue), { headers: { "content-type": "application/json" } }) },
  }, overrides || {});
}

async function call(method, path, body, overrides) {
  const request = new Request("https://sensorybeanbags.com/api/checkout/" + path, {
    method,
    headers: body ? { "content-type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  const res = await checkout.onRequest({ request, env: env(overrides), params: { path: path.split("/") } });
  return { status: res.status, data: await res.json() };
}

const basket = { items: [{ sku: "fleece-large", colour: "Royal Blue", qty: 1 }, { sku: "fleece-medium", colour: "Wine", qty: 2 }], delivery: "courier" };

test("priceBasket charges catalogue prices and per-beanbag courier delivery", () => {
  const priced = checkout.priceBasket(catalogue, basket);
  assert.equal(priced.itemTotal, 225 + 2 * 195);
  assert.equal(priced.deliveryTotal, 3 * 15);
  assert.equal(priced.total, 615 + 45);
  assert.equal(priced.count, 3);
});

test("priceBasket makes Cork city delivery free and merges duplicate lines", () => {
  const priced = checkout.priceBasket(catalogue, {
    items: [{ sku: "fleece-large", colour: "Royal Blue", qty: 1 }, { sku: "fleece-large", colour: "Royal Blue", qty: 1 }],
    delivery: "cork",
  });
  assert.equal(priced.lines.length, 1);
  assert.equal(priced.lines[0].qty, 2);
  assert.equal(priced.deliveryTotal, 0);
  assert.equal(priced.total, 450);
});

test("priceBasket refuses unknown products, colours, quantities and delivery", () => {
  const bad = (body) => assert.throws(() => checkout.priceBasket(catalogue, body), (e) => e.status === 400);
  bad({ items: [{ sku: "fleece-large", colour: "Royal Blue", qty: 1 }], delivery: "post" });
  bad({ items: [], delivery: "courier" });
  bad({ items: [{ sku: "lycra-large", colour: "Royal Blue", qty: 1 }], delivery: "courier" });
  bad({ items: [{ sku: "fleece-large", colour: "Neon", qty: 1 }], delivery: "courier" });
  bad({ items: [{ sku: "fleece-large", colour: "Royal Blue", qty: 0 }], delivery: "courier" });
  bad({ items: [{ sku: "fleece-large", colour: "Royal Blue", qty: 11 }], delivery: "courier" });
  bad({ items: [{ sku: "fleece-large", colour: "Royal Blue", qty: 1.5 }], delivery: "courier" });
  bad({ items: [{ sku: "fleece-large", colour: "Royal Blue", qty: "1; drop" }], delivery: "courier" });
});

test("orderPayload adds up and names the colour on every item", () => {
  const payload = checkout.orderPayload(checkout.priceBasket(catalogue, basket), catalogue);
  const unit = payload.purchase_units[0];
  assert.equal(payload.intent, "CAPTURE");
  assert.equal(unit.amount.value, "660.00");
  assert.equal(unit.amount.currency_code, "EUR");
  assert.equal(unit.amount.breakdown.item_total.value, "615.00");
  assert.equal(unit.amount.breakdown.shipping.value, "45.00");
  assert.equal(unit.custom_id, "delivery=courier");
  assert.deepEqual(unit.items.map((i) => i.name), ["Large fleece sensory beanbag, Royal Blue", "Medium fleece sensory beanbag, Wine"]);
  assert.deepEqual(unit.items.map((i) => i.quantity), ["1", "2"]);
  assert.ok(unit.items.every((i) => i.category === "PHYSICAL_GOODS"));
  assert.ok(unit.description.length <= 127);
});

test("inCountyCork recognises Cork by name or Eircode and nothing else", () => {
  assert.ok(checkout.inCountyCork({ admin_area_1: "Co. Cork" }));
  assert.ok(checkout.inCountyCork({ admin_area_2: "Cork" }));
  assert.ok(checkout.inCountyCork({ postal_code: "T12 X5Y6" }));
  assert.ok(checkout.inCountyCork({ postal_code: "p31ab12" }));
  assert.ok(!checkout.inCountyCork({ admin_area_1: "Co. Dublin", postal_code: "D04 X1Y2" }));
  assert.ok(!checkout.inCountyCork({ admin_area_2: "Corkagh Park Road" }));
  assert.ok(!checkout.inCountyCork({}));
});

test("config says when PayPal is not set up, and what the page needs when it is", async () => {
  let r = await call("GET", "config", null, { PAYPAL_CLIENT_SECRET: "" });
  assert.equal(r.status, 503);
  assert.equal(r.data.error, "NOT_CONFIGURED");
  r = await call("GET", "config", null, { PAYPAL_ENV: "production" });
  assert.equal(r.status, 503);
  r = await call("GET", "config");
  assert.equal(r.status, 200);
  assert.deepEqual(r.data, { clientId: "test-client-id", currency: "EUR", env: "sandbox" });
});

test("unknown paths and methods are refused", async () => {
  assert.equal((await call("GET", "orders")).status, 404);
  assert.equal((await call("POST", "config")).status, 404);
  assert.equal((await call("POST", "orders/ORDER00001/refund")).status, 404);
  assert.equal((await call("POST", "orders/../x/capture")).status, 404);
});

test("a full payment: create, approve in Ireland, capture", async () => {
  const created = await call("POST", "orders", basket);
  assert.equal(created.status, 201);
  assert.match(created.data.id, /^ORDER\d+$/);
  assert.equal(created.data.total, 660);

  const sent = mock.calls.find((c) => c.path === "/v2/checkout/orders");
  assert.equal(sent.body.purchase_units[0].amount.value, "660.00");
  assert.ok(sent.headers["paypal-request-id"]);
  assert.equal(sent.headers.authorization, "Bearer TEST-TOKEN");

  const notYet = await call("POST", "orders/" + created.data.id + "/capture");
  assert.equal(notYet.status, 409);
  assert.equal(notYet.data.error, "ORDER_NOT_APPROVED");

  await fetch(mock.base + "/__test/approve/" + created.data.id, { method: "POST" });
  const captured = await call("POST", "orders/" + created.data.id + "/capture");
  assert.equal(captured.status, 200);
  assert.equal(captured.data.status, "COMPLETED");
  assert.equal(captured.data.captureStatus, "COMPLETED");
  assert.equal(captured.data.reference, created.data.id);
  assert.equal(captured.data.amount.value, "660.00");
  assert.equal(captured.data.payer.name, "Test Buyer");
  assert.deepEqual(captured.data.deliverTo.lines, ["1 Main Street", "Douglas", "Co. Cork", "T12 AB12", "IE"]);
  assert.equal(captured.data.items.length, 2);
  assert.equal(captured.data.items[1].quantity, 2);

  const again = await call("POST", "orders/" + created.data.id + "/capture");
  assert.equal(again.status, 200, "capturing twice is harmless");
  assert.equal(again.data.status, "COMPLETED");
});

test("an address outside Ireland is not charged", async () => {
  const created = await call("POST", "orders", basket);
  await fetch(mock.base + "/__test/approve/" + created.data.id, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ address: { address_line_1: "1 High St", admin_area_2: "Belfast", postal_code: "BT1 1AA", country_code: "GB" } }),
  });
  const r = await call("POST", "orders/" + created.data.id + "/capture");
  assert.equal(r.status, 409);
  assert.equal(r.data.error, "OUTSIDE_IRELAND");
  assert.equal(mock.orders.get(created.data.id).status, "APPROVED", "never captured");
});

test("free Cork delivery to a Dublin address is not charged; to Cork it is", async () => {
  const cork = { ...basket, delivery: "cork" };
  let created = await call("POST", "orders", cork);
  assert.equal(created.data.total, 615);
  await fetch(mock.base + "/__test/approve/" + created.data.id, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ address: { address_line_1: "2 Quay", admin_area_2: "Dublin 2", admin_area_1: "Co. Dublin", postal_code: "D02 AB12", country_code: "IE" } }),
  });
  let r = await call("POST", "orders/" + created.data.id + "/capture");
  assert.equal(r.status, 409);
  assert.equal(r.data.error, "NOT_CORK");

  created = await call("POST", "orders", cork);
  await fetch(mock.base + "/__test/approve/" + created.data.id, { method: "POST" });
  r = await call("POST", "orders/" + created.data.id + "/capture");
  assert.equal(r.status, 200);
  assert.equal(r.data.amount.value, "615.00");
});

test("a declined card is reported so the buyer can try another", async () => {
  const created = await call("POST", "orders", basket);
  await fetch(mock.base + "/__test/approve/" + created.data.id, {
    method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ decline: true }),
  });
  const r = await call("POST", "orders/" + created.data.id + "/capture");
  assert.equal(r.status, 422);
  assert.equal(r.data.error, "INSTRUMENT_DECLINED");
});

test("bad baskets never reach PayPal", async () => {
  const before = mock.calls.length;
  let r = await call("POST", "orders", { items: [{ sku: "fleece-large", colour: "Royal Blue", qty: 99 }], delivery: "courier" });
  assert.equal(r.status, 400);
  r = await call("POST", "orders", null);
  assert.equal(r.status, 400);
  const request = new Request("https://sensorybeanbags.com/api/checkout/orders", { method: "POST", body: "{not json" });
  const res = await checkout.onRequest({ request, env: env(), params: { path: ["orders"] } });
  assert.equal(res.status, 400);
  assert.equal(mock.calls.length, before, "no PayPal calls were made");
});

test("an unknown order id is a 404, and PayPal being down is a 502 with nothing charged", async () => {
  let r = await call("POST", "orders/NOSUCHORDER/capture");
  assert.equal(r.status, 404);
  r = await call("POST", "orders", basket, { PAYPAL_API_BASE: "http://127.0.0.1:1", PAYPAL_CLIENT_ID: "other-id" });
  assert.ok(r.status === 500 || r.status === 502);
  assert.match(r.data.message, /charged/);
});
