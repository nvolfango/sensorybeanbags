/* Sensory Beanbags — the basket and online checkout. No dependencies.

   The basket is kept in this browser (localStorage) as a list of
   { sku, colour, qty }. Prices come from assets/data/catalogue.json, the same
   file the checkout function on the server reads, so what PayPal charges is
   worked out on the server and never trusted from here.

   Three jobs, each only where its markup exists:
     1. the basket count in the header, on every page;
     2. the "add to basket" form on the beanbags page;
     3. the basket page: lines, delivery, totals and the PayPal buttons. */
(function () {
  "use strict";

  var KEY = "sb-basket";
  var MAX_LINES = 10;

  /* --- The basket in storage --------------------------------------------- */

  function readBasket() {
    try {
      var raw = JSON.parse(localStorage.getItem(KEY) || "[]");
      if (!Array.isArray(raw)) return [];
      return raw.filter(function (l) {
        return l && typeof l.sku === "string" && typeof l.colour === "string" &&
          typeof l.qty === "number" && l.qty % 1 === 0 && l.qty > 0;
      }).map(function (l) { return { sku: l.sku, colour: l.colour, qty: l.qty }; });
    } catch (e) {
      return [];
    }
  }

  function saveBasket(lines) {
    try {
      localStorage.setItem(KEY, JSON.stringify(lines));
    } catch (e) { /* storage unavailable: the basket lives for this page only */ }
    paintHeader(lines);
  }

  function countOf(lines) {
    return lines.reduce(function (n, l) { return n + l.qty; }, 0);
  }

  /* --- Header count ------------------------------------------------------- */

  function paintHeader(lines) {
    var count = countOf(lines || readBasket());
    var badge = document.querySelector("[data-basket-count]");
    var link = document.querySelector("[data-basket-link]");
    if (!badge || !link) return;
    badge.textContent = String(count);
    badge.hidden = count === 0;
    link.setAttribute("aria-label", count === 0 ? "Basket, empty" : "Basket, " + count + (count === 1 ? " item" : " items"));
  }

  paintHeader();
  window.addEventListener("storage", function (e) { if (e.key === KEY) paintHeader(); });

  /* --- Small helpers ------------------------------------------------------ */

  function euro(n) {
    return "€" + Number(n).toLocaleString("en-IE");
  }

  // Builds an element. Text goes in through textContent, never innerHTML, so
  // nothing from storage or the network is ever treated as markup.
  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === "class") node.className = attrs[k];
      else if (k === "text") node.textContent = attrs[k];
      else if (k.indexOf("on") === 0) node.addEventListener(k.slice(2), attrs[k]);
      else if (attrs[k] === true) node.setAttribute(k, "");
      else if (attrs[k] !== false && attrs[k] != null) node.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) {
      if (c == null) return;
      node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    });
    return node;
  }

  function fetchJson(url, body) {
    var init = body === undefined
      ? { method: "GET", cache: "no-store" }
      : { method: "POST", cache: "no-store", headers: body === null ? {} : { "Content-Type": "application/json" }, body: body === null ? undefined : JSON.stringify(body) };
    return fetch(url, init).then(function (r) {
      return r.text().then(function (t) {
        var data = {};
        try { data = t ? JSON.parse(t) : {}; } catch (e) { data = {}; }
        return { ok: r.ok, status: r.status, data: data };
      });
    });
  }

  /* --- 2. Add to basket (beanbags page) ------------------------------------ */

  var form = document.querySelector("[data-order-form]");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var status = form.querySelector("[data-order-status]");
      var skuField = form.elements.sku;
      var option = skuField.options[skuField.selectedIndex];
      var colour = form.elements.colour.value;
      var qty = parseInt(form.elements.qty.value, 10);
      var maxQty = parseInt(form.elements.qty.max, 10) || 10;
      status.textContent = "";
      if (!option || !option.value || !colour || !(qty >= 1 && qty <= maxQty)) {
        status.textContent = "Choose a size, a colour and a quantity between 1 and " + maxQty + ".";
        return;
      }
      var lines = readBasket();
      var existing = lines.filter(function (l) { return l.sku === option.value && l.colour === colour; })[0];
      if (existing) {
        existing.qty = Math.min(maxQty, existing.qty + qty);
      } else if (lines.length >= MAX_LINES) {
        status.textContent = "The basket is full. For a larger order, please email Julie.";
        return;
      } else {
        lines.push({ sku: option.value, colour: colour, qty: qty });
      }
      saveBasket(lines);
      var count = countOf(lines);
      status.appendChild(document.createTextNode(
        "Added " + qty + " × " + option.getAttribute("data-name") + ", " + colour + ". " +
        "Your basket now has " + count + (count === 1 ? " beanbag. " : " beanbags. ")));
      status.appendChild(el("a", { href: "cart.html", text: "Go to your basket to pay" }));
      status.appendChild(document.createTextNode("."));
    });
  }

  /* --- 3. The basket page -------------------------------------------------- */

  var root = document.querySelector("[data-basket]");
  if (!root) return;

  var contact = {
    email: root.getAttribute("data-email"),
    phone: root.getAttribute("data-phone"),
    phoneLink: root.getAttribute("data-phone-link")
  };
  var state = { cat: null, lines: [], delivery: "courier", maxQty: 10 };
  var parts = {};

  fetchJson("assets/data/catalogue.json").then(function (res) {
    if (!res.ok || !res.data.products) throw new Error("catalogue");
    state.cat = res.data;
    state.maxQty = res.data.maxQuantity || 10;
    // Drop anything the catalogue no longer has, and clamp quantities
    state.lines = readBasket().filter(function (l) {
      return product(l.sku) && state.cat.colours.indexOf(l.colour) !== -1;
    }).map(function (l) { l.qty = Math.min(l.qty, state.maxQty); return l; });
    saveBasket(state.lines);
    render();
  }).catch(function () {
    root.textContent = "";
    root.appendChild(el("div", { class: "note" }, [el("p", {}, [
      el("strong", { text: "The price list could not be loaded. " }),
      "Please reload the page, or call ", el("a", { href: "tel:" + contact.phoneLink, text: contact.phone }), " to order."
    ])]));
  });

  function product(sku) {
    return state.cat.products.filter(function (p) { return p.sku === sku; })[0];
  }
  function itemTotal() {
    return state.lines.reduce(function (n, l) { return n + product(l.sku).price * l.qty; }, 0);
  }
  function deliveryTotal() {
    if (state.delivery === "cork") return 0;
    return state.lines.reduce(function (n, l) { return n + product(l.sku).delivery * l.qty; }, 0);
  }

  function render() {
    root.textContent = "";
    if (!state.lines.length) {
      root.appendChild(el("div", { class: "basket-empty" }, [
        el("h2", { text: "Your basket is empty" }),
        el("p", { class: "lede", text: "Fleece beanbags can be added from the sizes table on the beanbags page." }),
        el("div", { class: "btn-row" }, [
          el("a", { class: "btn btn--primary", href: "beanbags.html#order-online", text: "Choose a beanbag" }),
          el("a", { class: "btn btn--ghost", href: "order.html", text: "Other ways to order" })
        ])
      ]));
      return;
    }
    parts.lines = el("div", { class: "table-scroll" });
    parts.delivery = deliveryFieldset();
    parts.totals = el("ul", { class: "totals", "aria-live": "polite" });
    parts.pay = payBox();
    root.appendChild(parts.lines);
    root.appendChild(parts.delivery);
    root.appendChild(parts.totals);
    root.appendChild(parts.pay);
    refresh();
    setupPayment();
  }

  // Redraws the lines and totals after a change; the pay box stays put so the
  // PayPal buttons are not torn down (they read the basket when clicked).
  function refresh() {
    if (!state.lines.length) { render(); return; }
    parts.lines.textContent = "";
    parts.lines.appendChild(linesTable());
    parts.delivery.querySelector("[data-courier-cost]").textContent = euro(
      state.lines.reduce(function (n, l) { return n + product(l.sku).delivery * l.qty; }, 0));
    var count = countOf(state.lines);
    parts.totals.textContent = "";
    parts.totals.appendChild(el("li", {}, [el("span", { text: (count === 1 ? "1 beanbag" : count + " beanbags") }), el("span", { text: euro(itemTotal()) })]));
    parts.totals.appendChild(el("li", {}, [el("span", { text: "Delivery" }), el("span", { text: state.delivery === "cork" ? "Free" : euro(deliveryTotal()) })]));
    parts.totals.appendChild(el("li", { class: "grand" }, [el("span", { text: "Total to pay" }), el("span", { text: euro(itemTotal() + deliveryTotal()) })]));
    parts.pay.querySelector("[data-email-order]").setAttribute("href", emailHref());
  }

  function linesTable() {
    var tbody = el("tbody");
    state.lines.forEach(function (line, index) {
      var p = product(line.sku);
      var qtySelect = el("select", { "aria-label": "Quantity of " + p.name + ", " + line.colour, onchange: function (e) {
        line.qty = parseInt(e.target.value, 10) || 1;
        saveBasket(state.lines);
        refresh();
      } });
      for (var q = 1; q <= state.maxQty; q++) {
        qtySelect.appendChild(el("option", { value: String(q), selected: q === line.qty, text: String(q) }));
      }
      var remove = el("button", { type: "button", class: "link-button", text: "Remove", onclick: function () {
        state.lines.splice(index, 1);
        saveBasket(state.lines);
        refresh();
      } });
      tbody.appendChild(el("tr", {}, [
        el("td", { "data-label": "Item" }, [el("b", { text: p.name }), el("br"), el("span", { class: "colour", text: line.colour + " · " + p.across + " across" })]),
        el("td", { "data-label": "Quantity" }, [el("div", { class: "qty" }, [qtySelect, remove])]),
        el("td", { "data-label": "Price" }, [el("b", { text: euro(p.price * line.qty) }), line.qty > 1 ? el("span", { class: "colour", text: " (" + euro(p.price) + " each)" }) : null])
      ]));
    });
    return el("table", { class: "basket-table" }, [
      el("caption", { text: "Fleece sensory beanbags, made to order in your colour." }),
      el("thead", {}, [el("tr", {}, [
        el("th", { scope: "col", text: "Item" }), el("th", { scope: "col", text: "Quantity" }), el("th", { scope: "col", text: "Price" })
      ])]),
      tbody
    ]);
  }

  function deliveryFieldset() {
    var d = state.cat.delivery;
    function option(value, label, note, costNode) {
      var input = el("input", { type: "radio", name: "delivery", value: value, checked: state.delivery === value, onchange: function () {
        state.delivery = value;
        refresh();
      } });
      return el("label", {}, [input, el("b", { text: label }), costNode, el("small", { text: note })]);
    }
    var perBeanbag = state.cat.products.map(function (p) { return p.delivery; });
    var courierNote = "€" + Math.min.apply(null, perBeanbag) + (Math.min.apply(null, perBeanbag) === Math.max.apply(null, perBeanbag) ? "" : "–" + Math.max.apply(null, perBeanbag)) + " per beanbag. " + (d.courier.note || "");
    return el("fieldset", { class: "delivery-options" }, [
      el("legend", { text: "Delivery" }),
      option("courier", d.courier.label, courierNote, el("span", { class: "cost", "data-courier-cost": true })),
      option("cork", d.cork.label, d.cork.note || "", el("span", { class: "cost", text: "Free" }))
    ]);
  }

  function payBox() {
    return el("div", { class: "pay-box" }, [
      el("h2", { text: "Pay securely" }),
      el("p", {}, ["Pay with your PayPal account, or choose ", el("b", { text: "Debit or Credit Card" }), " to pay by card without one. PayPal asks for your delivery address during payment."]),
      el("div", { class: "paypal-buttons", id: "paypal-buttons" }, [el("p", { class: "small", "data-pay-loading": true, text: "Loading payment options…" })]),
      el("p", { class: "pay-message", "data-pay-message": true, role: "status", "aria-live": "polite" }),
      el("p", { class: "small", text: "Payments are handled by PayPal. Your card details never reach this website." }),
      el("div", { class: "pay-alt" }, [
        el("p", {}, [
          el("strong", { text: "Rather pay by Revolut or bank transfer? " }),
          el("a", { href: "#", "data-email-order": true, text: "Email this order to Julie" }),
          " and she will send you the details. Or call ", el("a", { href: "tel:" + contact.phoneLink, text: contact.phone }), "."
        ])
      ])
    ]);
  }

  function emailHref() {
    var body = "Hi Julie,\n\nI'd like to order:\n";
    state.lines.forEach(function (l) {
      var p = product(l.sku);
      body += "- " + l.qty + " x " + p.name + ", " + l.colour + " (" + euro(p.price * l.qty) + ")\n";
    });
    body += "\nDelivery: " + (state.delivery === "cork" ? "Cork city (free)" : "courier or An Post (" + euro(deliveryTotal()) + ")") +
      "\nTotal: " + euro(itemTotal() + deliveryTotal()) +
      "\n\nMy name, delivery address and phone number:\n\n\nI'd like to pay by (Revolut, bank transfer, or cash on delivery in Cork city):\n\n\nThanks,\n";
    return "mailto:" + contact.email + "?subject=" + encodeURIComponent("Beanbag order") + "&body=" + encodeURIComponent(body);
  }

  /* --- PayPal -------------------------------------------------------------- */

  function say(text, isError) {
    var box = parts.pay && parts.pay.querySelector("[data-pay-message]");
    if (!box) return;
    box.textContent = text || "";
    box.className = "pay-message" + (isError ? " is-error" : "");
  }

  function unavailable() {
    var host = parts.pay.querySelector("#paypal-buttons");
    host.textContent = "";
    host.appendChild(el("div", { class: "note" }, [el("p", {}, [
      el("strong", { text: "Online payment is not switched on here yet. " }),
      "You can still order: email the basket to Julie with the link below and pay by Revolut or bank transfer, or call ",
      el("a", { href: "tel:" + contact.phoneLink, text: contact.phone }), "."
    ])]));
  }

  function setupPayment() {
    fetchJson("api/checkout/config").then(function (res) {
      if (!res.ok || !res.data.clientId) throw new Error(res.data.error || "config");
      return loadSdk(res.data);
    }).then(renderButtons).catch(function (err) {
      if (window.console) console.warn("Online payment unavailable:", err && err.message);
      unavailable();
    });
  }

  function loadSdk(cfg) {
    return new Promise(function (resolve, reject) {
      if (window.paypal && window.paypal.Buttons) return resolve();
      var script = document.createElement("script");
      script.src = "https://www.paypal.com/sdk/js?client-id=" + encodeURIComponent(cfg.clientId) +
        "&currency=" + encodeURIComponent(cfg.currency || "EUR") + "&intent=capture&components=buttons";
      script.async = true;
      script.setAttribute("data-page-type", "checkout");
      script.onload = function () { (window.paypal && window.paypal.Buttons) ? resolve() : reject(new Error("sdk")); };
      script.onerror = function () { reject(new Error("sdk")); };
      document.head.appendChild(script);
    });
  }

  function renderButtons() {
    var host = parts.pay.querySelector("#paypal-buttons");
    var buttons = window.paypal.Buttons({
      style: { layout: "vertical", shape: "pill", color: "gold", label: "pay" },

      onClick: function (data, actions) {
        say("");
        if (!state.lines.length) {
          say("Your basket is empty.", true);
          return actions.reject();
        }
        return actions.resolve();
      },

      // The server prices the basket and creates the PayPal order; we only
      // pass back PayPal's order id.
      createOrder: function () {
        return fetchJson("api/checkout/orders", { items: state.lines, delivery: state.delivery }).then(function (res) {
          if (!res.ok || !res.data.id) {
            throw new Error(res.data.message || "Could not start the payment. Please try again, or call " + contact.phone + ".");
          }
          return res.data.id;
        }).catch(function (err) {
          say(err.message || "Could not start the payment. Please try again, or call " + contact.phone + ".", true);
          throw err;
        });
      },

      // Ireland only: tell the buyer inside PayPal's window, before they get
      // as far as paying. The server checks again before taking the money.
      onShippingAddressChange: function (data, actions) {
        var country = data && data.shippingAddress && data.shippingAddress.countryCode;
        if (country && country !== "IE") return actions.reject(data.errors.COUNTRY_ERROR);
      },

      onApprove: function (data, actions) {
        say("Finishing your payment…");
        return fetchJson("api/checkout/orders/" + encodeURIComponent(data.orderID) + "/capture", null).then(function (res) {
          if (res.data.error === "INSTRUMENT_DECLINED") {
            say("That card or account was declined. Please try another way to pay.", true);
            return actions.restart();
          }
          if (!res.ok) {
            say((res.data.message || "The payment could not be completed. Nothing has been charged.") + " Reference " + data.orderID + ".", true);
            return;
          }
          showThanks(res.data);
        }).catch(function () {
          say("The payment may not have completed. Please check your email for a PayPal receipt before trying again, or call " + contact.phone + " quoting reference " + data.orderID + ".", true);
        });
      },

      onCancel: function () {
        say("Payment cancelled. Your basket is still here whenever you are ready.");
      },

      onError: function (err) {
        if (window.console) console.error(err);
        say("Something went wrong with the payment. Nothing has been charged unless PayPal has emailed you a receipt. Please try again, or call " + contact.phone + ".", true);
      }
    });

    if (!buttons.isEligible()) { unavailable(); return; }
    host.textContent = "";
    return buttons.render("#paypal-buttons");
  }

  function showThanks(order) {
    state.lines = [];
    saveBasket([]);
    var pending = order.captureStatus && order.captureStatus !== "COMPLETED";
    var amount = order.amount ? euro(Number(order.amount.value)) : "";
    var details = el("dl");
    function row(label, value) {
      details.appendChild(el("dt", { text: label }));
      details.appendChild(el("dd", {}, [typeof value === "string" ? document.createTextNode(value) : value]));
    }
    row("Reference", order.reference || "");
    if (amount) row(pending ? "Amount" : "Paid", amount);
    if (order.items && order.items.length) {
      row("Order", el("ul", {}, order.items.map(function (i) { return el("li", { text: i.quantity + " × " + i.name }); })));
    }
    if (order.deliverTo && order.deliverTo.lines.length) {
      row("Delivering to", el("span", { text: [order.deliverTo.name].concat(order.deliverTo.lines).filter(Boolean).join(", ") }));
    }
    var mail = "mailto:" + contact.email + "?subject=" + encodeURIComponent("Order " + (order.reference || ""));
    root.textContent = "";
    root.appendChild(el("div", { class: "thanks", role: "status", tabindex: "-1" }, [
      el("h2", { text: pending ? "Thank you — your payment is being processed" : "Thank you — your order is paid" }),
      el("p", { text: pending
        ? "PayPal is still processing this payment" + (order.pendingReason ? " (" + order.pendingReason.toLowerCase().replace(/_/g, " ") + ")" : "") + ". Julie will start on your beanbag once it clears, and PayPal will email you either way."
        : "PayPal has emailed you a receipt, and Julie has your order and delivery address with the payment. She will be in touch to confirm. Beanbags are usually made within five to seven working days." }),
      details,
      el("p", {}, [
        "Anything to add — a delivery instruction, a question about the colour? ",
        el("a", { href: mail, text: "Email Julie" }), " quoting the reference, or call ",
        el("a", { href: "tel:" + contact.phoneLink, text: contact.phone }), "."
      ]),
      el("div", { class: "btn-row" }, [el("a", { class: "btn btn--ghost", href: "index.html", text: "Back to the home page" })])
    ]));
    root.querySelector(".thanks").focus();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
})();
