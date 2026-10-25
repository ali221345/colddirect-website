/* ColdDirect Voice — dark Ask Your Fault bar above the slider
 * Watermark: CD-UK-IP-2026-994821-VOICE-AI
 * Owner: ColdDirect Ltd, colddirect.co.uk
 */
(function () {
  "use strict";

  var TITLE = "Ask Your Fault";
  var LANG_BADGE = "Lang: Auto";
  var ASSISTANT_ID = "e31c40c7-a45b-4dff-833c-320c54250743";
  var SDK = "https://cdn.jsdelivr.net/npm/@vapi-ai/web/+esm";
  var CONFIG_URLS = [
    "/colddirect-vapi-config.aspx",
    "/api/colddirect-vapi-config.aspx"
  ];

  var vapi = null;
  var root, speakBtn, listenBtn, statusEl;
  var callActive = false;
  var callStarting = false;

  function css() {
    return [
      "#cd-voice-root{position:relative;z-index:40;width:100%;max-width:100vw;margin:0;font:600 12px/1.3 system-ui,-apple-system,Segoe UI,sans-serif;color:#e2e8f0;}",
      "#cd-voice-root *{box-sizing:border-box;}",
      "#cd-voice-bar{height:44px;padding:0 12px;display:flex;align-items:center;gap:8px;background:linear-gradient(90deg,#0b1120 0%,#0f172a 100%);border-bottom:1px solid #1e293b;width:100%;}",
      "#cd-voice-left{display:flex;align-items:center;gap:8px;min-width:0;flex:1;}",
      "#cd-voice-dot{width:8px;height:8px;border-radius:50%;background:#38bdf8;box-shadow:0 0 0 0 rgba(56,189,248,.7);animation:cdVoicePulse 1.6s infinite;flex:0 0 8px;}",
      "#cd-voice-root.is-busy #cd-voice-dot{background:#fbbf24;}",
      "#cd-voice-root.is-live #cd-voice-dot{background:#22c55e;}",
      "@keyframes cdVoicePulse{0%{box-shadow:0 0 0 0 rgba(56,189,248,.65);}70%{box-shadow:0 0 0 8px rgba(56,189,248,0);}100%{box-shadow:0 0 0 0 rgba(56,189,248,0);}}",
      "#cd-voice-title{min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:13px;font-weight:700;color:#f8fafc;}",
      "#cd-voice-controls{display:flex;align-items:center;gap:6px;flex:0 0 auto;}",
      "#cd-voice-root .cd-voice-langwrap{display:inline-flex;align-items:center;height:28px;padding:0 8px;border:1px solid #38bdf8;border-radius:6px;background:#082f49;color:#e0f2fe;font:700 11px/1 system-ui,sans-serif;}",
      "#cd-voice-root button.cd-voice-btn{height:28px;padding:0 10px;border:1px solid #334155;border-radius:6px;background:#1e293b;color:#f8fafc;font:700 10px/1 system-ui,sans-serif;letter-spacing:.04em;cursor:pointer;display:inline-flex;align-items:center;gap:4px;}",
      "#cd-voice-root button.cd-voice-btn.is-on{background:#0ea5e9;border-color:#38bdf8;color:#04111f;}",
      "#cd-voice-root button.cd-voice-btn#cd-voice-speak.is-on{background:#dc2626;border-color:#f87171;color:#fff;}",
      "#cd-voice-status{min-height:18px;margin:0;padding:6px 12px;background:#0f172a;color:#7dd3fc;font:500 11px/1.3 system-ui,sans-serif;border-bottom:1px solid #1e293b;}",
      "#cd-voice-status.is-error{color:#fca5a5;}",
      "@media (max-width:480px){#cd-voice-bar{padding:0 8px;gap:6px;}#cd-voice-title{font-size:12px;}#cd-voice-root button.cd-voice-btn{padding:0 7px;font-size:9.5px;letter-spacing:0;}#cd-voice-dot{display:none;}}"
    ].join("");
  }

  function html() {
    return (
      '<div id="cd-voice-bar">' +
        '<div id="cd-voice-left">' +
          '<span id="cd-voice-dot" aria-hidden="true"></span>' +
          '<span id="cd-voice-title">' + TITLE + "</span>" +
        "</div>" +
        '<div id="cd-voice-controls">' +
          '<span class="cd-voice-langwrap" aria-label="Language">' + LANG_BADGE + "</span>" +
          '<button type="button" class="cd-voice-btn" id="cd-voice-speak" aria-pressed="false">🎤 SPEAK</button>' +
          '<button type="button" class="cd-voice-btn" id="cd-voice-listen" aria-pressed="false">🔊 LISTEN</button>' +
        "</div>" +
      "</div>" +
      '<div id="cd-voice-status" role="status">Ready to start a voice conversation.</div>'
    );
  }

  function setStatus(kind, message) {
    if (!statusEl) return;
    statusEl.textContent = message || "";
    statusEl.classList.toggle("is-error", kind === "error");
    if (root) {
      root.classList.toggle("is-busy", kind === "connecting");
      root.classList.toggle("is-live", kind === "active");
    }
  }

  function setIdleState() {
    callActive = false;
    callStarting = false;
    if (speakBtn) {
      speakBtn.disabled = false;
      speakBtn.classList.remove("is-on");
      speakBtn.setAttribute("aria-pressed", "false");
      speakBtn.textContent = "🎤 SPEAK";
    }
    if (listenBtn) {
      listenBtn.disabled = false;
      listenBtn.classList.remove("is-on");
      listenBtn.setAttribute("aria-pressed", "false");
    }
    setStatus("", "Ready to start a voice conversation.");
  }

  function setLiveState() {
    callStarting = false;
    callActive = true;
    if (speakBtn) {
      speakBtn.disabled = false;
      speakBtn.classList.add("is-on");
      speakBtn.setAttribute("aria-pressed", "true");
      speakBtn.textContent = "⏹ END";
    }
    if (listenBtn) {
      listenBtn.disabled = false;
      listenBtn.classList.add("is-on");
      listenBtn.setAttribute("aria-pressed", "true");
    }
    setStatus("active", "Connected — speak in Persian or English.");
  }

  function keyLooksReady(key) {
    return !!(key && key !== "YOUR_PUBLIC_API_KEY" && key.length > 8);
  }

  function vapiCtor(mod) {
    var x = mod && (mod.default || mod.Vapi || mod);
    if (x && typeof x !== "function" && x.default) x = x.default;
    if (x && typeof x !== "function" && x.Vapi) x = x.Vapi;
    return typeof x === "function" ? x : null;
  }

  function fetchJson(url) {
    return fetch(url, { credentials: "same-origin", cache: "no-store" }).then(function (r) {
      if (!r.ok) throw new Error("config");
      return r.json();
    });
  }

  function resolvePublicKey() {
    if (keyLooksReady(window.CD_VAPI_PUBLIC_KEY)) {
      return Promise.resolve(String(window.CD_VAPI_PUBLIC_KEY).trim());
    }
    var chain = Promise.reject(new Error("start"));
    CONFIG_URLS.forEach(function (url) {
      chain = chain.catch(function () { return fetchJson(url); });
    });
    return chain.then(function (data) {
      var key = data && (data.publicKey || data.public_key || data.key);
      if (keyLooksReady(key)) return String(key).trim();
      throw new Error("missing-key");
    });
  }

  function startCall() {
    if (!vapi || callStarting) return;
    if (callActive) return;
    callStarting = true;
    if (speakBtn) speakBtn.disabled = true;
    if (listenBtn) listenBtn.disabled = true;
    setStatus("connecting", "Requesting microphone access…");
    Promise.resolve(vapi.start(ASSISTANT_ID)).catch(function () {
      setIdleState();
      setStatus("error", "The call could not start. Check microphone permission.");
    });
  }

  function stopCall() {
    if (!vapi) return;
    if (speakBtn) speakBtn.disabled = true;
    setStatus("connecting", "Ending the conversation…");
    try { vapi.stop(); } catch (e1) {}
  }

  function toggleSpeak() {
    if (callStarting) return;
    if (callActive) stopCall();
    else startCall();
  }

  function listenNow() {
    if (callStarting) return;
    if (callActive) {
      setStatus("active", "Listening — the engineer is on the line.");
      return;
    }
    startCall();
  }

  function bindCall(instance) {
    vapi = instance;
    speakBtn.addEventListener("click", toggleSpeak);
    listenBtn.addEventListener("click", listenNow);
    vapi.on("call-start", setLiveState);
    vapi.on("call-end", setIdleState);
    vapi.on("error", function () {
      setIdleState();
      setStatus("error", "A voice connection error occurred. Please try again.");
    });
  }

  function placeRoot(node) {
    var slider = document.getElementById("home-slider") || document.querySelector(".home-slider");
    if (slider && slider.parentNode) {
      slider.parentNode.insertBefore(node, slider);
      return;
    }
    var heroImg = document.querySelector(".hero img, .blackbox img, .page-header img, .inner-banner img");
    if (heroImg && heroImg.parentNode) {
      heroImg.parentNode.insertBefore(node, heroImg);
      return;
    }
    var hero = document.querySelector("section.hero, .blackbox, .page-header, .inner-banner");
    if (hero && hero.parentNode) {
      hero.parentNode.insertBefore(node, hero);
      return;
    }
    var header = document.querySelector(".cd-main-header, header.site, .site-header");
    if (header && header.parentNode) {
      if (header.nextSibling) header.parentNode.insertBefore(node, header.nextSibling);
      else header.parentNode.appendChild(node);
      return;
    }
    document.body.insertBefore(node, document.body.firstChild);
  }

  function mount() {
    if (document.getElementById("cd-voice-root")) return;
    document.documentElement.classList.remove("cd-voice-on");
    var float = document.querySelector(".vapi-widget");
    if (float && float.parentNode) float.parentNode.removeChild(float);
    var oldCss = document.getElementById("cd-voice-bar-css");
    if (oldCss && oldCss.parentNode) oldCss.parentNode.removeChild(oldCss);

    var style = document.createElement("style");
    style.id = "cd-voice-bar-css";
    style.textContent = css();
    document.head.appendChild(style);

    root = document.createElement("div");
    root.id = "cd-voice-root";
    root.setAttribute("data-cd-ip", "CD-UK-IP-2026-994821-VOICE-AI");
    root.setAttribute("role", "region");
    root.setAttribute("aria-label", TITLE);
    root.innerHTML = html();
    placeRoot(root);

    speakBtn = document.getElementById("cd-voice-speak");
    listenBtn = document.getElementById("cd-voice-listen");
    statusEl = document.getElementById("cd-voice-status");

    Promise.all([
      resolvePublicKey(),
      import(SDK)
    ]).then(function (parts) {
      var Vapi = vapiCtor(parts[1]);
      if (!Vapi) throw new Error("sdk");
      bindCall(new Vapi(parts[0]));
      setIdleState();
    }).catch(function (err) {
      var msg = String(err && err.message || err);
      if (msg === "missing-key" || msg.indexOf("config") !== -1) {
        setStatus("error", "Voice assistant is unavailable. Please refresh.");
      } else {
        setStatus("error", "The voice widget could not load. Please refresh and try again.");
      }
    });
  }

  if (document.body) mount();
  else document.addEventListener("DOMContentLoaded", mount);
})();
