/*
 * The online checkout: the PayPal side of the basket. Cloudflare Pages runs
 * this at /api/checkout/ on the live site (and on its branch previews); the
 * GitHub Pages preview has no functions, so there the basket page says that
 * online payment is not available.
 *
 *   GET  /api/checkout/config                 -> { clientId, currency, env }
 *   POST /api/checkout/orders                 -> { id }
 *        body: { items: [{ sku, colour, qty }], delivery: "courier" | "cork" }
 *   POST /api/checkout/orders/<id>/capture    -> { status, reference, ... }
 *
 * The browser never says what to charge, only what is in the basket. Prices
 * and delivery come from assets/data/catalogue.json on the deployed site, the
 * same file the pages use, so the amount PayPal takes is worked out here.
 * Before capturing a payment the delivery address PayPal collected is checked:
 * Ireland only, and County Cork when free Cork city delivery was chosen.
 *
 * Settings (Pages project -> Settings -> Variables and secrets; Production for
 * the real site, Preview for branch previews):
 *   PAYPAL_ENV            "live" or "sandbox"
 *   PAYPAL_CLIENT_ID      the REST app's client ID (public: the page loads
 *                         PayPal's script with it)
 *   PAYPAL_CLIENT_SECRET  the REST app's secret (add it as a secret)
 *   PAYPAL_API_BASE       tests only: points the PayPal calls at a stand-in
 */

const CURRENCY = "EUR";
const CATALOGUE_PATH = "/assets/data/catalogue.json";
const API = {
  live: "https://api-m.paypal.com",
  sandbox: "https://api-m.sandbox.paypal.com",
};
const MAX_LINES = 10;
const MAX_BODY_BYTES = 8 * 1024;
const DELIVERY_METHODS = ["courier", "cork"];

class RequestError extends Error {
  constructor(status, code, message) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

export async function onRequest(context) {
  const { request, env } = context;
  const path = (context.params.path || []).join("/");
  const method = request.method.toUpperCase();
  try {
    if (path === "config" && method === "GET") return config(env);
    if (path === "orders" && method === "POST") return await createOrder(request, env);
    const capture = /^orders\/([A-Z0-9]{1,36})\/capture$/.exec(path);
    if (capture && method === "POST") return await captureOrder(capture[1], request, env);
    return reply({ error: "NOT_FOUND", message: "No such checkout endpoint." }, 404);
  } catch (err) {
    if (err instanceof RequestError) {
      return reply({ error: err.code, message: err.message }, err.status);
    }
    console.error("checkout: " + (err && err.stack ? err.stack : err));
    return reply({ error: "SERVER_ERROR", message: "Something went wrong on our side. Nothing has been charged." }, 500);
  }
}

/* --- Settings ------------------------------------------------------------ */

function settings(env) {
  const mode = env.PAYPAL_ENV;
  const id = env.PAYPAL_CLIENT_ID;
  const secret = env.PAYPAL_CLIENT_SECRET;
  if ((mode !== "live" && mode !== "sandbox") || !id || !secret) {
    throw new RequestError(503, "NOT_CONFIGURED", "Online payment is not switched on.");
  }
  return { mode, id, secret, base: env.PAYPAL_API_BASE || API[mode] };
}

function config(env) {
  const s = settings(env);
  return reply({ clientId: s.id, currency: CURRENCY, env: s.mode });
}

/* --- The basket, priced from the catalogue ------------------------------- */

async function catalogue(env, request) {
  const res = await env.ASSETS.fetch(new URL(CATALOGUE_PATH, request.url));
  if (!res.ok) throw new Error("catalogue not found: HTTP " + res.status);
  return res.json();
}

/**
 * Turns { items: [{sku, colour, qty}], delivery } into priced lines and totals,
 * refusing anything that is not in the catalogue. Whole euros throughout.
 */
export function priceBasket(cat, body) {
  if (!body || typeof body !== "object") throw new RequestError(400, "BAD_BASKET", "The basket could not be read.");
  if (!DELIVERY_METHODS.includes(body.delivery)) {
    throw new RequestError(400, "BAD_BASKET", "Choose a delivery option.");
  }
  if (!Array.isArray(body.items) || body.items.length === 0) {
    throw new RequestError(400, "BAD_BASKET", "The basket is empty.");
  }
  if (body.items.length > MAX_LINES) {
    throw new RequestError(400, "BAD_BASKET", "That is more than the basket can take in one order. Please email Julie.");
  }
  const maxQty = Number(cat.maxQuantity) || 10;
  const merged = new Map();
  for (const item of body.items) {
    if (!item || typeof item !== "object") throw new RequestError(400, "BAD_BASKET", "The basket could not be read.");
    const product = cat.products.find((p) => p.sku === item.sku);
    if (!product) throw new RequestError(400, "BAD_BASKET", "One of the items is no longer available: " + String(item.sku).slice(0, 40));
    if (!cat.colours.includes(item.colour)) throw new RequestError(400, "BAD_BASKET", "Choose a colour from the list.");
    const qty = Number(item.qty);
    if (!Number.isInteger(qty) || qty < 1 || qty > maxQty) {
      throw new RequestError(400, "BAD_BASKET", "Quantity must be between 1 and " + maxQty + ".");
    }
    const key = product.sku + "|" + item.colour;
    const line = merged.get(key) || { sku: product.sku, name: product.name, across: product.across, colour: item.colour, qty: 0, unit: product.price, delivery: product.delivery };
    line.qty += qty;
    if (line.qty > maxQty) throw new RequestError(400, "BAD_BASKET", "Quantity must be between 1 and " + maxQty + ".");
    merged.set(key, line);
  }
  const lines = [...merged.values()];
  const count = lines.reduce((n, l) => n + l.qty, 0);
  const itemTotal = lines.reduce((n, l) => n + l.unit * l.qty, 0);
  const deliveryTotal = body.delivery === "courier" ? lines.reduce((n, l) => n + l.delivery * l.qty, 0) : 0;
  return { lines, count, delivery: body.delivery, itemTotal, deliveryTotal, total: itemTotal + deliveryTotal };
}

const money = (n) => ({ currency_code: CURRENCY, value: n.toFixed(2) });

/** The PayPal order for a priced basket: what Julie sees with the payment. */
export function orderPayload(priced, cat) {
  const plural = priced.count === 1 ? "fleece sensory beanbag" : "fleece sensory beanbags";
  const how = priced.delivery === "cork" ? "free Cork city delivery" : "courier delivery";
  return {
    intent: "CAPTURE",
    purchase_units: [
      {
        reference_id: "default",
        description: `Sensory Beanbags: ${priced.count} ${plural}, ${how}`.slice(0, 127),
        custom_id: "delivery=" + priced.delivery,
        amount: {
          ...money(priced.total),
          breakdown: { item_total: money(priced.itemTotal), shipping: money(priced.deliveryTotal) },
        },
        items: priced.lines.map((l) => ({
          name: `${l.name}, ${l.colour}`.slice(0, 127),
          description: `${l.across} across. Made to order in County Cork.`.slice(0, 127),
          sku: l.sku,
          unit_amount: money(l.unit),
          quantity: String(l.qty),
          category: "PHYSICAL_GOODS",
        })),
      },
    ],
  };
}

/* --- Endpoints ----------------------------------------------------------- */

async function createOrder(request, env) {
  const s = settings(env);
  const body = await readJson(request);
  const cat = await catalogue(env, request);
  const priced = priceBasket(cat, body);
  const res = await paypal(s, "POST", "/v2/checkout/orders", orderPayload(priced, cat), {
    "PayPal-Request-Id": crypto.randomUUID(),
  });
  if (!res.ok || !res.data || !res.data.id) {
    console.error("checkout: PayPal would not create the order: " + JSON.stringify(res.data));
    throw new RequestError(502, "PAYPAL_ERROR", "PayPal could not start the payment. Nothing has been charged.");
  }
  return reply({ id: res.data.id, total: priced.total }, 201);
}

async function captureOrder(id, request, env) {
  const s = settings(env);
  const details = await paypal(s, "GET", "/v2/checkout/orders/" + id);
  if (details.status === 404) throw new RequestError(404, "ORDER_NOT_FOUND", "That payment could not be found.");
  if (!details.ok) throw new RequestError(502, "PAYPAL_ERROR", "PayPal could not be reached. Nothing has been charged.");
  const order = details.data;
  if (order.status === "COMPLETED") return reply(summary(order));
  if (order.status !== "APPROVED") {
    throw new RequestError(409, "ORDER_NOT_APPROVED", "The payment was not approved, so nothing has been charged.");
  }

  const unit = order.purchase_units[0] || {};
  const address = (unit.shipping && unit.shipping.address) || {};
  if (address.country_code !== "IE") {
    throw new RequestError(409, "OUTSIDE_IRELAND", "We deliver within Ireland only, so the payment was not taken. Please choose a delivery address in Ireland and try again.");
  }
  if (unit.custom_id === "delivery=cork" && !inCountyCork(address)) {
    throw new RequestError(409, "NOT_CORK", "Free delivery is for the Cork city area and this address is not in Cork, so the payment was not taken. Please choose courier delivery and try again.");
  }

  const res = await paypal(s, "POST", "/v2/checkout/orders/" + id + "/capture", null, {
    "PayPal-Request-Id": "capture-" + id,
    Prefer: "return=representation",
  });
  if (res.status === 422) {
    const issue = res.data && res.data.details && res.data.details[0] && res.data.details[0].issue;
    if (issue === "INSTRUMENT_DECLINED") {
      throw new RequestError(422, "INSTRUMENT_DECLINED", "That card or account was declined. Please try another way to pay.");
    }
    if (issue === "ORDER_ALREADY_CAPTURED") {
      const again = await paypal(s, "GET", "/v2/checkout/orders/" + id);
      if (again.ok) return reply(summary(again.data));
    }
    console.error("checkout: capture refused: " + JSON.stringify(res.data));
    throw new RequestError(422, issue || "PAYPAL_ERROR", "PayPal could not complete the payment. Nothing has been charged.");
  }
  if (!res.ok) {
    console.error("checkout: capture failed: " + JSON.stringify(res.data));
    throw new RequestError(502, "PAYPAL_ERROR", "PayPal could not complete the payment. If money has left your account, please call Julie with your PayPal receipt.");
  }
  return reply(summary(res.data, unit));
}

/** What the thank-you panel shows: no more than the buyer typed in themselves. */
function summary(order, unitFromBefore) {
  const unit = order.purchase_units[0] || unitFromBefore || {};
  const captures = (unit.payments && unit.payments.captures) || [];
  const capture = captures[0] || {};
  const shipping = unit.shipping || (unitFromBefore && unitFromBefore.shipping) || {};
  const address = shipping.address || {};
  const items = unit.items || (unitFromBefore && unitFromBefore.items) || [];
  const payer = order.payer || {};
  return {
    status: order.status,
    reference: order.id,
    captureId: capture.id || null,
    captureStatus: capture.status || null,
    pendingReason: (capture.status_details && capture.status_details.reason) || null,
    amount: capture.amount || unit.amount || null,
    payer: {
      name: payer.name ? [payer.name.given_name, payer.name.surname].filter(Boolean).join(" ") : null,
      email: payer.email_address || null,
    },
    deliverTo: {
      name: (shipping.name && shipping.name.full_name) || null,
      lines: [address.address_line_1, address.address_line_2, address.admin_area_2, address.admin_area_1, address.postal_code, address.country_code].filter(Boolean),
    },
    items: items.map((i) => ({ name: i.name, quantity: Number(i.quantity), unit: i.unit_amount ? Number(i.unit_amount.value) : null })),
  };
}

/** Eircodes for County Cork start with P or T, and nobody else's do. */
export function inCountyCork(address) {
  const words = [address.admin_area_1, address.admin_area_2, address.address_line_1, address.address_line_2]
    .filter(Boolean).join(" ").toLowerCase();
  if (/\bcork\b|\bcorcaigh\b/.test(words)) return true;
  const eircode = String(address.postal_code || "").replace(/\s+/g, "").toUpperCase();
  return /^[PT]\d\d/.test(eircode);
}

/* --- PayPal REST ---------------------------------------------------------- */

let tokenCache = { key: "", value: "", expires: 0 };

async function accessToken(s) {
  const key = s.base + "|" + s.id;
  if (tokenCache.key === key && tokenCache.expires > Date.now()) return tokenCache.value;
  const res = await fetch(s.base + "/v1/oauth2/token", {
    method: "POST",
    headers: {
      Authorization: "Basic " + btoa(s.id + ":" + s.secret),
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: "grant_type=client_credentials",
  });
  if (!res.ok) {
    console.error("checkout: PayPal refused the credentials: HTTP " + res.status);
    throw new RequestError(502, "PAYPAL_AUTH", "PayPal did not accept the site's credentials. Nothing has been charged.");
  }
  const data = await res.json();
  tokenCache = { key, value: data.access_token, expires: Date.now() + Math.max(0, (data.expires_in || 0) - 60) * 1000 };
  return data.access_token;
}

async function paypal(s, method, path, body, extraHeaders) {
  const headers = Object.assign(
    { Authorization: "Bearer " + (await accessToken(s)), "Content-Type": "application/json" },
    extraHeaders || {},
  );
  const res = await fetch(s.base + path, { method, headers, body: body == null ? undefined : JSON.stringify(body) });
  const text = await res.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch (e) {
    data = { raw: text.slice(0, 500) };
  }
  return { ok: res.ok, status: res.status, data };
}

/* --- HTTP helpers --------------------------------------------------------- */

async function readJson(request) {
  const length = Number(request.headers.get("content-length") || 0);
  if (length > MAX_BODY_BYTES) throw new RequestError(413, "BAD_BASKET", "The basket is too large.");
  const text = await request.text();
  if (text.length > MAX_BODY_BYTES) throw new RequestError(413, "BAD_BASKET", "The basket is too large.");
  try {
    return JSON.parse(text);
  } catch (e) {
    throw new RequestError(400, "BAD_BASKET", "The basket could not be read.");
  }
}

function reply(data, status) {
  return new Response(JSON.stringify(data), {
    status: status || 200,
    headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" },
  });
}
