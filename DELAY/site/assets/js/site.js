/* ============================================================
   Aaron Delay Counseling — site config + form handling
   ------------------------------------------------------------
   ONE FILE TO EDIT WHEN THE ACCOUNTS ARE LIVE.
   Replace the REPLACE_ME values below and everything wires up.
   ============================================================ */

var SITE = {
  /* MailerLite embedded-form endpoint.
     Forms > Embedded forms > the form > HTML code, inside action="".
     Account 2591010, form "Reset opt-in (site-wide)".                */
  FORM_ACTION: "https://assets.mailerlite.com/jsonp/2591010/forms/196633341769811899/subscribe",

  /* Gumroad product URL for the $19 playbook.
     Looks like: https://aarondelay.gumroad.com/l/playbook         */
  GUMROAD_PLAYBOOK_URL: "https://shop.aarondelaycounseling.com/l/wrong-person",

  /* Instagram profile URL.
     Looks like: https://www.instagram.com/aarondelaycounseling/    */
  INSTAGRAM_URL: "https://www.instagram.com/aarondelaytherapy/",

  /* Public contact address for speaking enquiries.                */
  CONTACT_EMAIL: "aaron@aarondelaycounseling.com",

  /* Where to send people after a successful opt-in.
     Leave as-is to use the built-in /thanks/ page.                */
  THANKS_URL: "/thanks/",

  /* Enquiry forms, keyed by the form's data-enquiry-kind attribute.
     Formspree endpoints look like https://formspree.io/f/xxxxxxxx

     "thanks" is a plain site-relative path because the redirect happens
     in this file, not at the form service.

     Leave an action as REPLACE_ME and that form falls back to opening
     the visitor's own mail client. The fallback needs no account, but
     it strands anyone without a mail client configured, so treat it as
     a stopgap rather than a solution.                                */
  ENQUIRY: {
    Coaching: {
      action: "https://formspree.io/f/xrpzwpnb",
      thanks: "/coaching-thanks/"
    },
    Speaking: {
      action: "https://formspree.io/f/xbgrvogj",
      thanks: "/speaking-thanks/"
    }
  }
};

(function () {
  "use strict";

  var unset = function (v) { return !v || v.indexOf("REPLACE_ME") === 0; };

  /* ---------- Wire up Gumroad links ---------- */
  document.querySelectorAll("[data-gumroad]").forEach(function (el) {
    if (unset(SITE.GUMROAD_PLAYBOOK_URL)) {
      el.setAttribute("href", "#");
      el.addEventListener("click", function (e) {
        e.preventDefault();
        alert("Checkout isn't connected yet.\n\nAdd the Gumroad product URL in assets/js/site.js (GUMROAD_PLAYBOOK_URL).");
      });
    } else {
      el.setAttribute("href", SITE.GUMROAD_PLAYBOOK_URL);
    }
  });

  /* ---------- Wire up Instagram links ---------- */
  document.querySelectorAll("[data-instagram]").forEach(function (el) {
    if (unset(SITE.INSTAGRAM_URL)) {
      el.setAttribute("href", "#");
      el.addEventListener("click", function (e) {
        e.preventDefault();
        alert("Instagram isn't connected yet.\n\nAdd Aaron's profile URL in assets/js/site.js (INSTAGRAM_URL).");
      });
    } else {
      el.setAttribute("href", SITE.INSTAGRAM_URL);
    }
  });

  /* ---------- Wire up contact / speaking mailto links ---------- */
  document.querySelectorAll("[data-mailto]").forEach(function (el) {
    if (unset(SITE.CONTACT_EMAIL)) {
      el.setAttribute("href", "#");
      el.addEventListener("click", function (e) {
        e.preventDefault();
        alert("No contact address set yet.\n\nAdd it in assets/js/site.js (CONTACT_EMAIL).");
      });
    } else {
      var subject = el.getAttribute("data-mailto") || "Enquiry";
      el.setAttribute("href", "mailto:" + SITE.CONTACT_EMAIL + "?subject=" + encodeURIComponent(subject));
    }
  });

  /* ---------- Opt-in forms ---------- */
  /* MailerLite's endpoint is JSONP: a normal form POST would navigate the
     visitor to a page of raw JSON. So we send it with fetch in no-cors mode
     and move them to /thanks/ ourselves. We cannot read a no-cors response,
     so HTML5 validation is what catches bad input before it is sent. */
  document.querySelectorAll("form[data-optin]").forEach(function (form) {
    var note = form.querySelector(".form-note");

    if (unset(SITE.FORM_ACTION)) {
      form.setAttribute("action", "#");
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        if (note) {
          note.textContent =
            "This form isn't connected yet. Add the MailerLite form action URL in assets/js/site.js (FORM_ACTION).";
          note.classList.add("show");
        }
      });
      return;
    }

    form.setAttribute("action", SITE.FORM_ACTION);
    form.setAttribute("method", "post");

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }

      var btn = form.querySelector("button[type=submit]");
      if (btn) { btn.disabled = true; btn.textContent = "Sending…"; }

      var done = false;
      var go = function () {
        if (done) { return; }
        done = true;
        window.location.href = SITE.THANKS_URL;
      };

      /* URLSearchParams, not FormData: FormData sends multipart/form-data
         and MailerLite's endpoint only accepts url-encoded bodies. It
         silently accepts the request and creates no subscriber otherwise. */
      fetch(SITE.FORM_ACTION, {
        method: "POST",
        mode: "no-cors",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams(new FormData(form)).toString()
      }).then(go).catch(go);

      /* Never strand someone on a disabled button if the network hangs. */
      setTimeout(go, 3500);
    });
  });

  /* ---------- Enquiry forms (coaching, speaking) ---------- */
  document.querySelectorAll("form[data-enquiry]").forEach(function (form) {
    var note = form.querySelector(".form-note");

    var say = function (msg) {
      if (note) { note.textContent = msg; note.classList.add("show"); }
    };

    /* Which enquiry this is. Unknown kinds fall through to the mailto
       fallback rather than posting somewhere arbitrary. */
    var kind = form.getAttribute("data-enquiry-kind") || "Coaching";
    var cfg = (SITE.ENQUIRY && SITE.ENQUIRY[kind]) || {};

    /* A real endpoint is configured.

       We submit with fetch rather than letting the browser navigate, and do
       the redirect ourselves. Formspree ignores the "_next" hidden field, so
       a native POST strands the visitor on formspree.io looking at someone
       else's branding. Asking for JSON back also means a failure can be shown
       in place, on our own page, instead of on their error screen.

       The action and method are still set, so if this script fails to load
       the browser falls back to a native POST. That lands on Formspree's own
       confirmation page, which is worse but is not a dead end. */
    if (!unset(cfg.action)) {
      form.setAttribute("action", cfg.action);
      form.setAttribute("method", "post");

      form.addEventListener("submit", function (e) {
        e.preventDefault();
        if (!form.checkValidity()) { form.reportValidity(); return; }

        var btn = form.querySelector("button[type=submit]");
        var label = btn ? btn.textContent : "";
        if (btn) { btn.disabled = true; btn.textContent = "Sending\u2026"; }

        var restore = function () {
          if (btn) { btn.disabled = false; btn.textContent = label; }
        };

        fetch(cfg.action, {
          method: "POST",
          headers: { "Accept": "application/json" },
          body: new FormData(form)
        }).then(function (res) {
          if (res.ok) {
            window.location.href = cfg.thanks;
            return;
          }
          /* Formspree returns the reason in JSON. Surface it rather than a
             generic failure, so a bad email address reads as a bad email
             address. */
          return res.json().then(function (data) {
            var msg = data && data.errors && data.errors.length
              ? data.errors.map(function (x) { return x.message; }).join(" ")
              : "Something went wrong sending that.";
            say(msg + " You can also email " + SITE.CONTACT_EMAIL + " directly.");
            restore();
          }).catch(function () {
            say("Something went wrong sending that. You can also email " + SITE.CONTACT_EMAIL + " directly.");
            restore();
          });
        }).catch(function () {
          say("That didn't send, which usually means the connection dropped. Try again, or email " + SITE.CONTACT_EMAIL + " directly.");
          restore();
        });
      });
      return;
    }

    /* No endpoint yet. Hand the message to the visitor's own mail client
       so nothing is stored by a third party and no account is needed. */
    form.addEventListener("submit", function (e) {
      e.preventDefault();

      if (unset(SITE.CONTACT_EMAIL)) {
        say("This form isn't connected yet. Add CONTACT_EMAIL in assets/js/site.js, or an endpoint under ENQUIRY." + kind + ".");
        return;
      }

      /* Build the body from whatever fields this form actually has, so a
         new field never silently goes missing from the email. */
      var fields = Array.prototype.slice.call(
        form.querySelectorAll("input[name], textarea[name], select[name]")
      );

      var missing = fields.filter(function (el) {
        return el.required && !el.value.trim();
      });
      if (missing.length) {
        say("Please fill in the required fields before sending.");
        missing[0].focus();
        return;
      }

      var labelFor = function (el) {
        var lab = form.querySelector('label[for="' + el.id + '"]');
        if (!lab) { return el.name; }
        /* Drop the "(optional)" style hint so the email reads cleanly. */
        var clone = lab.cloneNode(true);
        var opt = clone.querySelector(".opt");
        if (opt) { opt.remove(); }
        return clone.textContent.trim().replace(/\s+/g, " ");
      };

      var who = "";
      var body = fields.map(function (el) {
        var v = el.value.trim();
        if (el.name === "name") { who = v; }
        return labelFor(el) + ": " + (v || "not given");
      }).join("\n") + "\n";

      var name = who;

      window.location.href =
        "mailto:" + SITE.CONTACT_EMAIL +
        "?subject=" + encodeURIComponent(kind + " enquiry" + (name ? " from " + name : "")) +
        "&body=" + encodeURIComponent(body);

      say("Your email app should be opening with the message ready. Press send and it comes straight to Aaron. If nothing happened, email " + SITE.CONTACT_EMAIL + " directly.");
    });
  });

  /* ---------- Current year in footers ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
