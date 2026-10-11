/*
 * A stand-in for PayPal's REST API, enough for the checkout function's tests:
 * OAuth token, create order, show order, capture. Orders start CREATED; a test
 * approves one (with a delivery address) through POST /__test/approve/<id>,
 * which stands in for the buyer going through PayPal's window.
 *
 *   node tests/mock-paypal.mjs [port]      runs it on its own (default 8799)
 *   import { startMockPayPal } ...         from a test
 */
import http from "node:http";

export function startMockPayPal(port = 0) {
  const orders = new Map();
  const calls = [];
  let nextId = 1;

  const server = http.createServer(async (req, res) => {
    const chunks = [];
    for await (const c of req) chunks.push(c);
    const text = Buffer.concat(chunks).toString("utf8");
    let body = null;
    if (text && String(req.headers["content-type"] || "").includes("json")) {
      try { body = JSON.parse(text); } catch (e) { body = { raw: text }; }
    } else if (text) {
      body = { raw: text };
    }
    const url = new URL(req.url, "http://x");
    calls.push({ method: req.method, path: url.pathname, body, headers: req.headers });
    const send = (status, data) => {
      res.writeHead(status, { "content-type": "application/json" });
      res.end(JSON.stringify(data));
    };

    if (req.method === "POST" && url.pathname === "/v1/oauth2/token") {
      if (!String(req.headers.authorization || "").startsWith("Basic ")) return send(401, { error: "invalid_client" });
      return send(200, { access_token: "TEST-TOKEN", expires_in: 3600 });
    }

    if (url.pathname.startsWith("/v2/") && !String(req.headers.authorization || "").startsWith("Bearer ")) {
      return send(401, { name: "NOT_AUTHORIZED" });
    }
    if (req.method === "POST" && url.pathname === "/v2/checkout/orders") {
      const id = "ORDER" + String(nextId++).padStart(5, "0");
      orders.set(id, { id, status: "CREATED", intent: body.intent, purchase_units: body.purchase_units.map((u) => ({ ...u })) });
      return send(201, { id, status: "CREATED" });
    }
    let m = /^\/v2\/checkout\/orders\/([A-Z0-9]+)$/.exec(url.pathname);
    if (req.method === "GET" && m) {
      const order = orders.get(m[1]);
      return order ? send(200, order) : send(404, { name: "RESOURCE_NOT_FOUND" });
    }
    m = /^\/v2\/checkout\/orders\/([A-Z0-9]+)\/capture$/.exec(url.pathname);
    if (req.method === "POST" && m) {
      const order = orders.get(m[1]);
      if (!order) return send(404, { name: "RESOURCE_NOT_FOUND" });
      if (order.status === "COMPLETED") return send(422, { name: "UNPROCESSABLE_ENTITY", details: [{ issue: "ORDER_ALREADY_CAPTURED" }] });
      if (order.status !== "APPROVED") return send(422, { name: "UNPROCESSABLE_ENTITY", details: [{ issue: "ORDER_NOT_APPROVED" }] });
      if (order.decline) return send(422, { name: "UNPROCESSABLE_ENTITY", details: [{ issue: "INSTRUMENT_DECLINED" }] });
      order.status = "COMPLETED";
      order.purchase_units[0].payments = {
        captures: [{ id: "CAP" + order.id.slice(5), status: "COMPLETED", final_capture: true, amount: order.purchase_units[0].amount }],
      };
      return send(201, order);
    }
    if (req.method === "GET" && url.pathname === "/__test/calls") return send(200, calls);
    m = /^\/__test\/approve\/([A-Z0-9]+)$/.exec(url.pathname);
    if (req.method === "POST" && m) {
      const order = orders.get(m[1]);
      if (!order) return send(404, {});
      order.status = "APPROVED";
      order.decline = Boolean(body && body.decline);
      order.payer = { name: { given_name: "Test", surname: "Buyer" }, email_address: "buyer@example.com", payer_id: "PAYER123" };
      order.purchase_units[0].shipping = {
        name: { full_name: "Test Buyer" },
        address: (body && body.address) || { address_line_1: "1 Main Street", admin_area_2: "Douglas", admin_area_1: "Co. Cork", postal_code: "T12 AB12", country_code: "IE" },
      };
      return send(200, order);
    }
    send(404, { name: "NOT_FOUND" });
  });

  return new Promise((resolve) => {
    server.listen(port, "127.0.0.1", () => {
      resolve({ server, orders, calls, base: "http://127.0.0.1:" + server.address().port, close: () => new Promise((r) => server.close(r)) });
    });
  });
}

if (process.argv[1] && import.meta.url.endsWith(process.argv[1].split("/").pop())) {
  const port = Number(process.argv[2] || 8799);
  startMockPayPal(port).then((m) => console.log("mock PayPal on " + m.base));
}
