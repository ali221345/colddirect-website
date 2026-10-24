/*!
 * Cold Direct Interactive SEO Service Popover / Hover Card Engine (V4.7)
 * Zero-CLS (position: fixed), 250ms hover bridge, desktop hover + mobile tap/focus support.
 */
(function () {
  "use strict";

  // Owner 2026-10-24: disable Dispatch Active / 60–90 Min hover popover sitewide.
  // Keep file so existing <script src="/js/cd-hover-card.js"> tags stay 200 OK.
  return;

  var SERVICE_CATALOG = {
    "commercial-fridge-repair": {
      title: "Commercial Fridge Repair London",
      desc: "24/7 F-Gas emergency repair for upright cabinets, undercounters, display chillers & kitchen fridges across London."
    },
    "fridge-repair-london": {
      title: "Commercial Fridge Repair London",
      desc: "Same-day trade refrigeration engineers for restaurants, pubs, hotels & supermarkets. Strictly B2B commercial only."
    },
    "commercial-freezer-repair": {
      title: "Commercial Freezer Repair London",
      desc: "Emergency breakdown response for upright gastronorm freezers, chest freezers & frozen storage cabinets (-18°C to -22°C)."
    },
    "freezer-repair-london": {
      title: "Commercial Freezer Repair London",
      desc: "Rapid diagnosis for defrost heater faults, iced evaporator coils, high-temperature alarms & compressor trips."
    },
    "cold-room-repair": {
      title: "Walk-In Cold Room Engineers London",
      desc: "24/7 walk-in cold room & chiller room repair: condensing units, expansion valves, Dixell/Carel panels & F-Gas regas."
    },
    "walk-in-chiller": {
      title: "Walk-In Chiller & Cold Room Repair",
      desc: "Emergency walk-in chiller servicing, evaporator fan replacement, refrigerant leak detection & HACCP certification."
    },
    "walk-in-freezer": {
      title: "Walk-In Freezer Room Repair London",
      desc: "Heavy-duty walk-in freezer plant diagnostics, electric defrost elements, door seals & Copeland/Danfoss packs."
    },
    "freezer-room-repair": {
      title: "Walk-In Freezer Room Engineers",
      desc: "24/7 emergency attendance for sub-zero walk-in freezer rooms across North & Central London and all M25 postcodes."
    },
    "supermarket-fridge-repair": {
      title: "Supermarket Multideck Chiller Repair",
      desc: "Early-morning & 24/7 callouts for supermarket multidecks, dairy aisles, glass-door merchandisers & remote packs."
    },
    "supermarket-freezer-repair": {
      title: "Supermarket Island & Display Freezer Repair",
      desc: "Same-day commercial repair for supermarket chest islands, glass-door freeze decks & remote refrigeration packs."
    },
    "dairy-cabinet-repair": {
      title: "Dairy Cabinet & Multideck Repair London",
      desc: "Rapid repair for milk multidecks, cheese serve-over counters & chilled retail display cases holding 1°C–5°C."
    },
    "multideck": {
      title: "Multideck Display Chiller Repair London",
      desc: "Fixing air-curtain collapse, blocked honeycombs, iced evaporators & failed fan motors on open-front multidecks."
    },
    "prep-fridge-repair": {
      title: "Bottle Cooler & Prep Fridge Repair",
      desc: "Same-day repair for stainless-steel saladettes, pizza prep counters & gastronorm chilled rails in hot kitchens."
    },
    "bottle-cooler": {
      title: "Bottle Cooler & Bar Fridge Repair",
      desc: "24/7 back-bar double-door & under-counter glass bottle cooler repair for pubs, bars, clubs & hospitality venues."
    },
    "cellar-cooler": {
      title: "Beer Cellar Cooling Repair London",
      desc: "Emergency pub & brewery cellar cooling system repair (J&E Hall, Marstair, Qualitair) holding steady 10°C–12°C."
    },
    "ice-machine-repair": {
      title: "Commercial Ice Machine Repair London",
      desc: "Same-day repair & descaling for Hoshizaki, Scotsman, Manitowoc & Ice-O-Matic commercial ice makers & flakers."
    },
    "air-conditioning-repair": {
      title: "24/7 Air Conditioning Service London",
      desc: "Commercial VRV/VRF, ceiling cassette & split AC breakdown repair (Daikin, Mitsubishi, Fujitsu, Toshiba)."
    },
    "catering-repair": {
      title: "Commercial Catering Fridge Repair",
      desc: "24/7 kitchen refrigeration & catering counter repairs for London restaurants, dark kitchens, schools & hotels."
    },
    "chiller-repair": {
      title: "Commercial Chiller Repair London",
      desc: "F-Gas certified engineers for display chillers, blast chillers, process chillers & glycol cooling loops."
    },
    "blast-chiller": {
      title: "Commercial Blast Chiller Repair London",
      desc: "Rapid repair for kitchen blast chillers & shock freezers to keep 90-minute chill cycles EHO & HACCP compliant."
    },
    "display-fridge": {
      title: "Commercial Display Fridge Repair",
      desc: "Same-day repair for glass-door drink merchandisers, patisserie counters, deli serve-overs & retail chillers."
    },
    "display-cabinet": {
      title: "Commercial Display Cabinet Repair",
      desc: "24/7 F-Gas service for retail & hospitality refrigerated display cabinets across Greater London."
    },
    "undercounter-fridge": {
      title: "Undercounter Commercial Fridge Repair",
      desc: "Fast first-visit repairs for commercial undercounter kitchen & bar fridges (Williams, Foster, Polar, True)."
    },
    "commercial-appliances-repair": {
      title: "Commercial Refrigeration & Appliances Hub",
      desc: "Complete 24/7 B2B commercial refrigeration, cold room, ice machine, cellar cooler & AC engineering across London."
    },
    "williams-": {
      title: "Williams Commercial Refrigeration Repair",
      desc: "Specialist London engineers for Williams Jade, Amber, Opal, Aztra counters, blast chillers & modular cold rooms."
    },
    "foster-": {
      title: "Foster Commercial Fridge & Freezer Repair",
      desc: "Same-day London repairs for Foster EcoPro G2/G3 cabinets, Xtra counters, blast chillers & walk-in cold rooms."
    },
    "true-": {
      title: "True Commercial Refrigeration Engineers",
      desc: "24/7 hydrocarbon (R290) & F-Gas repair for True T-Series uprights, pizza prep tables & bar bottle coolers."
    },
    "hoshizaki-": {
      title: "Hoshizaki Ice Machine & Fridge Repair",
      desc: "Specialist diagnostics for Hoshizaki IM/KM ice makers, water pumps, inlet solenoids & commercial cabinets."
    },
    "polar-": {
      title: "Polar Commercial Fridge & Counter Repair",
      desc: "Fast London repair for Polar C-Series, G-Series & U-Series commercial kitchen fridges, prep counters & bar coolers."
    },
    "gram-": {
      title: "Gram Commercial Refrigeration Repair",
      desc: "Same-day London engineer callouts for Gram Compact, Midi, Plus & Superior commercial cabinets and freezers."
    }
  };

  // V4.7: exact-path popover entries for the 9 money-keyword hub pages (checked before the substring catalog)
  var MONEY_PAGES = {
    "/fridge-repair-london/": { title: "Fridge Repair London", desc: "Same-day fridge repair & service for trade kitchens, shops, bars & hotels. Fixed-price diagnosis, F-Gas certified. Commercial only." },
    "/freezer-repair-london/": { title: "Freezer Repair London", desc: "Emergency freezer repair for upright, chest & kitchen freezers: defrost faults, iced evaporators, high-temp alarms, compressor trips." },
    "/commercial-fridge-repair-london/": { title: "Commercial Fridge Repair London", desc: "24/7 emergency repair for commercial uprights, undercounters, prep counters & display fridges across London. 60–90 min target response." },
    "/commercial-freezer-repair-london/": { title: "Commercial Freezer Repair London", desc: "Walk-in, chest & blast freezer repair: defrost heaters, compressors, controllers & F-Gas regas. 24/7 same-day engineers." },
    "/cold-room-repair-london/": { title: "Cold Room Repair London", desc: "24/7 walk-in chiller & freezer room repair: condensing units, expansion valves, Dixell/Carel/Eliwell controllers & F-Gas regas." },
    "/catering-repair-london/": { title: "Catering Repair London", desc: "Kitchen fridge, chiller & catering refrigeration repair for restaurants, hotels, schools & dark kitchens. 24/7 emergency cover." },
    "/commercial-appliances-repair-london/": { title: "Commercial Catering Repair London", desc: "Commercial catering & refrigeration appliances repair: cabinets, cold rooms, ice machines & blast chillers. Fixed-price diagnosis." },
    "/air-conditioning-repair-london/": { title: "Air Conditioning Repair London", desc: "Commercial split, cassette & VRV/VRF AC repair and servicing (Daikin, Mitsubishi). Fault codes, gas leaks & drain faults fixed." },
    "/cellar-cooler-repair-london/": { title: "Cellar Repair London", desc: "24/7 pub & bar cellar cooler repair for steady keg and cask temperatures. J&E Hall, Marstair & all commercial cellar plant." }
  };

  function normalizePath(href) {
    var p = (href || "").toLowerCase().replace(/^https?:\/\/(www\.)?colddirect\.co\.uk/, "").split("#")[0].split("?")[0];
    if (p.slice(-5) === ".html") p = p.slice(0, -5);
    if (p.slice(-1) !== "/") p += "/";
    return p;
  }

  function resolveServiceMeta(href, linkText) {
    var cleanHref = (href || "").toLowerCase();
    var exact = MONEY_PAGES[normalizePath(href)];
    if (exact) return exact;
    for (var key in SERVICE_CATALOG) {
      if (Object.prototype.hasOwnProperty.call(SERVICE_CATALOG, key)) {
        if (cleanHref.indexOf(key) !== -1) {
          return SERVICE_CATALOG[key];
        }
      }
    }
    var cleanText = (linkText || "").replace(/\s+/g, " ").trim();
    var title = cleanText.length > 4 && cleanText.length < 52
      ? cleanText.replace(/\b\w/g, function (c) { return c.toUpperCase(); })
      : "24/7 Commercial Refrigeration Repair London";
    return {
      title: title,
      desc: "Same-day F-Gas certified commercial refrigeration, cold room & AC engineers covering all London postcodes 24/7."
    };
  }

  function initHoverCardEngine() {
    if (document.getElementById("cd-hover-popover")) return;

    var scopes = document.querySelectorAll(
      "article, .article, .blog-content, main, .section .wrap, .seo-article, .cd-cro-section, .cd-blog-cta-box"
    );
    if (!scopes.length) return;

    var links = [];
    for (var i = 0; i < scopes.length; i++) {
      var anchorNodes = scopes[i].querySelectorAll("a[href]");
      for (var j = 0; j < anchorNodes.length; j++) {
        var a = anchorNodes[j];
        if (a.closest("header, nav, footer, .site-footer, .sticky-cta, .cta-row, .cd-trust-ctas, .phones")) continue;
        if (a.classList.contains("btn") || a.classList.contains("cta-office") || a.classList.contains("cta-mobile")) continue;
        var rawHref = a.getAttribute("href") || "";
        if (!rawHref || rawHref.indexOf("tel:") === 0 || rawHref.indexOf("mailto:") === 0 || rawHref.indexOf("#") === 0) continue;
        var isInternal = rawHref.charAt(0) === "/" || rawHref.indexOf("colddirect.co.uk") !== -1;
        if (!isInternal) continue;
        if (rawHref === "/" || rawHref === "/contact" || rawHref === "/contact/" || rawHref === "/blog" || rawHref === "/blog/") continue;

        var meta = resolveServiceMeta(rawHref, a.textContent);
        a.setAttribute("data-cd-popover", meta.title);
        a.setAttribute("data-cd-popover-desc", meta.desc);
        if (links.indexOf(a) === -1) links.push(a);
      }
    }

    if (!links.length) return;

    var card = document.createElement("aside");
    card.id = "cd-hover-popover";
    card.className = "cd-popover-card";
    card.setAttribute("role", "dialog");
    card.setAttribute("aria-label", "Cold Direct 24/7 Commercial Service Quick Dispatch");
    card.innerHTML =
      '<div class="cd-popover-badge">🟢 24/7 London Dispatch Active — 60–90 Min Arrival</div>' +
      '<div class="cd-popover-header">' +
        '<h4 class="cd-popover-title" id="cd-pop-title">Commercial Fridge Repair London</h4>' +
        '<button type="button" class="cd-popover-close" id="cd-pop-close" aria-label="Close preview">&times;</button>' +
      '</div>' +
      '<p class="cd-popover-desc" id="cd-pop-desc">Same-day F-Gas certified engineers across Greater London.</p>' +
      '<ul class="cd-popover-bullets">' +
        '<li><span class="cd-check">&#10003;</span> F-Gas Certified Engineers</li>' +
        '<li><span class="cd-check">&#10003;</span> OEM Van Stock (Carel, Danfoss, Embraco)</li>' +
        '<li><span class="cd-check">&#10003;</span> All London Postcodes (Strictly B2B)</li>' +
      '</ul>' +
      '<div class="cd-popover-actions">' +
        '<a href="tel:02039524822" class="cd-popover-btn-call">&#128222; 0203 952 4822</a>' +
        '<a href="tel:+447983759320" class="cd-popover-btn-mob">&#128241; 07983 759320</a>' +
        '<a href="/commercial-fridge-repair-london/" class="cd-popover-btn-hub" id="cd-pop-hub">Open Service Hub &rarr;</a>' +
      '</div>';

    document.body.appendChild(card);

    var titleEl = document.getElementById("cd-pop-title");
    var descEl = document.getElementById("cd-pop-desc");
    var hubEl = document.getElementById("cd-pop-hub");
    var closeBtn = document.getElementById("cd-pop-close");

    var hideTimer = null;
    var activeAnchor = null;

    function clearHideTimer() {
      if (hideTimer) {
        clearTimeout(hideTimer);
        hideTimer = null;
      }
    }

    function scheduleHide() {
      clearHideTimer();
      hideTimer = setTimeout(function () {
        card.classList.remove("is-visible");
        activeAnchor = null;
      }, 260);
    }

    function positionCard(anchor) {
      var rect = anchor.getBoundingClientRect();
      var cardWidth = 348;
      var cardHeight = card.offsetHeight || 235;
      var vw = window.innerWidth || document.documentElement.clientWidth;
      var vh = window.innerHeight || document.documentElement.clientHeight;

      var left = rect.left + rect.width / 2 - cardWidth / 2;
      if (left < 12) left = 12;
      if (left + cardWidth > vw - 12) left = Math.max(12, vw - cardWidth - 12);

      var top = rect.bottom + 10;
      if (top + cardHeight > vh - 12 && rect.top > cardHeight + 16) {
        top = rect.top - cardHeight - 10;
      } else if (top + cardHeight > vh - 12) {
        top = Math.max(12, vh - cardHeight - 12);
      }

      card.style.left = Math.round(left) + "px";
      card.style.top = Math.round(top) + "px";
    }

    function showCardFor(anchor) {
      clearHideTimer();
      activeAnchor = anchor;
      var title = anchor.getAttribute("data-cd-popover") || "Commercial Refrigeration Repair London";
      var desc = anchor.getAttribute("data-cd-popover-desc") || "";
      var href = anchor.getAttribute("href") || "/commercial-fridge-repair-london/";

      titleEl.textContent = title;
      descEl.textContent = desc;
      hubEl.setAttribute("href", href);

      positionCard(anchor);
      card.classList.add("is-visible");
    }

    for (var k = 0; k < links.length; k++) {
      (function (anchor) {
        anchor.addEventListener("mouseenter", function () {
          showCardFor(anchor);
        });
        anchor.addEventListener("mouseleave", function () {
          scheduleHide();
        });
        anchor.addEventListener("focus", function () {
          showCardFor(anchor);
        });
        anchor.addEventListener("blur", function () {
          scheduleHide();
        });
        anchor.addEventListener("touchstart", function (e) {
          if (activeAnchor !== anchor || !card.classList.contains("is-visible")) {
            e.preventDefault();
            showCardFor(anchor);
          }
        }, { passive: false });
      })(links[k]);
    }

    card.addEventListener("mouseenter", function () {
      clearHideTimer();
    });
    card.addEventListener("mouseleave", function () {
      scheduleHide();
    });

    if (closeBtn) {
      closeBtn.addEventListener("click", function () {
        clearHideTimer();
        card.classList.remove("is-visible");
        activeAnchor = null;
      });
    }

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && card.classList.contains("is-visible")) {
        clearHideTimer();
        card.classList.remove("is-visible");
        activeAnchor = null;
      }
    });

    document.addEventListener("touchstart", function (e) {
      if (!card.classList.contains("is-visible")) return;
      if (card.contains(e.target)) return;
      if (activeAnchor && activeAnchor.contains(e.target)) return;
      card.classList.remove("is-visible");
      activeAnchor = null;
    }, { passive: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initHoverCardEngine);
  } else {
    initHoverCardEngine();
  }
})();
