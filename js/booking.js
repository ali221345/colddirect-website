(function () {
  var FORM_HTML =
    '<form class="booking-form" data-booking-form novalidate>' +
    '<div class="hp"><label>Website</label><input type="text" name="website" tabindex="-1" autocomplete="off"></div>' +
    '<label for="bk-name">Name</label>' +
    '<input id="bk-name" name="name" type="text" required autocomplete="name">' +
    '<label for="bk-phone">Phone</label>' +
    '<input id="bk-phone" name="phone" type="tel" required autocomplete="tel">' +
    '<label for="bk-email">Email</label>' +
    '<input id="bk-email" name="email" type="email" required autocomplete="email">' +
    '<label for="bk-date">Date</label>' +
    '<input id="bk-date" name="date" type="date">' +
    '<label for="bk-message">Message / Product Interest</label>' +
    '<textarea id="bk-message" name="message" placeholder="Fridge, freezer, ice machine, site address…"></textarea>' +
    '<button class="btn" type="submit">Send booking</button>' +
    '<p class="booking-status" role="status"></p>' +
    "</form>";

  function uniqueIds(html, prefix) {
    return html
      .replace(/id="bk-/g, 'id="' + prefix + "-")
      .replace(/for="bk-/g, 'for="' + prefix + "-");
  }

  function bindForm(form) {
    if (!form || form.getAttribute("data-bound") === "1") return;
    form.setAttribute("data-bound", "1");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var status = form.querySelector(".booking-status");
      var payload = {
        name: form.querySelector('[name="name"]').value,
        phone: form.querySelector('[name="phone"]').value,
        email: form.querySelector('[name="email"]').value,
        date: form.querySelector('[name="date"]').value,
        message: form.querySelector('[name="message"]').value,
        website: form.querySelector('[name="website"]').value,
        page: window.location.href
      };
      status.className = "booking-status";
      if (!payload.name.trim() || !payload.phone.trim() || !payload.email.trim()) {
        status.className = "booking-status err";
        status.textContent = "Please enter your name, phone and email.";
        return;
      }
      status.textContent = "Sending…";
      fetch("book.php", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })
        .then(function (res) {
          return res.json().then(function (data) {
            return { ok: res.ok && data.ok, data: data };
          });
        })
        .then(function (result) {
          if (result.ok) {
            status.className = "booking-status ok";
            status.textContent = "Thanks! We will contact you shortly.";
            form.reset();
          } else {
            status.className = "booking-status err";
            status.textContent =
              (result.data && result.data.error) ||
              "Could not send. Email coldcom@hotmail.co.uk or call 07983 759320.";
          }
        })
        .catch(function () {
          status.className = "booking-status err";
          status.textContent =
            "Could not send. Email coldcom@hotmail.co.uk or call 07983 759320.";
        });
    });
  }

  function injectWidget() {
    if (document.querySelector(".booking-fab")) return;

    var fab = document.createElement("button");
    fab.type = "button";
    fab.className = "booking-fab";
    fab.setAttribute("aria-haspopup", "dialog");
    fab.innerHTML = 'Book<span class="booking-fab-extra"> a Consultation</span>';

    var modal = document.createElement("div");
    modal.className = "booking-modal";
    modal.setAttribute("role", "dialog");
    modal.setAttribute("aria-modal", "true");
    modal.setAttribute("aria-labelledby", "booking-modal-title");
    modal.innerHTML =
      '<div class="booking-modal-panel">' +
      '<button type="button" class="booking-modal-close" aria-label="Close">&times;</button>' +
      '<h2 id="booking-modal-title">Book a Consultation</h2>' +
      '<div class="booking-tabs">' +
      '<button type="button" class="active" data-tab="form">Request a call</button>' +
      '<button type="button" data-tab="cal">Pick a time</button>' +
      "</div>" +
      '<div class="booking-tab-form">' +
      uniqueIds(FORM_HTML, "modal") +
      "</div>" +
      '<div class="booking-calendly" data-calendly-host></div>' +
      "</div>";

    document.body.appendChild(fab);
    document.body.appendChild(modal);

    var closeBtn = modal.querySelector(".booking-modal-close");
    var formPane = modal.querySelector(".booking-tab-form");
    var calPane = modal.querySelector(".booking-calendly");
    var tabs = modal.querySelectorAll(".booking-tabs button");

    function openModal() {
      modal.classList.add("open");
    }
    function closeModal() {
      modal.classList.remove("open");
    }

    fab.addEventListener("click", openModal);
    closeBtn.addEventListener("click", closeModal);
    modal.addEventListener("click", function (e) {
      if (e.target === modal) closeModal();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeModal();
    });

    tabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        tabs.forEach(function (t) {
          t.classList.remove("active");
        });
        tab.classList.add("active");
        var which = tab.getAttribute("data-tab");
        if (which === "cal") {
          formPane.style.display = "none";
          calPane.style.display = "block";
          if (!calPane.querySelector("iframe")) {
            calPane.innerHTML =
              '<iframe title="Calendly" src="https://calendly.com/colddirect/consultation?hide_gdpr_banner=1"></iframe>';
          }
        } else {
          formPane.style.display = "block";
          calPane.style.display = "none";
        }
      });
    });

    bindForm(modal.querySelector("[data-booking-form]"));
  }

  document.querySelectorAll("[data-booking-form]").forEach(bindForm);
  injectWidget();
})();
