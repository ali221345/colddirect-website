/* ColdDirect Voice — Ask Your Fault bar in the hero, Vapi live transcript
 * Watermark: CD-UK-IP-2026-994821-VOICE-AI
 * Owner: ColdDirect Ltd, colddirect.co.uk
 */
(function () {
  "use strict";

  var TITLE = "Ask Your Fault";
  var LANG_BADGE = "Lang: Auto";
  var ASSISTANT_ID = "e31c40c7-a45b-4dff-833c-320c54250743";
  var SDK = "https://cdn.jsdelivr.net/npm/@vapi-ai/web/+esm";
  var REVIEW_HREF = "/write-a-review/";
  var CONFIG_URLS = [
    "/colddirect-vapi-config.aspx",
    "/api/colddirect-vapi-config.aspx"
  ];

  var vapi = null;
  var root, speakBtn, listenBtn, statusEl, logEl, ctaEl;
  var callActive = false;
  var callStarting = false;
  var liveUser = null;
  var liveBot = null;

  function css() {
    return [
      "#cd-voice-root{position:relative;z-index:50;width:100%;max-width:100vw;margin:0 0 14px;font:600 12px/1.3 system-ui,-apple-system,Segoe UI,sans-serif;color:#e2e8f0;}",
      "#cd-voice-root *{box-sizing:border-box;}",
      "#cd-voice-bar{min-height:44px;padding:6px 12px;display:flex;align-items:center;gap:8px;background:linear-gradient(90deg,#0b1120 0%,#0f172a 100%);border:1px solid #1e293b;border-radius:10px;width:100%;}",
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
      "#cd-voice-panel{display:none;margin-top:8px;padding:12px;background:#0b1120;border:1px solid #1e293b;border-radius:10px;}",
      "#cd-voice-root.is-open #cd-voice-panel{display:block;}",
      "#cd-voice-status{min-height:18px;margin:0 0 10px;color:#7dd3fc;font:500 12px/1.4 system-ui,sans-serif;}",
      "#cd-voice-status.is-error{color:#fca5a5;}",
      "#cd-voice-log{max-height:min(42vh,360px);overflow:auto;display:flex;flex-direction:column;gap:8px;padding:4px 2px 8px;}",
      "#cd-voice-log .cd-voice-row{max-width:92%;padding:8px 10px;border-radius:10px;font:400 14px/1.5 system-ui,sans-serif;white-space:pre-wrap;overflow-wrap:anywhere;}",
      "#cd-voice-log .cd-voice-row.is-user{align-self:flex-end;background:#1e3a5f;color:#e0f2fe;}",
      "#cd-voice-log .cd-voice-row.is-bot{align-self:flex-start;background:#111827;color:#f8fafc;border:1px solid #334155;}",
      "#cd-voice-log .cd-voice-row.is-partial{opacity:.78;}",
      "#cd-voice-log .cd-voice-who{display:block;margin:0 0 4px;font:700 10px/1 system-ui,sans-serif;letter-spacing:.04em;color:#93c5fd;}",
      "#cd-voice-cta{display:none;margin-top:12px;width:100%;min-height:48px;align-items:center;justify-content:center;gap:8px;padding:12px 14px;border:0;border-radius:10px;background:#14532d;color:#bbf7d0;font:700 14px/1.3 system-ui,sans-serif;text-decoration:none;cursor:pointer;}",
      "#cd-voice-root.is-open #cd-voice-cta{display:flex;}",
      "#cd-voice-cta.is-hot{background:#16a34a;color:#fff;box-shadow:0 0 0 3px rgba(34,197,94,.45);animation:cdVoiceCta 1.2s ease-in-out 3;}",
      "@keyframes cdVoiceCta{0%,100%{transform:scale(1);}50%{transform:scale(1.02);}}",
      "@media (max-width:480px){#cd-voice-bar{padding:6px 8px;gap:6px;}#cd-voice-title{font-size:12px;}#cd-voice-root button.cd-voice-btn{padding:0 7px;font-size:9.5px;letter-spacing:0;}#cd-voice-dot{display:none;}#cd-voice-cta{font-size:13px;}}"
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
      '<div id="cd-voice-panel">' +
        '<div id="cd-voice-status" role="status">Ready to start a voice conversation.</div>' +
        '<div id="cd-voice-log" aria-live="polite"></div>' +
        '<a id="cd-voice-cta" href="' + REVIEW_HREF + '">👍 Like &amp; Leave a 5-Star Review · ثبت لایک و نظر</a>' +
      "</div>"
    );
  }

  function hasPersian(text) {
    return /[\u0600-\u06FF]/.test(String(text || ""));
  }

  function applyDir(el, text) {
    if (!el) return;
    if (hasPersian(text)) {
      el.setAttribute("dir", "rtl");
      el.style.textAlign = "right";
    } else {
      el.setAttribute("dir", "ltr");
      el.style.textAlign = "left";
    }
  }

  function openPanel() {
    if (root) root.classList.add("is-open");
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

  function highlightCta(on) {
    if (!ctaEl) return;
    ctaEl.classList.toggle("is-hot", !!on);
  }

  function addRow(role, text, partial) {
    if (!logEl) return null;
    var row = document.createElement("div");
    row.className = "cd-voice-row " + (role === "user" ? "is-user" : "is-bot") + (partial ? " is-partial" : "");
    var who = document.createElement("span");
    who.className = "cd-voice-who";
    who.textContent = role === "user" ? "You" : "Head Engineer";
    var body = document.createElement("span");
    body.className = "cd-voice-txt";
    body.textContent = text || "";
    applyDir(body, text);
    row.appendChild(who);
    row.appendChild(body);
    logEl.appendChild(row);
    logEl.scrollTop = logEl.scrollHeight;
    return { row: row, body: body };
  }

  function upsertLive(role, text, final) {
    var cur = role === "user" ? liveUser : liveBot;
    if (!cur) {
      cur = addRow(role, text, !final);
      if (role === "user") liveUser = cur;
      else liveBot = cur;
    } else {
      cur.body.textContent = text || "";
      applyDir(cur.body, text);
      cur.row.classList.toggle("is-partial", !final);
    }
    if (final) {
      if (role === "user") liveUser = null;
      else liveBot = null;
    }
    if (logEl) logEl.scrollTop = logEl.scrollHeight;
  }

  function resetTranscript() {
    liveUser = null;
    liveBot = null;
    if (logEl) logEl.innerHTML = "";
    highlightCta(false);
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
    openPanel();
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
    openPanel();
    resetTranscript();
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
    openPanel();
    if (callActive) {
      setStatus("active", "Listening — the engineer is on the line.");
      return;
    }
    startCall();
  }

  function roleFrom(msg) {
    var r = String((msg && (msg.role || msg.speaker || (msg.message && msg.message.role))) || "").toLowerCase();
    if (r === "assistant" || r === "bot" || r === "agent") return "bot";
    if (r === "user" || r === "customer") return "user";
    return "";
  }

  function textFrom(msg) {
    if (!msg) return "";
    if (typeof msg.transcript === "string") return msg.transcript;
    if (typeof msg.text === "string") return msg.text;
    if (msg.message && typeof msg.message.content === "string") return msg.message.content;
    if (msg.message && typeof msg.message.transcript === "string") return msg.message.transcript;
    return "";
  }

  function handleConversation(msg) {
    var conv = msg.conversation || msg.messages || (msg.message && msg.message.messages);
    if (!Array.isArray(conv) || !logEl) return;
    logEl.innerHTML = "";
    liveUser = null;
    liveBot = null;
    conv.forEach(function (item) {
      var role = roleFrom(item) || "bot";
      var text = textFrom(item) || (typeof item.content === "string" ? item.content : "");
      if (text) addRow(role, text, false);
    });
  }

  function handleMessage(msg) {
    if (!msg) return;
    var type = String(msg.type || "").toLowerCase();
    if (type === "conversation-update") {
      handleConversation(msg);
      return;
    }
    if (type === "transcript" || type === "transcript-final" || type.indexOf("transcript") !== -1) {
      var role = roleFrom(msg) || (String(msg.transcriptType || "").indexOf("assistant") !== -1 ? "bot" : "user");
      var text = textFrom(msg);
      if (!text) return;
      var final = msg.transcriptType === "final" || type === "transcript-final" || msg.isFinal === true;
      upsertLive(role, text, final);
      if (final && role === "bot") highlightCta(true);
      return;
    }
    if (type === "speech-update") {
      var st = String(msg.status || msg.speechUpdateType || "").toLowerCase();
      if (st === "started" || st === "speech-started") {
        setStatus("active", "Head engineer is speaking…");
      }
      if (st === "stopped" || st === "speech-stopped") {
        highlightCta(true);
        setStatus("active", "If this helped, please leave a like and a 5-star review.");
      }
    }
  }

  function bindCall(instance) {
    vapi = instance;
    speakBtn.addEventListener("click", toggleSpeak);
    listenBtn.addEventListener("click", listenNow);
    vapi.on("call-start", setLiveState);
    vapi.on("call-end", function () {
      setIdleState();
      if (logEl && logEl.children.length) highlightCta(true);
    });
    vapi.on("message", handleMessage);
    vapi.on("error", function () {
      setIdleState();
      setStatus("error", "A voice connection error occurred. Please try again.");
    });
  }

  function placeRoot(node) {
    var header = document.querySelector(".cd-main-header, header.site, .site-header, header");
    var hero = document.querySelector("section.hero, .hero, .blackbox, .page-header, .inner-banner");
    if (hero && hero.parentNode) {
      hero.parentNode.insertBefore(node, hero);
      return;
    }
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
    logEl = document.getElementById("cd-voice-log");
    ctaEl = document.getElementById("cd-voice-cta");

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
      openPanel();
      if (msg === "missing-key" || msg.indexOf("config") !== -1) {
        setStatus("error", "Voice assistant is unavailable. Please refresh.");
      } else {
        setStatus("error", "The voice widget could not load. Please refresh and try again.");
      }
    });
  }

  function boot() { mount(); }
  if (document.body) boot();
  document.addEventListener("DOMContentLoaded", boot);
  window.addEventListener("load", boot);
  setTimeout(boot, 60);
  setTimeout(boot, 500);
})();
