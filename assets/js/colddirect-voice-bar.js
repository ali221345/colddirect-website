/* ColdDirect Voice — Vapi Ask Your Fault widget
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
  var panel, launcher, closeButton, callButton, callLabel, statusText, statusDot;
  var callActive = false;
  var callStarting = false;

  function css() {
    return [
      ".vapi-widget{position:fixed;right:24px;bottom:24px;z-index:999999;display:flex;flex-direction:column;align-items:flex-end;gap:12px;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,\"Segoe UI\",sans-serif;}",
      ".vapi-widget *,.vapi-widget *::before,.vapi-widget *::after{box-sizing:border-box;}",
      ".vapi-widget{--vapi-primary:#111827;--vapi-primary-hover:#1f2937;--vapi-accent:#22c55e;--vapi-surface:#ffffff;--vapi-text:#111827;--vapi-muted:#6b7280;--vapi-border:#e5e7eb;--vapi-shadow:0 18px 45px rgba(17,24,39,.18);}",
      ".vapi-panel{width:min(360px,calc(100vw - 32px));overflow:hidden;background:var(--vapi-surface);border:1px solid var(--vapi-border);border-radius:18px;box-shadow:var(--vapi-shadow);opacity:0;visibility:hidden;transform:translateY(12px) scale(.98);transform-origin:bottom right;transition:opacity 180ms ease,transform 180ms ease,visibility 180ms ease;}",
      ".vapi-panel.is-open{opacity:1;visibility:visible;transform:translateY(0) scale(1);}",
      ".vapi-header{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:16px 18px;color:#fff;background:var(--vapi-primary);}",
      ".vapi-heading{display:flex;align-items:center;gap:10px;min-width:0;}",
      ".vapi-heading h2{margin:0;overflow:hidden;font-size:16px;font-weight:700;line-height:1.2;text-overflow:ellipsis;white-space:nowrap;color:#fff;}",
      ".vapi-language-badge{flex:0 0 auto;padding:4px 8px;color:#fff;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.24);border-radius:999px;font-size:12px;font-weight:700;line-height:1;}",
      ".vapi-close{width:32px;height:32px;padding:0;color:#fff;background:transparent;border:0;border-radius:8px;cursor:pointer;font-size:22px;line-height:1;}",
      ".vapi-close:hover{background:rgba(255,255,255,.12);}",
      ".vapi-body{padding:22px 18px 18px;text-align:center;}",
      ".vapi-status-dot{width:12px;height:12px;margin:0 auto 12px;background:#94a3b8;border-radius:50%;}",
      ".vapi-status-dot.is-connecting{background:#f59e0b;animation:vapi-pulse 1s infinite;}",
      ".vapi-status-dot.is-active{background:var(--vapi-accent);animation:vapi-pulse 1.4s infinite;}",
      ".vapi-status-dot.is-error{background:#ef4444;}",
      "@keyframes vapi-pulse{0%,100%{box-shadow:0 0 0 0 currentColor;opacity:1;}50%{box-shadow:0 0 0 8px transparent;opacity:.75;}}",
      ".vapi-status{min-height:22px;margin:0 0 18px;color:var(--vapi-muted);font-size:14px;line-height:1.5;}",
      ".vapi-call-button{display:inline-flex;min-width:190px;min-height:48px;align-items:center;justify-content:center;gap:9px;padding:12px 18px;color:#fff;background:var(--vapi-primary);border:0;border-radius:12px;cursor:pointer;font:inherit;font-size:15px;font-weight:700;transition:background 150ms ease,transform 150ms ease;}",
      ".vapi-call-button:hover:not(:disabled){background:var(--vapi-primary-hover);transform:translateY(-1px);}",
      ".vapi-call-button:disabled{cursor:wait;opacity:.65;}",
      ".vapi-call-button.is-active{background:#dc2626;}",
      ".vapi-launcher{display:inline-flex;min-height:56px;align-items:center;justify-content:center;gap:10px;padding:0 20px;color:#fff;background:var(--vapi-primary);border:0;border-radius:999px;box-shadow:var(--vapi-shadow);cursor:pointer;font:inherit;font-size:15px;font-weight:750;transition:background 150ms ease,transform 150ms ease;}",
      ".vapi-launcher:hover{background:var(--vapi-primary-hover);transform:translateY(-2px);}",
      ".vapi-icon{width:20px;height:20px;fill:currentColor;}",
      "@media (max-width:520px){.vapi-widget{right:16px;bottom:16px;left:16px;align-items:stretch;}.vapi-panel{width:100%;}.vapi-launcher{width:100%;}}"
    ].join("");
  }

  function html() {
    return (
      '<section id="vapiPanel" class="vapi-panel" role="dialog" aria-labelledby="vapiTitle" aria-hidden="true">' +
        '<header class="vapi-header">' +
          '<div class="vapi-heading">' +
            '<h2 id="vapiTitle">' + TITLE + "</h2>" +
            '<span class="vapi-language-badge">' + LANG_BADGE + "</span>" +
          "</div>" +
          '<button id="vapiClose" class="vapi-close" type="button" aria-label="Close">&times;</button>' +
        "</header>" +
        '<div class="vapi-body">' +
          '<div id="vapiStatusDot" class="vapi-status-dot"></div>' +
          '<p id="vapiStatus" class="vapi-status" aria-live="polite">Ready to start a voice conversation.</p>' +
          '<button id="vapiCallButton" class="vapi-call-button" type="button">' +
            '<svg class="vapi-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M6.62 10.79a15.46 15.46 0 0 0 6.59 6.59l2.2-2.2a1 1 0 0 1 1.02-.24 11.36 11.36 0 0 0 3.57.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1C10.61 21 3 13.39 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1 11.36 11.36 0 0 0 .57 3.57 1 1 0 0 1-.25 1.02l-2.2 2.2Z"/></svg>' +
            '<span id="vapiCallLabel">' + TITLE + "</span>" +
          "</button>" +
        "</div>" +
      "</section>" +
      '<button id="vapiLauncher" class="vapi-launcher" type="button" aria-controls="vapiPanel" aria-expanded="false">' +
        '<svg class="vapi-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a9 9 0 0 0-9 9v3a3 3 0 0 0 3 3h1v-6H5a7 7 0 1 1 14 0h-2v7h-3v2h3a4 4 0 0 0 4-4v-5a9 9 0 0 0-9-9Z"/></svg>' +
        "<span>" + TITLE + "</span>" +
      "</button>"
    );
  }

  function openPanel() {
    panel.classList.add("is-open");
    panel.setAttribute("aria-hidden", "false");
    launcher.setAttribute("aria-expanded", "true");
  }

  function closePanel() {
    panel.classList.remove("is-open");
    panel.setAttribute("aria-hidden", "true");
    launcher.setAttribute("aria-expanded", "false");
  }

  function setStatus(state, message) {
    statusDot.className = "vapi-status-dot";
    if (state) statusDot.classList.add("is-" + state);
    statusText.textContent = message;
  }

  function setIdleState() {
    callActive = false;
    callStarting = false;
    callButton.disabled = false;
    callButton.classList.remove("is-active");
    callLabel.textContent = TITLE;
    setStatus("", "Ready to start a voice conversation.");
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

  function bindChrome() {
    launcher.addEventListener("click", function () {
      if (panel.classList.contains("is-open")) closePanel();
      else openPanel();
    });
    closeButton.addEventListener("click", closePanel);
  }

  function bindCall(instance) {
    vapi = instance;
    callButton.addEventListener("click", function () {
      if (callStarting) return;
      if (callActive) {
        callButton.disabled = true;
        callLabel.textContent = "Ending…";
        setStatus("connecting", "Ending the conversation…");
        try { vapi.stop(); } catch (e1) {}
        return;
      }
      callStarting = true;
      callButton.disabled = true;
      callLabel.textContent = "Connecting…";
      setStatus("connecting", "Requesting microphone access…");
      Promise.resolve(vapi.start(ASSISTANT_ID)).catch(function (error) {
        console.error("Unable to start Vapi call:", error);
        setIdleState();
        setStatus("error", "The call could not start. Check microphone permission and the Public API Key.");
      });
    });
    vapi.on("call-start", function () {
      callStarting = false;
      callActive = true;
      callButton.disabled = false;
      callButton.classList.add("is-active");
      callLabel.textContent = "End conversation";
      setStatus("active", "Connected — speak in Persian or English.");
    });
    vapi.on("call-end", function () { setIdleState(); });
    vapi.on("error", function (error) {
      console.error("Vapi error:", error);
      callStarting = false;
      callActive = false;
      callButton.disabled = false;
      callButton.classList.remove("is-active");
      callLabel.textContent = TITLE;
      setStatus("error", "A voice connection error occurred. Please try again.");
    });
  }

  function mount() {
    if (document.querySelector(".vapi-widget")) return;
    document.documentElement.classList.remove("cd-voice-on");
    var old = document.getElementById("cd-voice-root");
    if (old && old.parentNode) old.parentNode.removeChild(old);
    var oldCss = document.getElementById("cd-voice-bar-css");
    if (oldCss && oldCss.parentNode) oldCss.parentNode.removeChild(oldCss);

    var style = document.createElement("style");
    style.id = "cd-voice-bar-css";
    style.textContent = css();
    document.head.appendChild(style);

    var root = document.createElement("div");
    root.className = "vapi-widget";
    root.setAttribute("data-cd-ip", "CD-UK-IP-2026-994821-VOICE-AI");
    root.innerHTML = html();
    document.body.appendChild(root);

    panel = document.getElementById("vapiPanel");
    launcher = document.getElementById("vapiLauncher");
    closeButton = document.getElementById("vapiClose");
    callButton = document.getElementById("vapiCallButton");
    callLabel = document.getElementById("vapiCallLabel");
    statusText = document.getElementById("vapiStatus");
    statusDot = document.getElementById("vapiStatusDot");
    bindChrome();

    Promise.all([
      resolvePublicKey(),
      import(SDK)
    ]).then(function (parts) {
      var key = parts[0];
      var Vapi = vapiCtor(parts[1]);
      if (!Vapi) throw new Error("sdk");
      bindCall(new Vapi(key));
      setIdleState();
    }).catch(function (err) {
      var msg = String(err && err.message || err);
      if (msg === "missing-key" || msg.indexOf("config") !== -1) {
        setStatus("error", "Add your Vapi Public API Key to the HTML before using the widget.");
      } else {
        setStatus("error", "The voice widget could not load. Please refresh and try again.");
      }
    });
  }

  if (document.body) mount();
  else document.addEventListener("DOMContentLoaded", mount);
})();
