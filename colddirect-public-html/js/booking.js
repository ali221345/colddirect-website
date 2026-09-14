(function () {
  var FORM_HTML =
    '<form class="booking-form" data-booking-form action="/booking.asp" method="POST" novalidate>' +
    '<div class="hp"><label>Website</label><input type="text" name="website" tabindex="-1" autocomplete="off"></div>' +
    '<input type="hidden" name="ajax" value="1">' +
    '<input type="hidden" name="service" value="">' +
    '<label for="bk-name">Name</label>' +
    '<input id="bk-name" name="name" type="text" required autocomplete="name">' +
    '<label for="bk-phone">Phone</label>' +
    '<input id="bk-phone" name="phone" type="tel" required autocomplete="tel">' +
    '<label for="bk-email">Email</label>' +
    '<input id="bk-email" name="email" type="email" required autocomplete="email">' +
    '<label for="bk-message">Message / Product Interest</label>' +
    '<textarea id="bk-message" name="message" placeholder="Fridge, freezer, ice machine, site address…"></textarea>' +
    '<button class="btn" type="submit">Send booking</button>' +
    '<p class="booking-status" role="status"></p>' +
    "</form>";

  var SUCCESS_MSG = "We will call you shortly on 07983 759320";
  var bookingModal = null;

  function uniqueIds(html, prefix) {
    return html
      .replace(/id="bk-/g, 'id="' + prefix + "-")
      .replace(/for="bk-/g, 'for="' + prefix + "-");
  }

  function openBookingModal(e) {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    if (!bookingModal) return false;
    bookingModal.classList.add("open");
    bookingModal.style.display = "flex";
    var first = bookingModal.querySelector('input[name="name"]');
    if (first) first.focus();
    return false;
  }

  function closeBookingModal() {
    if (!bookingModal) return;
    bookingModal.classList.remove("open");
    bookingModal.style.display = "none";
  }

  window.openBookingModal = openBookingModal;

  function bindForm(form) {
    if (!form || form.getAttribute("data-bound") === "1") return;
    form.setAttribute("data-bound", "1");
    form.setAttribute("action", "/booking.asp");
    form.setAttribute("method", "POST");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var status = form.querySelector(".booking-status");
      function field(name) {
        var el = form.querySelector('[name="' + name + '"]');
        return el ? el.value : "";
      }
      var serviceEl = form.querySelector('[name="service"]');
      if (serviceEl && !serviceEl.value) serviceEl.value = document.title;
      var payload = {
        name: field("name"),
        phone: field("phone"),
        email: field("email"),
        service: field("service") || document.title,
        message: field("message"),
        website: field("website"),
        page: window.location.href,
        ajax: "1"
      };
      status.className = "booking-status";
      if (!payload.name.trim() || !payload.phone.trim() || !payload.email.trim()) {
        status.className = "booking-status err";
        status.textContent = "Please enter your name, phone and email.";
        return;
      }
      status.textContent = "Sending…";
      fetch("/booking.asp", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams(payload).toString(),
        cache: "no-store",
        credentials: "same-origin"
      })
        .then(function (res) {
          return res.text().then(function (text) {
            var data = {};
            try {
              data = JSON.parse(text);
            } catch (err) {
              data = { ok: res.ok };
            }
            return { ok: res.ok && data.ok !== false, data: data };
          });
        })
        .then(function (result) {
          status.className = "booking-status ok";
          status.textContent =
            (result.data && result.data.message) || SUCCESS_MSG;
          form.reset();
        })
        .catch(function () {
          status.className = "booking-status ok";
          status.textContent = SUCCESS_MSG;
        });
    });
  }

  function isContactPageLink(el) {
    var text = (el.textContent || "").replace(/\s+/g, " ").trim().toLowerCase();
    return text === "contact" || text === "contact us";
  }

  function isBookingTrigger(el) {
    if (!el || !el.getAttribute) return false;
    if (el.getAttribute("data-open-booking") !== null) return true;
    if (el.classList && el.classList.contains("js-open-booking")) return true;
    var href = (el.getAttribute("href") || "").toLowerCase();
    if (href.indexOf("contact.asp") !== -1 && !isContactPageLink(el)) return true;
    var text = (el.textContent || "").replace(/\s+/g, " ").trim().toLowerCase();
    return (
      text.indexOf("request a booking") !== -1 ||
      text.indexOf("book a consultation") !== -1 ||
      text.indexOf("book a repair") !== -1
    );
  }

  function injectWidget() {
    if (document.querySelector(".booking-fab")) {
      bookingModal = document.getElementById("bookingModal") || document.querySelector(".booking-modal");
      return;
    }

    var fab = document.createElement("button");
    fab.type = "button";
    fab.className = "booking-fab";
    fab.setAttribute("aria-haspopup", "dialog");
    fab.innerHTML = 'Book<span class="booking-fab-extra"> a Consultation</span>';

    var modal = document.createElement("div");
    modal.id = "bookingModal";
    modal.className = "booking-modal";
    modal.setAttribute("role", "dialog");
    modal.setAttribute("aria-modal", "true");
    modal.setAttribute("aria-labelledby", "booking-modal-title");
    modal.innerHTML =
      '<div class="booking-modal-panel">' +
      '<button type="button" class="booking-modal-close" aria-label="Close">&times;</button>' +
      '<h2 id="booking-modal-title">Book a Consultation</h2>' +
      uniqueIds(FORM_HTML, "modal") +
      "</div>";

    document.body.appendChild(fab);
    document.body.appendChild(modal);
    bookingModal = modal;

    var closeBtn = modal.querySelector(".booking-modal-close");
    fab.addEventListener("click", openBookingModal);
    closeBtn.addEventListener("click", closeBookingModal);
    modal.addEventListener("click", function (e) {
      if (e.target === modal) closeBookingModal();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeBookingModal();
    });

    bindForm(modal.querySelector("[data-booking-form]"));
  }

  document.addEventListener("click", function (e) {
    var el = e.target.closest("a, button, [data-open-booking]");
    if (!el || el.classList.contains("booking-modal-close")) return;
    if (el.closest("[data-booking-form]")) return;
    if (!isBookingTrigger(el)) return;
    openBookingModal(e);
  });

  document.querySelectorAll("[data-booking-form]").forEach(bindForm);
  injectWidget();
})();
