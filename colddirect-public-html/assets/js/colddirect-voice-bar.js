/* ColdDirect Voice — Ask Your Fault via ElevenLabs Conversational AI
 * Agent: agent_2901m5th5arfe9kamcec9ef2p42q
 * Watermark: CD-UK-IP-2026-994821-VOICE-AI
 * Owner: ColdDirect Ltd, colddirect.co.uk
 */
(function () {
  "use strict";

  var TITLE = "Ask Your Fault";
  var LANG_BADGE = "Lang: Auto";
  var MARK = "CD-UK-IP-2026-994821-VOICE-AI";
  var REVIEW_HREF = "/write-a-review/";
  var SPEAK_LABEL = "🎤 SPEAK";
  var STOP_LABEL = "⏹ STOP & SEND";
  var LISTEN_LABEL = "🔊 LISTEN";
  var STATUS_IDLE = "Tap SPEAK, then STOP & SEND when you finish.";
  var AGENT_ID = "agent_2901m5th5arfe9kamcec9ef2p42q";
  var TOKEN_URL = "/colddirect-elevenlabs-token.aspx";
  var TRANSCRIBE_URL = "/colddirect-voice-transcribe.aspx";
  var EL_LANGS = "en ja zh de hi fr ko pt pt-br it es id nl tr pl sv bg ro ar cs el fi ms da ta uk ru hu hr sk no vi tl af hy as az be bn bs ca et gl ka gu ha he is ga jv kn kk ky lv lt lb mk ml mr ne ps fa pa sr sd sl so sw te th ur cy";
  var SDK_URLS = [
    "https://cdn.jsdelivr.net/npm/@elevenlabs/client@0.15.2/+esm",
    "https://esm.sh/@elevenlabs/client@0.15.2",
    "https://unpkg.com/@elevenlabs/client@0.15.2/+esm",
    "https://cdn.jsdelivr.net/npm/@11labs/client@0.15.2/+esm"
  ];

  var host = String(location.hostname || "").toLowerCase();
  if (host && host !== "www.colddirect.co.uk" && host !== "colddirect.co.uk" && host !== "localhost" && host !== "127.0.0.1") return;

  var root, speakBtn, listenBtn, closeBtn, statusEl, logEl, ctaEl, meterEl;
  var userCollapsed = false;
  var liveUser = null;
  var liveBot = null;
  var conversation = null;
  var starting = false;
  var live = false;
  var agentSpoke = false;
  var meterTimer = null;
  var sdkPromise = null;
  var seq = 0;
  var spokenLang = "";
  var blockNativeAsr = true;
  var srRec = null;
  var micStream = null;
  var probePromise = null;
  var lastProbe = null;
  var sttSeq = 0;
  var lastSentUser = "";
  var contextSent = false;

  function css() {
    return [
      ".cd-main-header,.cd-header-inner,header.site,.site-header,.cd-topbar{overflow:visible !important;}",
      "#cd-voice-mobile-strip{display:none;}",
      "#cd-audio-dock{display:block !important;visibility:visible !important;opacity:1 !important;pointer-events:auto !important;position:absolute !important;top:12px !important;right:10px !important;left:auto !important;bottom:auto !important;z-index:401 !important;width:240px !important;max-width:min(240px,calc(100vw - 24px)) !important;}",
      "#cd-voice-root{position:fixed !important;top:10px !important;left:10px !important;right:auto !important;bottom:auto !important;z-index:99999 !important;width:max-content;max-width:min(420px,calc(100vw - 24px));margin:0;font:600 12px/1.3 system-ui,-apple-system,Segoe UI,sans-serif;color:#e2e8f0;}",
      "#cd-voice-root *{box-sizing:border-box;}",
      "#cd-voice-bar{display:flex;flex-wrap:wrap;align-items:center;gap:6px;padding:7px 9px;background:linear-gradient(90deg,#0b1120 0%,#0f172a 100%);border:1px solid #38bdf8;border-radius:10px;box-shadow:0 8px 22px rgba(15,23,42,.28);}",
      "#cd-voice-left{display:flex;align-items:center;gap:6px;min-width:0;}",
      "#cd-voice-dot{width:8px;height:8px;border-radius:50%;background:#22c55e;box-shadow:0 0 0 0 rgba(34,197,94,.7);animation:cdVoicePulse 1.6s infinite;flex:0 0 8px;}",
      "#cd-voice-root.is-busy #cd-voice-dot{background:#fbbf24;}",
      "#cd-voice-root.is-live #cd-voice-dot{background:#ef4444;}",
      "@keyframes cdVoicePulse{0%{box-shadow:0 0 0 0 rgba(34,197,94,.65);}70%{box-shadow:0 0 0 8px rgba(34,197,94,0);}100%{box-shadow:0 0 0 0 rgba(34,197,94,0);}}",
      "#cd-voice-title{white-space:nowrap;font-size:12px;font-weight:800;color:#f8fafc;}",
      "#cd-voice-controls{display:flex;align-items:center;gap:5px;flex:0 0 auto;flex-wrap:wrap;}",
      "#cd-voice-root .cd-voice-langwrap{display:inline-flex;align-items:center;height:26px;padding:0 7px;border:1px solid #38bdf8;border-radius:6px;background:#082f49;color:#e0f2fe;font:700 10px/1 system-ui,sans-serif;white-space:nowrap;}",
      "#cd-voice-root button.cd-voice-btn{height:26px;padding:0 8px;border:1px solid #334155;border-radius:6px;background:#1e293b;color:#f8fafc;font:700 10px/1 system-ui,sans-serif;letter-spacing:.03em;cursor:pointer;display:inline-flex;align-items:center;gap:3px;white-space:nowrap;}",
      "#cd-voice-root button.cd-voice-btn.is-on{background:#0ea5e9;border-color:#38bdf8;color:#04111f;}",
      "#cd-voice-root button.cd-voice-btn#cd-voice-speak.is-on{background:#dc2626;border-color:#f87171;color:#fff;animation:cdVoicePulse 1s infinite;}",
      "#cd-voice-panel{display:none;position:absolute;left:0;top:calc(100% + 8px);z-index:100000;width:min(420px,calc(100vw - 20px));padding:12px;background:#0b1120;border:1px solid #1e293b;border-radius:12px;box-shadow:0 18px 40px rgba(2,6,23,.35);}",
      "#cd-voice-root.is-open #cd-voice-panel{display:block;animation:cdVoiceDrop .18s ease forwards;}",
      "@keyframes cdVoiceDrop{from{opacity:0;transform:translateY(-8px);}to{opacity:1;transform:translateY(0);}}",
      "#cd-voice-panel-head{display:flex;align-items:flex-start;gap:8px;margin:0 0 8px;}",
      "#cd-voice-status{flex:1;min-height:18px;margin:0;color:#7dd3fc;font:500 12px/1.4 system-ui,sans-serif;}",
      "#cd-voice-status.is-error{color:#fca5a5;}",
      "#cd-voice-close{flex:0 0 28px;width:28px;height:28px;padding:0;border:1px solid #334155;border-radius:6px;background:#1e293b;color:#f8fafc;font:700 16px/1 system-ui,sans-serif;cursor:pointer;}",
      "#cd-voice-meter{height:4px;background:#1e293b;border-radius:2px;margin:0 0 8px;overflow:hidden;}",
      "#cd-voice-meter>i{display:block;height:100%;width:0;background:#22c55e;}",
      "#cd-voice-log{max-height:min(42vh,320px);overflow:auto;-webkit-overflow-scrolling:touch;display:flex;flex-direction:column;gap:8px;padding:4px 2px 8px;}",
      "#cd-voice-log .cd-voice-row{max-width:92%;padding:8px 10px;border-radius:10px;font:400 14px/1.5 system-ui,sans-serif;white-space:pre-wrap;overflow-wrap:anywhere;}",
      "#cd-voice-log .cd-voice-row.is-user{align-self:flex-end;background:#1e3a5f;color:#e0f2fe;}",
      "#cd-voice-log .cd-voice-row.is-bot{align-self:flex-start;background:#111827;color:#f8fafc;border:1px solid #334155;}",
      "#cd-voice-log .cd-voice-row.is-partial{opacity:.78;}",
      "#cd-voice-log .cd-voice-who{display:block;margin:0 0 4px;font:700 10px/1 system-ui,sans-serif;letter-spacing:.04em;color:#93c5fd;}",
      "#cd-voice-log .cd-voice-txt a{color:#7dd3fc;text-decoration:underline;font-weight:700;}",
      "#cd-voice-cta{display:flex;margin-top:12px;width:100%;min-height:48px;align-items:center;justify-content:center;gap:8px;padding:12px 14px;border:0;border-radius:10px;background:linear-gradient(180deg,#16a34a 0%,#15803d 100%);color:#fff;font:800 13px/1.3 system-ui,sans-serif;text-decoration:none;cursor:pointer;box-shadow:0 0 0 2px rgba(74,222,128,.55),0 8px 18px rgba(22,163,74,.38);}",
      "#cd-voice-cta.is-hot{background:#22c55e;color:#052e16;box-shadow:0 0 0 4px rgba(74,222,128,.75),0 0 28px rgba(34,197,94,.7);animation:cdVoiceCta .9s ease-in-out infinite;}",
      "@keyframes cdVoiceCta{0%,100%{transform:scale(1);}50%{transform:scale(1.045);}}",
      "elevenlabs-convai,.vapi-widget{display:none !important;}",
      "@media (min-width:769px){#cd-voice-root{max-width:min(420px,calc(100vw - 270px));}#cd-voice-mobile-strip{display:none !important;}}",
      "@media (max-width:768px){" +
        ".cd-main-header{height:auto !important;overflow:visible !important;}" +
        ".cd-header-inner{height:auto !important;min-height:64px !important;}" +
        "#cd-voice-mobile-strip{display:flex !important;align-items:stretch;justify-content:space-between;gap:6px;width:100%;max-width:100%;box-sizing:border-box;padding:6px;background:#0f172a;position:relative;z-index:120;overflow:visible;}" +
        "#cd-audio-dock{position:relative !important;top:auto !important;right:auto !important;left:auto !important;bottom:auto !important;float:none !important;width:auto !important;max-width:none !important;flex:1 1 40%;min-width:0;margin:0 !important;z-index:1 !important;max-height:none !important;overflow:hidden !important;box-sizing:border-box;}" +
        "#cd-voice-root{position:static !important;top:auto !important;left:auto !important;right:auto !important;bottom:auto !important;width:auto !important;max-width:100% !important;flex:1 1 52%;min-width:0;box-sizing:border-box;z-index:2 !important;margin:0;overflow:visible;}" +
        "#cd-voice-bar{display:flex;flex-direction:column;align-items:stretch;flex-wrap:nowrap;white-space:normal;width:100%;max-width:100%;box-sizing:border-box;gap:4px;padding:6px;overflow:hidden;}" +
        "#cd-voice-left{width:100%;min-width:0;}" +
        "#cd-voice-title{font-size:11px;}" +
        "#cd-voice-controls{display:flex;flex-wrap:nowrap;align-items:center;width:100%;max-width:100%;min-width:0;gap:4px;box-sizing:border-box;}" +
        "#cd-voice-root .cd-voice-langwrap{flex:1 1 0;min-width:0;height:28px;padding:0 4px;font-size:9px;justify-content:center;overflow:hidden;text-overflow:ellipsis;}" +
        "#cd-voice-root button.cd-voice-btn{flex:1 1 0;min-width:0;height:28px;min-height:28px;padding:0 4px;font-size:9px;justify-content:center;}" +
        "#cd-voice-mobile-strip #cd-voice-panel{position:absolute;left:8px;right:8px;width:auto;max-width:none;top:100%;margin-top:6px;max-height:min(70vh,520px);overflow:auto;z-index:200;box-sizing:border-box;}" +
      "}"
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
          '<button type="button" class="cd-voice-btn" id="cd-voice-speak" aria-pressed="false">' + SPEAK_LABEL + "</button>" +
          '<button type="button" class="cd-voice-btn" id="cd-voice-listen" aria-pressed="false">' + LISTEN_LABEL + "</button>" +
        "</div>" +
      "</div>" +
      '<div id="cd-voice-panel">' +
        '<div id="cd-voice-panel-head">' +
          '<div id="cd-voice-status" role="status">' + STATUS_IDLE + "</div>" +
          '<button type="button" id="cd-voice-close" aria-label="Close transcript">✕</button>' +
        "</div>" +
        '<div id="cd-voice-meter" hidden><i></i></div>' +
        '<div id="cd-voice-log" aria-live="polite"></div>' +
        '<a id="cd-voice-cta" href="' + REVIEW_HREF + '">👍 Like &amp; Leave a 5-Star Review</a>' +
      "</div>"
    );
  }

  function isRtl(text) {
    return /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]/.test(String(text || ""));
  }

  function applyDir(el, text) {
    if (!el) return;
    if (isRtl(text)) {
      el.setAttribute("dir", "rtl");
      el.style.textAlign = "right";
    } else {
      el.setAttribute("dir", "ltr");
      el.style.textAlign = "left";
    }
  }

  function telHref(display) {
    var d = String(display).replace(/\s+/g, "");
    if (d.indexOf("07983") === 0) return "tel:+447983759320";
    if (d.indexOf("0203") === 0) return "tel:+442039524822";
    if (d.indexOf("0800") === 0) return "tel:08001123427";
    return "tel:" + d;
  }

  function setTranscriptBody(el, text, clickable) {
    el.textContent = "";
    applyDir(el, text);
    if (!clickable) {
      el.textContent = text;
      return;
    }
    var re = /(07983\s*759320|0203\s*952\s*4822|0800\s*112\s*3427)/g;
    var last = 0;
    var m;
    var shown = false;
    while ((m = re.exec(text))) {
      if (m.index > last) el.appendChild(document.createTextNode(text.slice(last, m.index)));
      var a = document.createElement("a");
      a.href = telHref(m[0]);
      a.textContent = m[0];
      el.appendChild(a);
      last = m.index + m[0].length;
      shown = true;
    }
    if (last < text.length) el.appendChild(document.createTextNode(text.slice(last)));
    if (!shown && !el.childNodes.length) el.textContent = text;
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
    setTranscriptBody(body, text || "", role === "bot");
    row.appendChild(who);
    row.appendChild(body);
    logEl.appendChild(row);
    logEl.scrollTop = logEl.scrollHeight;
    return { row: row, body: body };
  }

  function upsertLive(role, text, final) {
    text = String(text || "");
    var cur = role === "user" ? liveUser : liveBot;
    if (!cur) {
      cur = addRow(role, text, !final);
      if (role === "user") liveUser = cur;
      else liveBot = cur;
    } else {
      setTranscriptBody(cur.body, text, role === "bot");
      cur.row.classList.toggle("is-partial", !final);
    }
    if (final) {
      if (role === "user") liveUser = null;
      else liveBot = null;
    }
    if (logEl) logEl.scrollTop = logEl.scrollHeight;
  }

  function openPanel(force) {
    if (userCollapsed && !force) return;
    if (root) root.classList.add("is-open");
  }

  function closePanel() {
    userCollapsed = true;
    if (root) root.classList.remove("is-open");
  }

  function setSpeakUi(on) {
    if (!speakBtn) return;
    speakBtn.classList.toggle("is-on", !!on);
    speakBtn.setAttribute("aria-pressed", on ? "true" : "false");
    speakBtn.textContent = on ? STOP_LABEL : SPEAK_LABEL;
  }

  function setStatus(kind, message) {
    if (arguments.length === 1) {
      message = kind;
      kind = "";
    }
    if (!statusEl) return;
    statusEl.textContent = message || "";
    statusEl.classList.toggle("is-error", kind === "error");
    if (root) {
      root.classList.toggle("is-busy", kind === "connecting" || starting);
      root.classList.toggle("is-live", kind === "active" || live);
    }
  }

  function highlightCta(on) {
    if (!ctaEl) return;
    openPanel();
    if (!on) {
      ctaEl.classList.remove("is-hot");
      return;
    }
    ctaEl.classList.remove("is-hot");
    void ctaEl.offsetWidth;
    ctaEl.classList.add("is-hot");
    try { ctaEl.scrollIntoView({ block: "nearest", behavior: "smooth" }); } catch (e1) {}
  }

  function unlockAudio() {
    try {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (AC) {
        if (!window.__cdPlayCtx) window.__cdPlayCtx = new AC();
        if (window.__cdPlayCtx.state === "suspended") window.__cdPlayCtx.resume();
      }
    } catch (e1) {}
  }

  function welcomeAudio() {
    return document.querySelector("#cd-audio-dock audio, #cd-hero-audio, audio.cd-welcome-audio");
  }

  function setListenUi(on) {
    if (!listenBtn) return;
    listenBtn.classList.toggle("is-on", !!on);
    listenBtn.setAttribute("aria-pressed", on ? "true" : "false");
  }

  function playWelcome() {
    unlockAudio();
    var a = welcomeAudio();
    if (!a) {
      openPanel(true);
      setStatus("error", "Welcome audio is not available on this page.");
      return;
    }
    if (!a.paused && !a.ended) {
      try { a.pause(); } catch (e1) {}
      setListenUi(false);
      return;
    }
    try { a.currentTime = 0; } catch (e2) {}
    var p = a.play();
    setListenUi(true);
    a.onended = function () { setListenUi(false); };
    a.onpause = function () { if (a.paused) setListenUi(false); };
    if (p && typeof p.catch === "function") {
      p.catch(function () { setListenUi(false); });
    }
  }

  function isMobileVoice() {
    return window.matchMedia && window.matchMedia("(max-width: 768px)").matches;
  }

  function restoreAudioDock() {
    if (document.getElementById("cd-audio-dock-restore")) return;
    try {
      var style = document.createElement("style");
      style.id = "cd-audio-dock-restore";
      style.textContent = [
        "#cd-audio-dock{display:block !important;visibility:visible !important;opacity:1 !important;pointer-events:auto !important;}",
        "@media (min-width:769px){#cd-audio-dock{position:absolute !important;top:12px !important;right:10px !important;left:auto !important;bottom:auto !important;z-index:401 !important;width:240px !important;max-width:min(240px,calc(100vw - 24px)) !important;}}",
        "@media (max-width:768px){#cd-audio-dock{position:relative !important;top:auto !important;right:auto !important;left:auto !important;bottom:auto !important;width:auto !important;max-width:none !important;flex:1 1 40%;min-width:0;margin:0 !important;z-index:1 !important;overflow:hidden !important;box-sizing:border-box;}}"
      ].join("");
      (document.body || document.documentElement).appendChild(style);
    } catch (e1) {}
  }

  function placeRoot(node) {
    if (!node) return;
    var dock = document.getElementById("cd-audio-dock");
    var header = document.querySelector(".cd-main-header, header.site, .site-header, header");
    var strip = document.getElementById("cd-voice-mobile-strip");
    if (isMobileVoice() && header) {
      if (!strip) {
        strip = document.createElement("div");
        strip.id = "cd-voice-mobile-strip";
      }
      if (strip.parentNode !== header) header.appendChild(strip);
      if (dock && dock.parentNode !== strip) strip.insertBefore(dock, strip.firstChild);
      if (node.parentNode !== strip) strip.appendChild(node);
      if (dock && node && dock.nextSibling !== node) strip.insertBefore(dock, node);
      return;
    }
    if (strip && strip.parentNode) {
      if (dock && header) header.appendChild(dock);
      strip.parentNode.removeChild(strip);
    }
    if (document.body && node.parentNode !== document.body) document.body.appendChild(node);
    if (dock && header && dock.parentNode !== header) header.appendChild(dock);
  }

  function syncVoicePlacement() {
    if (root) placeRoot(root);
    restoreAudioDock();
  }

  function loadSdk() {
    if (sdkPromise) return sdkPromise;
    sdkPromise = (function next(i) {
      if (i >= SDK_URLS.length) return Promise.reject(new Error("ElevenLabs SDK failed to load"));
      return import(SDK_URLS[i]).then(function (mod) {
        var C = (mod && (mod.Conversation || (mod.default && mod.default.Conversation) || mod.default)) || null;
        if (C && typeof C.startSession === "function") return C;
        return next(i + 1);
      }).catch(function () { return next(i + 1); });
    })(0);
    return sdkPromise;
  }

  function messageText(payload) {
    if (payload == null) return "";
    if (typeof payload === "string") return payload;
    return String(payload.message || payload.text || payload.transcript || payload.content || "");
  }

  function messageRole(payload) {
    var src = "";
    if (payload && typeof payload === "object") src = String(payload.source || payload.role || payload.type || payload.sender || "");
    if (/user|human/i.test(src)) return "user";
    return "bot";
  }

  function messageFinal(payload) {
    if (!payload || typeof payload !== "object") return true;
    if (payload.is_final === false || payload.isFinal === false) return false;
    if (payload.tentative === true || payload.interim === true) return false;
    return true;
  }

  function onAgentMessage(payload) {
    var text = messageText(payload).replace(/\s+/g, " ").trim();
    if (!text) return;
    var role = messageRole(payload);
    if (role === "user") return;
    upsertLive(role, text, messageFinal(payload));
  }

  function toElLang(code) {
    var raw = String(code || "").toLowerCase().replace(/_/g, "-").trim();
    var base = raw.split("-")[0];
    var aliases = { fas: "fa", per: "fa", farsi: "fa", persian: "fa", fil: "tl", tgl: "tl", cmn: "zh", yue: "zh", iw: "he", nb: "no", nn: "no" };
    if (aliases[raw]) base = aliases[raw];
    else if (aliases[base]) base = aliases[base];
    if (raw === "pt-br" || (base === "pt" && /br/.test(raw))) return "pt-br";
    if (raw === "zh-cn" || raw === "zh-tw" || raw === "zh-hans" || raw === "zh-hant") return "zh";
    return EL_LANGS.split(" ").indexOf(base) >= 0 ? base : "";
  }

  function toSrLang(code) {
    var el = toElLang(code);
    var m = {
      fa: "fa-IR", ar: "ar-SA", tr: "tr-TR", zh: "zh-CN", en: "en-GB", hi: "hi-IN",
      ur: "ur-PK", ps: "ps-AF", de: "de-DE", fr: "fr-FR", es: "es-ES", it: "it-IT",
      pt: "pt-PT", "pt-br": "pt-BR", ru: "ru-RU", uk: "uk-UA", nl: "nl-NL", pl: "pl-PL",
      ja: "ja-JP", ko: "ko-KR", tl: "fil-PH", he: "he-IL", bn: "bn-BD", pa: "pa-IN"
    };
    return m[el] || "";
  }

  function isLatinMostly(text) {
    var s = String(text || "");
    var latin = (s.match(/[A-Za-z]/g) || []).length;
    var other = (s.match(/[^\sA-Za-z0-9.,!?'"+\-:/()]/g) || []).length;
    return latin >= 8 && latin > other * 2;
  }

  function shouldIgnoreEnglishAsr(text) {
    if (!blockNativeAsr) return false;
    if (isRtl(text)) return false;
    if (spokenLang && spokenLang !== "en" && isLatinMostly(text)) return true;
    return false;
  }

  function encodeWav(chunks, sampleRate) {
    var n = 0;
    var i;
    var c;
    for (c = 0; c < chunks.length; c++) n += chunks[c].length;
    var buf = new ArrayBuffer(44 + n * 2);
    var v = new DataView(buf);
    function wstr(off, s) {
      for (i = 0; i < s.length; i++) v.setUint8(off + i, s.charCodeAt(i));
    }
    wstr(0, "RIFF");
    v.setUint32(4, 36 + n * 2, true);
    wstr(8, "WAVE");
    wstr(12, "fmt ");
    v.setUint32(16, 16, true);
    v.setUint16(20, 1, true);
    v.setUint16(22, 1, true);
    v.setUint32(24, sampleRate, true);
    v.setUint32(28, sampleRate * 2, true);
    v.setUint16(32, 2, true);
    v.setUint16(34, 16, true);
    wstr(36, "data");
    v.setUint32(40, n * 2, true);
    var o = 44;
    for (c = 0; c < chunks.length; c++) {
      var a = chunks[c];
      for (i = 0; i < a.length; i++, o += 2) {
        var s = Math.max(-1, Math.min(1, a[i]));
        v.setInt16(o, s < 0 ? s * 0x8000 : s * 0x7fff, true);
      }
    }
    var bytes = new Uint8Array(buf);
    var bin = "";
    var step = 0x8000;
    for (i = 0; i < bytes.length; i += step) {
      bin += String.fromCharCode.apply(null, bytes.subarray(i, Math.min(i + step, bytes.length)));
    }
    return btoa(bin);
  }

  function captureWav(stream, ms) {
    return new Promise(function (resolve, reject) {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return reject(new Error("no AudioContext"));
      var ctx = window.__cdPlayCtx || new AC();
      if (ctx.state === "suspended") ctx.resume();
      var src = ctx.createMediaStreamSource(stream);
      var proc = ctx.createScriptProcessor(4096, 1, 1);
      var gain = ctx.createGain();
      gain.gain.value = 0;
      var chunks = [];
      proc.onaudioprocess = function (ev) {
        chunks.push(new Float32Array(ev.inputBuffer.getChannelData(0)));
      };
      src.connect(proc);
      proc.connect(gain);
      gain.connect(ctx.destination);
      setTimeout(function () {
        try { proc.disconnect(); } catch (e1) {}
        try { src.disconnect(); } catch (e2) {}
        try { gain.disconnect(); } catch (e3) {}
        if (!chunks.length) return reject(new Error("no audio"));
        resolve({ b64: encodeWav(chunks, ctx.sampleRate || 48000), mime: "audio/wav" });
      }, ms);
    });
  }

  function transcribeOriginal(stream) {
    return captureWav(stream, 1400).then(function (clip) {
      return fetch(TRANSCRIBE_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        cache: "no-store",
        body: JSON.stringify({ audio_base64: clip.b64, mime: clip.mime, mode: "transcribe", translate: false })
      });
    }).then(function (r) { return r.json().catch(function () { return {}; }); }).then(function (j) {
      if (!j || j.ok === false) return null;
      var transcript = String(j.transcript || "").replace(/\s+/g, " ").trim();
      if (!transcript) return null;
      return { language: toElLang(j.language) || "", transcript: transcript, mode: "transcribe" };
    });
  }

  function stopSpeechRec() {
    if (!srRec) return;
    try { srRec.onresult = null; srRec.onend = null; srRec.stop(); } catch (e1) {}
    srRec = null;
  }

  function startSpeechRec(lang) {
    var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    var locale = toSrLang(lang);
    if (!SR || !locale) return;
    if (locale.toLowerCase().indexOf("en-us") === 0) locale = "en-GB";
    if (srRec && String(srRec.lang || "") === locale) return;
    stopSpeechRec();
    var rec = new SR();
    srRec = rec;
    rec.lang = locale;
    rec.continuous = true;
    rec.interimResults = true;
    rec.maxAlternatives = 1;
    rec.onresult = function (ev) {
      var t = "";
      var final = false;
      for (var i = ev.resultIndex; i < ev.results.length; i++) {
        t += ev.results[i][0].transcript || "";
        if (ev.results[i].isFinal) final = true;
      }
      t = String(t).replace(/\s+/g, " ").trim();
      if (!t || shouldIgnoreEnglishAsr(t)) return;
      upsertLive("user", t, final);
      if (final) sendOriginalUser(t);
    };
    rec.onend = function () {
      if (srRec === rec && live && blockNativeAsr) {
        try { rec.start(); } catch (e2) {}
      }
    };
    try { rec.start(); } catch (e3) {}
  }

  function muteElAsr() {
    blockNativeAsr = true;
    if (conversation && typeof conversation.setMicMuted === "function") {
      try { conversation.setMicMuted(true); } catch (e1) {}
    }
  }

  function sendTranscribeContext() {
    if (contextSent || !conversation || typeof conversation.sendContextualUpdate !== "function") return;
    contextSent = true;
    try {
      conversation.sendContextualUpdate(
        "STT mode is transcribe, never translate. Keep the user's original language. " +
        (spokenLang ? "They spoke " + spokenLang + ". " : "") +
        "Reply in that same language. Do not switch to English unless they spoke English."
      );
    } catch (e1) {}
  }

  function sendOriginalUser(text) {
    var t = String(text || "").replace(/\s+/g, " ").trim();
    if (!t) return;
    if (t === lastSentUser) return;
    if (lastSentUser && lastSentUser.indexOf(t) === 0) return;
    lastSentUser = t;
    if (conversation && typeof conversation.sendUserMessage === "function") {
      try { conversation.sendUserMessage(t); } catch (e1) {}
    }
  }

  function ingestOriginal(info) {
    if (!info || !live) return;
    var lang = toElLang(info.language);
    var transcript = String(info.transcript || "").replace(/\s+/g, " ").trim();
    if (transcript && isRtl(transcript) && (!lang || lang === "en")) {
      lang = /[\u067E\u0686\u0698\u06AF]/.test(transcript) ? "fa" : "ar";
    }
    if (lang) spokenLang = lang;
    muteElAsr();
    sendTranscribeContext();
    if (transcript && !shouldIgnoreEnglishAsr(transcript)) {
      upsertLive("user", transcript, true);
      sendOriginalUser(transcript);
    }
    if (spokenLang) startSpeechRec(spokenLang);
  }

  function stopSttLoop() {
    sttSeq += 1;
  }

  function startSttLoop() {
    var my = ++sttSeq;
    function tick() {
      if (my !== sttSeq || !live || !micStream) return;
      transcribeOriginal(micStream).then(function (info) {
        if (my !== sttSeq || !live) return;
        if (info) ingestOriginal(info);
      }).catch(function () {}).then(function () {
        if (my === sttSeq && live) setTimeout(tick, 200);
      });
    }
    tick();
  }

  function stopMeter() {
    if (meterTimer) { clearInterval(meterTimer); meterTimer = null; }
    if (meterEl) {
      meterEl.hidden = true;
      var bar = meterEl.querySelector("i");
      if (bar) bar.style.width = "0";
    }
  }

  function startMeter() {
    if (!meterEl || !conversation) return;
    meterEl.hidden = false;
    var bar = meterEl.querySelector("i");
    meterTimer = setInterval(function () {
      if (!live || !conversation) return;
      var p = null;
      try {
        if (typeof conversation.getInputVolume === "function") p = conversation.getInputVolume();
      } catch (e1) { return; }
      Promise.resolve(p).then(function (vol) {
        var n = typeof vol === "number" ? vol : (vol && vol.volume);
        if (typeof n !== "number") return;
        if (bar) bar.style.width = Math.min(100, Math.round(n * 100)) + "%";
      }).catch(function () {});
    }, 120);
  }

  function hangup() {
    var conv = conversation;
    conversation = null;
    live = false;
    starting = false;
    blockNativeAsr = true;
    spokenLang = "";
    lastProbe = null;
    probePromise = null;
    lastSentUser = "";
    contextSent = false;
    stopSttLoop();
    stopSpeechRec();
    if (micStream) {
      try { micStream.getTracks().forEach(function (t) { t.stop(); }); } catch (e0) {}
      micStream = null;
    }
    stopMeter();
    setSpeakUi(false);
    if (root) root.classList.remove("is-live", "is-busy");
    setStatus("", STATUS_IDLE);
    if (conv && typeof conv.endSession === "function") {
      try { conv.endSession(); } catch (e1) {}
    }
  }

  function sessionOptions(my, connectionType, langCode) {
    var elLang = toElLang(langCode);
    var opts = {
      agentId: AGENT_ID,
      connectionType: connectionType,
      dynamicVariables: {
        stt_mode: "transcribe",
        never_translate: "true",
        lang_auto: "true"
      },
      onConnect: function () {
        if (my !== seq) return;
        live = true;
        starting = false;
        muteElAsr();
        startSttLoop();
        setSpeakUi(true);
        setStatus("active", "Speak now — the Head Engineer is listening.");
        startMeter();
      },
      onDisconnect: function () {
        if (my !== seq) return;
        hangup();
      },
      onError: function (err) {
        try { console.error("ColdDirect ElevenLabs error", err); } catch (e1) {}
        if (my !== seq) return;
        hangup();
        setStatus("error", "The voice session could not start. Allow the microphone and tap SPEAK again.");
      },
      onMessage: function (payload) {
        if (my !== seq) return;
        onAgentMessage(payload);
      },
      onAgentResponseCorrection: function (info) {
        if (my !== seq) return;
        var text = info && (info.corrected_agent_response || info.corrected);
        if (text) upsertLive("bot", String(text), true);
      },
      onModeChange: function (info) {
        if (my !== seq) return;
        var mode = "";
        if (typeof info === "string") mode = info;
        else if (info && typeof info === "object") mode = String(info.mode || info.status || "");
        mode = mode.toLowerCase();
        if (mode === "speaking") {
          agentSpoke = true;
          setStatus("active", "🔊 Head Engineer speaking...");
        } else if (mode === "listening") {
          setStatus("active", "Speak now — the Head Engineer is listening.");
          if (agentSpoke) highlightCta(true);
        }
      }
    };
    if (elLang && elLang !== "en") {
      opts.overrides = { agent: { language: elLang } };
    }
    return opts;
  }

  function fetchConversationToken() {
    return fetch(TOKEN_URL, { cache: "no-store" }).then(function (r) {
      return r.json().catch(function () { return {}; });
    }).then(function (j) {
      return (j && (j.token || j.conversationToken || j.signed_url)) || "";
    }).catch(function () { return ""; });
  }

  function beginSession(Conversation, my) {
    function startWith(opts) {
      return Conversation.startSession(opts);
    }
    function startPublic(langCode) {
      var opts = sessionOptions(my, "webrtc", langCode);
      return startWith(opts).catch(function (err) {
        var msg = String((err && err.message) || err || "");
        if (opts.overrides && /override|400|not enabled|language/i.test(msg)) {
          delete opts.overrides;
          return startWith(opts);
        }
        throw err;
      });
    }
    return startPublic(spokenLang).catch(function (err) {
      var msg = String((err && err.message) || err || "");
      if (!/401|authentication|signed url|conversation token/i.test(msg)) throw err;
      return fetchConversationToken().then(function (token) {
        if (!token) throw err;
        var opts = sessionOptions(my, "webrtc", spokenLang);
        delete opts.agentId;
        opts.conversationToken = token;
        return startWith(opts);
      });
    }).then(function (conv) {
      if (my !== seq) {
        if (conv && conv.endSession) try { conv.endSession(); } catch (e2) {}
        return;
      }
      conversation = conv || conversation;
      live = true;
      muteElAsr();
      sendTranscribeContext();
      startSttLoop();
      if (lastProbe) ingestOriginal(lastProbe);
      else if (probePromise) {
        probePromise.then(function (info) {
          if (my !== seq || !info) return;
          lastProbe = info;
          ingestOriginal(info);
        }).catch(function () {});
      }
    });
  }

  function warmMic() {
    if (micStream && micStream.active) return Promise.resolve(micStream);
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) return Promise.resolve(null);
    return navigator.mediaDevices.getUserMedia({ audio: true }).then(function (s) {
      micStream = s;
      if (!probePromise) {
        probePromise = transcribeOriginal(s).then(function (info) {
          lastProbe = info;
          if (info && info.language) spokenLang = info.language;
          return info;
        }).catch(function () { return null; });
      }
      return s;
    });
  }

  function startLive() {
    if (live || starting) return;
    var my = ++seq;
    userCollapsed = false;
    starting = true;
    agentSpoke = false;
    liveUser = null;
    liveBot = null;
    blockNativeAsr = true;
    lastSentUser = "";
    contextSent = false;
    unlockAudio();
    openPanel(true);
    setSpeakUi(true);
    setStatus("connecting", "Connecting to the Head Engineer...");
    Promise.all([loadSdk(), warmMic()]).then(function (pair) {
      if (my !== seq) return;
      var Conversation = pair[0];
      if (lastProbe && lastProbe.language) spokenLang = lastProbe.language;
      return beginSession(Conversation, my);
    }).catch(function (err) {
      try { console.error("ColdDirect ElevenLabs start", err); } catch (e4) {}
      if (my !== seq) return;
      hangup();
      setStatus("error", "The voice session could not start. Allow the microphone and tap SPEAK again.");
    });
  }

  function onSpeakPointer(ev) {
    if (ev && ev.pointerType === "mouse" && ev.button !== 0) return;
    unlockAudio();
    loadSdk();
    if (!live && !starting) {
      probePromise = null;
      lastProbe = null;
      spokenLang = "";
      warmMic();
    }
  }

  function onSpeakClick(ev) {
    if (ev) ev.preventDefault();
    if (live || starting) {
      seq += 1;
      hangup();
      return;
    }
    startLive();
  }

  function bindUi() {
    speakBtn.addEventListener("pointerdown", onSpeakPointer);
    speakBtn.addEventListener("click", onSpeakClick);
    if (listenBtn) {
      listenBtn.addEventListener("pointerdown", function () { unlockAudio(); });
      listenBtn.addEventListener("click", function (ev) {
        if (ev) ev.preventDefault();
        playWelcome();
      });
    }
    if (closeBtn) closeBtn.addEventListener("click", function (ev) {
      ev.preventDefault();
      ev.stopPropagation();
      if (live || starting) {
        seq += 1;
        hangup();
      }
      closePanel();
    });
    document.addEventListener("pointerdown", function () { unlockAudio(); }, { capture: true, once: true });
  }

  function mount() {
    restoreAudioDock();
    if (document.getElementById("cd-voice-root") && document.getElementById("cd-voice-speak") && document.getElementById("cd-voice-listen")) {
      root = document.getElementById("cd-voice-root");
      syncVoicePlacement();
      return;
    }
    document.documentElement.classList.remove("cd-voice-on");
    var float = document.querySelector(".vapi-widget, elevenlabs-convai");
    if (float && float.parentNode) float.parentNode.removeChild(float);
    var oldCss = document.getElementById("cd-voice-bar-css");
    if (oldCss && oldCss.parentNode) oldCss.parentNode.removeChild(oldCss);
    var oldRoot = document.getElementById("cd-voice-root");
    if (oldRoot && oldRoot.parentNode) oldRoot.parentNode.removeChild(oldRoot);

    var style = document.createElement("style");
    style.id = "cd-voice-bar-css";
    style.textContent = css();
    document.head.appendChild(style);

    root = document.createElement("div");
    root.id = "cd-voice-root";
    root.setAttribute("data-cd-ip", MARK);
    root.setAttribute("role", "region");
    root.setAttribute("aria-label", TITLE);
    root.innerHTML = html();
    placeRoot(root);
    restoreAudioDock();
    window.addEventListener("resize", syncVoicePlacement);
    var mq = window.matchMedia("(max-width: 768px)");
    if (mq.addEventListener) mq.addEventListener("change", syncVoicePlacement);
    else if (mq.addListener) mq.addListener(syncVoicePlacement);

    speakBtn = document.getElementById("cd-voice-speak");
    listenBtn = document.getElementById("cd-voice-listen");
    closeBtn = document.getElementById("cd-voice-close");
    statusEl = document.getElementById("cd-voice-status");
    logEl = document.getElementById("cd-voice-log");
    ctaEl = document.getElementById("cd-voice-cta");
    meterEl = document.getElementById("cd-voice-meter");
    bindUi();
    loadSdk();
    setStatus("", STATUS_IDLE);
  }

  function boot() { mount(); }
  if (document.body) boot();
  document.addEventListener("DOMContentLoaded", boot);
  window.addEventListener("load", boot);
  setTimeout(boot, 60);
  setTimeout(boot, 500);
})();
