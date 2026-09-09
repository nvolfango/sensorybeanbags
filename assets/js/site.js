/* Sensory Beanbags — minimal progressive enhancement. No dependencies. */
(function () {
  "use strict";

  // Theme switch: light / auto / dark. "auto" means follow the device setting.
  // The choice is kept in localStorage and applied before first paint by a
  // small inline script in <head> (see tools/build.py).
  var root = document.documentElement;
  var themeSwitch = document.querySelector(".theme-switch");

  function paintThemeSwitch() {
    var current = root.getAttribute("data-theme") || "auto";
    var buttons = themeSwitch.querySelectorAll("button");
    for (var i = 0; i < buttons.length; i++) {
      var on = buttons[i].getAttribute("data-theme-choice") === current;
      buttons[i].setAttribute("aria-pressed", on ? "true" : "false");
    }
  }

  if (themeSwitch) {
    themeSwitch.addEventListener("click", function (e) {
      var button = e.target.closest("button");
      if (!button) return;
      var choice = button.getAttribute("data-theme-choice");
      try {
        if (choice === "auto") {
          root.removeAttribute("data-theme");
          localStorage.removeItem("theme");
        } else {
          root.setAttribute("data-theme", choice);
          localStorage.setItem("theme", choice);
        }
      } catch (err) { /* storage unavailable: the choice still applies to this page */ }
      paintThemeSwitch();
    });
    paintThemeSwitch();
  }

  // Mobile navigation toggle
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("primary-nav");

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });

    // Close the menu when a link is followed or Escape is pressed
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
  }
})();
