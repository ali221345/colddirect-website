/* ColdDirect Voice — Ask Your Fault / Head Engineer (PTT + Vercel Gemini)
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
  var STOP_LABEL = "🔴 Listening… Tap to send";
  var LISTEN_LABEL = "🔊 LISTEN";
  var STATUS_IDLE = "Tap SPEAK and describe the fault; it sends automatically.";
  var SPEECH_SILENCE_MS = 1500;
  var RECORDER_SILENCE_MS = 2000;
  var RECORDER_MAX_MS = 6000;
  var SPOKEN_SUMMARY_MAX_WORDS = 72;
  var SPOKEN_TECHNICAL_MAX_WORDS = 39;
  var VERCEL_API = "https://colddirect-website.vercel.app";
  var DIAGNOSE_URL = VERCEL_API + "/api/voice-diagnose";
  var TTS_URLS = [VERCEL_API + "/api/voice-tts"];

  var host = String(location.hostname || "").toLowerCase();
  if (host && host !== "www.colddirect.co.uk" && host !== "colddirect.co.uk" && host !== "localhost" && host !== "127.0.0.1") return;

  var root, speakBtn, listenBtn, closeBtn, statusEl, logEl, ctaEl, meterEl, textInput;
  var userCollapsed = false;
  var liveUser = null;
  var liveBot = null;
  var recordingRow = null;
  var starting = false;
  var live = false;
  var isSpeaking = false;
  var agentSpoke = false;
  var meterTimer = null;
  var seq = 0;
  var sessionLang = "";
  var micStream = null;
  var mediaRec = null;
  var nativeRecognition = null;
  var nativeText = "";
  var nativeSilenceTimer = null;
  var nativeStopResolve = null;
  var recChunks = [];
  var recMime = "audio/webm";
  var recordingStartedAt = 0;
  var recordingLimitTimer = null;
  var recordingUiTimer = null;
  var recorderHeardAt = 0;
  var recorderLastSoundAt = 0;
  var userText = "";
  var playToken = 0;
  var voiceSource = null;
  var voiceEl = null;
  var audioObjectUrl = "";
  var speechCache = [];
  var speechLang = "en-GB";

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
        '<form id="cd-voice-text-form" style="display:flex;gap:6px;margin-top:10px">' +
          '<label for="cd-voice-text-input" style="position:absolute;left:-10000px">Type your equipment fault</label>' +
          '<input id="cd-voice-text-input" type="text" maxlength="2000" required autocomplete="off" placeholder="Or type the fault here…" style="flex:1;min-width:0;padding:10px;border:1px solid #475569;border-radius:8px;background:#fff;color:#0f172a;font:14px system-ui">' +
          '<button type="submit" class="cd-voice-btn" style="height:auto!important;min-height:40px!important;padding:8px 12px!important">SEND</button>' +
        '</form>' +
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

  function showRecording() {
    if (recordingRow && recordingRow.row && recordingRow.row.parentNode) {
      setTranscriptBody(recordingRow.body, "Recording…", false);
      recordingRow.row.classList.add("is-partial");
      liveUser = recordingRow;
      return;
    }
    recordingRow = addRow("user", "Recording…", true);
    liveUser = recordingRow;
  }

  function fillRecording(text) {
    text = String(text || "");
    if (!recordingRow || !recordingRow.row || !recordingRow.row.parentNode) {
      recordingRow = addRow("user", text, false);
    } else {
      setTranscriptBody(recordingRow.body, text, false);
      recordingRow.row.classList.remove("is-partial");
    }
    liveUser = null;
    if (logEl) logEl.scrollTop = logEl.scrollHeight;
  }

  function showVoiceError(text) {
    if (recordingRow && recordingRow.row && recordingRow.row.parentNode) {
      recordingRow.row.parentNode.removeChild(recordingRow.row);
    }
    recordingRow = null;
    liveUser = null;
    upsertLive("bot", String(text || "I could not hear that clearly. Type the fault below or try again."), true);
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
    // Called synchronously from SPEAK, STOP, SEND and LISTEN user events. Keep
    // this exact element for later MP3 playback so iOS retains media approval.
    try {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (AC) {
        if (!window.__cdPlayCtx) window.__cdPlayCtx = new AC();
        var ctx = window.__cdPlayCtx;
        if (ctx.state === "suspended") ctx.resume();
        var silent = ctx.createBuffer(1, 1, 24000);
        var source = ctx.createBufferSource();
        source.buffer = silent;
        source.connect(ctx.destination);
        source.start(0);
      }
    } catch (e1) {}
    try {
      if (!window.__cdVoicePlayer) {
        var player = document.createElement("audio");
        player.playsInline = true;
        player.setAttribute("playsinline", "true");
        player.setAttribute("webkit-playsinline", "true");
        player.preload = "auto";
        player.style.display = "none";
        (document.body || document.documentElement).appendChild(player);
        window.__cdVoicePlayer = player;
      }
      voiceEl = window.__cdVoicePlayer;
      voiceEl.src = "data:audio/wav;base64,UklGRlQAAABXQVZFZm10IBAAAAABAAEAwF0AAIC7AAACABAAZGF0YTAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=";
      var primed = voiceEl.play();
      if (primed && primed.catch) primed.catch(function () {});
    } catch (e2) {}
    try {
      if (window.speechSynthesis && !window.__cdNativeUnlocked) {
        window.speechSynthesis.resume();
        var nativePrimer = new SpeechSynthesisUtterance(" ");
        nativePrimer.lang = "en-GB";
        nativePrimer.volume = 0;
        window.speechSynthesis.speak(nativePrimer);
        window.__cdNativeUnlocked = true;
      }
    } catch (e3) {}
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
    if (speechCache.length) return playCachedSpeech();
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

  function stripTags(text) {
    return String(text || "").replace(/\[\w+\]\s*/g, "").replace(/\s+/g, " ").trim();
  }

  function spokenClean(text, lang) {
    var fa = lang === "fa-IR";
    return stripTags(text)
      .replace(/read this exactly[^.]*\./gi, " ")
      .replace(/do not add words\.?/gi, " ")
      .replace(/never say the word slash\.?/gi, " ")
      .replace(/calm male head engineer voice\.?/gi, " ")
      .replace(/\bslash\b/gi, " ")
      .replace(/[／/]/g, fa ? " یا " : " or ")
      .replace(/0203\s*952\s*4822/g, "0203 952 4822")
      .replace(/07983\s*759320/g, "07983 759320")
      .replace(/\s+/g, " ").trim();
  }

  function lockLang(text) {
    if (/[\u0600-\u06FF]/.test(String(text || ""))) return "fa-IR";
    return "en-GB";
  }

  function clearRecordingTimers() {
    if (recordingLimitTimer) { clearTimeout(recordingLimitTimer); recordingLimitTimer = null; }
    if (recordingUiTimer) { clearInterval(recordingUiTimer); recordingUiTimer = null; }
    if (nativeSilenceTimer) { clearTimeout(nativeSilenceTimer); nativeSilenceTimer = null; }
  }

  function resolveNativeStop() {
    var resolve = nativeStopResolve;
    nativeStopResolve = null;
    nativeRecognition = null;
    if (resolve) resolve();
  }

  function stopNativeRecognition() {
    var recognition = nativeRecognition;
    if (!recognition) return Promise.resolve();
    return new Promise(function (resolve) {
      nativeStopResolve = resolve;
      var timer = setTimeout(function () {
        try { recognition.abort(); } catch (e1) {}
        resolveNativeStop();
      }, 800);
      var originalResolve = nativeStopResolve;
      nativeStopResolve = function () {
        clearTimeout(timer);
        originalResolve();
      };
      try { recognition.stop(); } catch (e2) {
        try { recognition.abort(); } catch (e3) {}
        resolveNativeStop();
      }
    });
  }

  function stopMicHard() {
    if (nativeRecognition) {
      try { nativeRecognition.abort(); } catch (e0) {}
      resolveNativeStop();
    }
    if (mediaRec) {
      try { if (mediaRec.state !== "inactive") mediaRec.stop(); } catch (e1) {}
      mediaRec = null;
    }
    if (micStream) {
      try { micStream.getTracks().forEach(function (t) { t.stop(); }); } catch (e2) {}
      micStream = null;
    }
  }

  function stopPlayback() {
    playToken += 1;
    isSpeaking = false;
    if (voiceSource) {
      try { voiceSource.stop(0); } catch (e1) {}
      voiceSource = null;
    }
    if (voiceEl) {
      try { voiceEl.pause(); } catch (e2) {}
    }
    var welcome = welcomeAudio();
    if (welcome && !welcome.paused) {
      try { welcome.pause(); } catch (e3) {}
      setListenUi(false);
    }
    try { window.speechSynthesis && window.speechSynthesis.cancel(); } catch (e4) {}
  }

  function startMeter(stream) {
    if (meterEl) meterEl.hidden = false;
    var bar = meterEl && meterEl.querySelector("i");
    var AC = window.AudioContext || window.webkitAudioContext;
    if (!AC || !stream) return;
    try {
      if (window.__cdMeterCtx) {
        try { window.__cdMeterCtx.close(); } catch (e0) {}
      }
      var ctx = new AC();
      window.__cdMeterCtx = ctx;
      if (ctx.state === "suspended") ctx.resume();
      var src = ctx.createMediaStreamSource(stream);
      var ana = ctx.createAnalyser();
      ana.fftSize = 256;
      src.connect(ana);
      var data = new Uint8Array(ana.frequencyBinCount);
      meterTimer = setInterval(function () {
        if (!live) return;
        ana.getByteFrequencyData(data);
        var n = 0;
        for (var i = 0; i < data.length; i++) n += data[i];
        var average = n / data.length;
        if (bar) bar.style.width = Math.min(100, Math.round((average / 255) * 100)) + "%";
        var now = Date.now();
        if (average >= 10) {
          if (!recorderHeardAt) recorderHeardAt = now;
          recorderLastSoundAt = now;
        }
        if (recorderHeardAt && now - recorderLastSoundAt >= RECORDER_SILENCE_MS && mediaRec) sendFault();
      }, 120);
    } catch (e1) {}
  }

  function stopMeter() {
    if (meterTimer) { clearInterval(meterTimer); meterTimer = null; }
    if (window.__cdMeterCtx) {
      try { window.__cdMeterCtx.close(); } catch (e0) {}
      window.__cdMeterCtx = null;
    }
    if (meterEl) {
      meterEl.hidden = true;
      var bar = meterEl.querySelector("i");
      if (bar) bar.style.width = "0";
    }
  }

  function hangup() {
    live = false;
    starting = false;
    clearRecordingTimers();
    stopMicHard();
    stopMeter();
    setSpeakUi(false);
    if (root) root.classList.remove("is-live", "is-busy");
    setStatus("", STATUS_IDLE);
  }

  function playBytes(b64, mime, token) {
    var bin = atob(b64);
    var bytes = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return new Promise(function (resolve, reject) {
      if (token !== playToken) return resolve();
      if (!voiceEl) {
        voiceEl = window.__cdVoicePlayer || document.createElement("audio");
        voiceEl.playsInline = true;
        voiceEl.setAttribute("playsinline", "true");
        voiceEl.setAttribute("webkit-playsinline", "true");
        voiceEl.preload = "auto";
        if (!voiceEl.parentNode) {
          voiceEl.style.display = "none";
          document.body.appendChild(voiceEl);
        }
        window.__cdVoicePlayer = voiceEl;
      }
      if (audioObjectUrl) {
        try { URL.revokeObjectURL(audioObjectUrl); } catch (e1) {}
      }
      audioObjectUrl = URL.createObjectURL(new Blob([bytes], { type: mime || "audio/mpeg" }));
      voiceEl.onended = function () { resolve(); };
      voiceEl.onerror = function () { reject(new Error("audio_playback")); };
      voiceEl.onpause = function () { if (token !== playToken) resolve(); };
      voiceEl.src = audioObjectUrl;
      voiceEl.load();
      var p = voiceEl.play();
      if (p && p.catch) p.catch(reject);
    });
  }

  function speakBrowser(text, lang, token) {
    return new Promise(function (resolve, reject) {
      if (!window.speechSynthesis || !text) return reject(new Error("native_tts_unavailable"));
      if (token !== playToken) return resolve();
      var u = new SpeechSynthesisUtterance(text);
      u.lang = lang === "fa-IR" ? "fa-IR" : "en-GB";
      u.rate = 1;
      var voices = window.speechSynthesis.getVoices() || [];
      var preferred = voices.filter(function (v) {
        var loc = String(v.lang || "").toLowerCase();
        if (lang === "fa-IR") return loc.indexOf("fa") === 0;
        return loc.indexOf("en-gb") === 0 && /natural|daniel|ryan|ravi|george|aaron|serena|male/i.test(v.name);
      })[0];
      var anyUk = voices.filter(function (v) { return String(v.lang || "").toLowerCase().indexOf("en-gb") === 0; })[0];
      var pick = preferred || (lang === "fa-IR" ? null : anyUk);
      if (pick) u.voice = pick;
      window.__cdNativeUtterance = u;
      isSpeaking = true;
      setListenUi(true);
      setStatus("active", "🔊 Speaking with your device voice...");
      u.onend = function () {
        if (token === playToken) {
          isSpeaking = false;
          setListenUi(false);
          setStatus("", STATUS_IDLE);
          highlightCta(true);
        }
        resolve();
      };
      u.onerror = function () { reject(new Error("native_tts_playback")); };
      window.speechSynthesis.resume();
      window.speechSynthesis.speak(u);
    });
  }

  function postJson(url, body) {
    return fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CD-IP": MARK },
      cache: "no-store",
      body: JSON.stringify(body)
    }).then(function (r) { return r.json().catch(function () { return {}; }); });
  }

  function diagnose(payload) {
    return postJson(DIAGNOSE_URL, payload).catch(function () { return null; });
  }

  function blobToBase64(blob) {
    return new Promise(function (resolve) {
      if (!blob || !blob.size) return resolve("");
      var fr = new FileReader();
      fr.onload = function () {
        var s = String(fr.result || "");
        resolve(s.indexOf(",") >= 0 ? s.split(",")[1] : s);
      };
      fr.onerror = function () { resolve(""); };
      fr.readAsDataURL(blob);
    });
  }

  function tracksAreLive(stream) {
    var tracks = stream && stream.getAudioTracks ? stream.getAudioTracks() : [];
    return tracks.length > 0 && tracks.every(function (t) {
      return t.readyState === "live" && t.enabled !== false;
    });
  }

  function waitForLiveTracks(stream) {
    return new Promise(function (resolve, reject) {
      if (tracksAreLive(stream)) return resolve(stream);
      var settled = false;
      var timer = null;
      function finish(ok) {
        if (settled) return;
        settled = true;
        if (timer) clearInterval(timer);
        if (ok) resolve(stream);
        else {
          try { stream.getTracks().forEach(function (t) { t.stop(); }); } catch (e1) {}
          reject(new Error("mic"));
        }
      }
      var tracks = stream.getAudioTracks();
      tracks.forEach(function (t) {
        t.onunmute = function () { if (tracksAreLive(stream)) finish(true); };
      });
      var n = 0;
      timer = setInterval(function () {
        n += 1;
        if (tracksAreLive(stream)) finish(true);
        else if (n > 30) finish(false);
      }, 50);
    });
  }

  function finishRecording() {
    return new Promise(function (resolve) {
      var rec = mediaRec;
      var settled = false;
      function done() {
        if (settled) return;
        settled = true;
        mediaRec = null;
        if (micStream) {
          try { micStream.getTracks().forEach(function (t) { t.stop(); }); } catch (e1) {}
          micStream = null;
        }
        stopMeter();
        resolve();
      }
      if (!rec || rec.state === "inactive") {
        done();
        return;
      }
      var timer = setTimeout(done, 1500);
      rec.onstop = function () {
        clearTimeout(timer);
        done();
      };
      try { rec.requestData(); } catch (e2) {}
      try { rec.stop(); } catch (e3) { clearTimeout(timer); done(); }
    });
  }

  function spokenCta(lang) {
    return lang === "fa-IR"
      ? "برای اعزام فوری مهندس در سراسر لندن، با کُلد دایرِکت با شماره 0203 952 4822 یا 07983 759320 تماس بگیرید. اگر این راهنما مفید بود، لطفاً دکمه سبز لایک و نظر پنج‌ستاره در پایین را بزنید!"
      : "For an immediate engineer visit across London, call Cold Direct on 0203 952 4822 or 07983 759320. If this advice helped, please tap the green Like and 5-Star Review button below!";
  }

  function stripSpokenClose(text, lang) {
    var s = String(text || "");
    var closes = lang === "fa-IR" ? [
      "لطفاً با شماره 0203 952 4822 یا 07983 759320 تماس بگیرید و دکمه سبز لایک و ۵ ستاره در پایین را بزنید.",
      "برای اعزام فوری مهندس در سراسر لندن، با کولد دایرکت با شماره 0203 952 4822 یا 07983 759320 تماس بگیرید. 👍 اگر این راهنما مفید بود، لطفاً دکمه سبز «Like & Leave a 5-Star Review» در پایین را بزنید!",
      spokenCta(lang)
    ] : [
      "Please call us on 0203 952 4822 or 07983 759320, and kindly click the green Like and 5-Star Review button below.",
      "For an immediate engineer visit across London, call ColdDirect on 0203 952 4822 or 07983 759320. 👍 Found this helpful? Please tap the green Like & Leave a 5-Star Review button below!",
      spokenCta(lang)
    ];
    closes.forEach(function (close) { s = s.split(close).join(" "); });
    return s.replace(/\s+/g, " ").trim();
  }

  function conciseSpeech(text, lang) {
    var cta = spokenCta(lang);
    var ctaWords = cta.split(/\s+/).filter(Boolean).length;
    var technicalLimit = Math.min(SPOKEN_TECHNICAL_MAX_WORDS, Math.max(20, SPOKEN_SUMMARY_MAX_WORDS - ctaWords));
    var s = stripSpokenClose(spokenClean(text, lang), lang)
      .replace(/Hello\. I am the Head Engineer at ColdDirect\. I'm glad you chose our company\./gi, " ")
      .replace(/سلام\.\s*من سرمهندس شرکت .*?خوشحالم که شرکت ما را انتخاب کردید\./g, " ")
      .replace(/\s+/g, " ").trim();
    var sentences = s.match(/[^.!?؟]+[.!?؟]+|[^.!?؟]+$/g) || [s];
    var selected = [];
    var words = 0;
    for (var i = 0; i < sentences.length && selected.length < 3; i++) {
      var sentence = sentences[i].trim();
      if (!sentence) continue;
      var count = sentence.split(/\s+/).filter(Boolean).length;
      if (selected.length && words + count > technicalLimit) break;
      if (count > technicalLimit) {
        sentence = sentence.split(/\s+/).slice(0, technicalLimit).join(" ");
        count = technicalLimit;
      }
      selected.push(sentence);
      words += count;
      if (words >= technicalLimit) break;
    }
    return (selected.join(" ").trim() + " " + cta).replace(/\s+/g, " ").trim();
  }

  function loadSpeechSummary() {
    var entry = speechCache[0];
    if (entry && entry.data) return Promise.resolve(entry.data);
    if (entry && entry.loading) return entry.loading;
    entry = { text: splitSpeechText[0], data: null, loading: null, native: false };
    speechCache[0] = entry;
    entry.loading = postJson(TTS_URLS[0], { text: splitSpeechText[0], language: speechLang, summary: true }).then(function (j) {
      if (!j || !j.audio_base64) throw new Error("tts_unavailable");
      entry.data = { data: j.audio_base64, mime: j.audio_mime || "audio/mpeg" };
      return entry.data;
    }).catch(function (error) {
      if (speechCache[0] === entry) speechCache[0] = { text: entry.text, data: null, loading: null, native: false };
      throw error;
    });
    return entry.loading;
  }

  var splitSpeechText = [];

  function finishSpeech(token) {
    if (token !== playToken) return;
    isSpeaking = false;
    setListenUi(false);
    setStatus("", STATUS_IDLE);
    highlightCta(true);
  }

  function nativeFallback(token) {
    if (token !== playToken) return Promise.resolve();
    if (speechCache[0]) speechCache[0].native = true;
    return speakBrowser(splitSpeechText[0], speechLang, token).catch(function () {
      if (token !== playToken) return;
      isSpeaking = false;
      setListenUi(false);
      setStatus("error", "Tap LISTEN to retry, and check your mute switch and volume.");
    });
  }

  function playSpeech(token) {
    if (token !== playToken || !splitSpeechText.length) return Promise.resolve();
    isSpeaking = true;
    setListenUi(true);
    setStatus("active", "🔊 Preparing a short spoken answer...");
    return loadSpeechSummary().then(function (audio) {
      if (token !== playToken) return;
      return playBytes(audio.data, audio.mime, token);
    }).then(function () { finishSpeech(token); }).catch(function () {
      return nativeFallback(token);
    });
  }

  function playCachedSpeech() {
    if (!splitSpeechText.length) return Promise.resolve();
    stopPlayback();
    var token = playToken;
    var first = speechCache[0];
    if (!first || (!first.data && !first.native)) return playSpeech(token);
    if (first.native) return nativeFallback(token);
    setStatus("active", "🔊 Replaying downloaded audio...");
    isSpeaking = true;
    setListenUi(true);
    return playBytes(first.data.data, first.data.mime, token).then(function () {
      finishSpeech(token);
    }).catch(function () {
      return nativeFallback(token);
    });
  }

  function speakAnswer(text, lang) {
    stopPlayback();
    speechLang = lang || "en-GB";
    splitSpeechText = [conciseSpeech(text, speechLang)];
    speechCache = [{ text: splitSpeechText[0], data: null, loading: null, native: false }];
    var token = playToken;
    return playSpeech(token);
  }

  function sendFault() {
    if (!live && !starting) return;
    var my = seq;
    live = false;
    starting = false;
    isSpeaking = true;
    clearRecordingTimers();
    setSpeakUi(false);
    if (root) root.classList.remove("is-live");
    if (root) root.classList.add("is-busy");
    setStatus("connecting", "Transcribing your voice...");
    showRecording();
    finishRecording().then(function () {
      if (my !== seq) return "";
      var blob = recChunks.length ? new Blob(recChunks, { type: recMime || "audio/webm" }) : null;
      return blobToBase64(blob);
    }).then(function (b64) {
      if (my !== seq) return null;
      if (!b64) {
        showVoiceError("I did not catch that. Tap SPEAK and try again.");
        setStatus("error", "I did not catch that. Tap SPEAK and try again.");
        isSpeaking = false;
        return { handled: true };
      }
      return diagnose({
        text: "",
        transcript: "",
        audio_base64: b64,
        mime: (recMime || "audio/webm").split(";")[0],
        language: "auto",
        mode: "transcribe",
        translate: false
      });
    }).then(function (j) {
      if (my !== seq || (j && j.handled)) return;
      if (!j) {
        showVoiceError("I did not catch that. Tap SPEAK and try again.");
        setStatus("error", "The Head Engineer could not hear that. Tap SPEAK again.");
        isSpeaking = false;
        return;
      }
      var transcript = stripTags((j && j.transcript) || "");
      var display = stripTags((j && (j.reply || j.display_text)) || "");
      var spoken = stripTags((j && (j.spoken_text || display)) || "");
      if (!j || j.ok === false || !display || !transcript || /give the brand, error code and whether the cabinet is still cold/i.test(display + " " + spoken)) {
        showVoiceError("I could not hear that clearly. Type the fault below or try again.");
        setStatus("error", (j && j.error) || "Type the fault below or tap SPEAK and try again.");
        isSpeaking = false;
        return;
      }
      var lang = (j && j.language) || lockLang(transcript + " " + display);
      sessionLang = lang;
      fillRecording(transcript);
      upsertLive("bot", display, true);
      return speakAnswer(spoken || display, lang);
    }).catch(function () {
      if (my !== seq) return;
      isSpeaking = false;
      showVoiceError("The diagnosis could not start. Type the fault below or call 0203 952 4822.");
      setStatus("error", "The diagnosis could not start. Type the fault below or call 0203 952 4822.");
    }).then(function () {
      if (root) root.classList.remove("is-busy");
    });
  }

  function sendTextFault(text) {
    text = String(text || "").trim();
    if (!text || live || starting) return;
    var my = ++seq;
    stopPlayback();
    openPanel(true);
    isSpeaking = true;
    if (root) root.classList.add("is-busy");
    upsertLive("user", text, true);
    setStatus("connecting", "Diagnosing your typed fault...");
    diagnose({ text: text, language: "auto", mode: "text" }).then(function (j) {
      if (my !== seq) return;
      var display = stripTags((j && (j.reply || j.display_text)) || "");
      var spoken = stripTags((j && (j.spoken_text || display)) || "");
      if (!j || j.ok === false || !display) {
        isSpeaking = false;
        setStatus("error", (j && j.error) || "Diagnosis is unavailable. Please call 0203 952 4822 or 07983 759320.");
        return;
      }
      var lang = (j && j.language) || lockLang(text + " " + display);
      upsertLive("bot", display, true);
      return speakAnswer(spoken, lang);
    }).catch(function () {
      if (my !== seq) return;
      isSpeaking = false;
      setStatus("error", "Diagnosis is unavailable. Please call 0203 952 4822 or 07983 759320.");
    }).then(function () {
      if (root) root.classList.remove("is-busy");
    });
  }

  function sendRecognizedFault() {
    if (!live && !starting) return;
    var text = String(nativeText || (textInput && textInput.value) || "").trim();
    live = false;
    starting = false;
    clearRecordingTimers();
    setSpeakUi(false);
    setStatus("connecting", "Diagnosing your recognized speech...");
    stopNativeRecognition().then(function () {
      if (!text) {
        hangup();
        showVoiceError("I did not detect any speech. Tap SPEAK and try again, or type the fault below.");
        return;
      }
      if (textInput) textInput.value = "";
      sendTextFault(text);
    });
  }

  function queueRecognizedSend(my) {
    if (nativeSilenceTimer) clearTimeout(nativeSilenceTimer);
    nativeSilenceTimer = setTimeout(function () {
      nativeSilenceTimer = null;
      if (my === seq && live && nativeText) sendRecognizedFault();
    }, SPEECH_SILENCE_MS);
  }

  function startRecorder(my) {
    starting = true;
    live = false;
    setStatus("connecting", "Starting the microphone recorder...");
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || !window.MediaRecorder) {
      hangup();
      setStatus("error", "This browser cannot capture speech. Type the fault below or try another browser.");
      return;
    }
    navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true, channelCount: 1 } }).then(function (s) {
      return waitForLiveTracks(s);
    }).then(function (s) {
      if (my !== seq) {
        s.getTracks().forEach(function (t) { t.stop(); });
        return;
      }
      micStream = s;
      recMime = MediaRecorder.isTypeSupported("audio/webm;codecs=opus") ? "audio/webm;codecs=opus" : "audio/mp4";
      try {
        mediaRec = new MediaRecorder(s, { mimeType: recMime });
      } catch (e1) {
        try { mediaRec = new MediaRecorder(s); recMime = mediaRec.mimeType || recMime; } catch (e2) { mediaRec = null; }
      }
      if (!mediaRec) {
        hangup();
        setStatus("error", "This browser cannot record audio. Type the fault below.");
        return;
      }
      mediaRec.ondataavailable = function (ev) {
        if (ev.data && ev.data.size) recChunks.push(ev.data);
      };
      try { mediaRec.start(250); } catch (e3) {
        hangup();
        setStatus("error", "This browser cannot record audio. Type the fault below.");
        return;
      }
      live = true;
      starting = false;
      recordingStartedAt = Date.now();
      recorderHeardAt = 0;
      recorderLastSoundAt = 0;
      recordingLimitTimer = setTimeout(function () {
        recordingLimitTimer = null;
        if (my === seq && live) sendFault();
      }, RECORDER_MAX_MS);
      recordingUiTimer = setInterval(function () {
        if (!live || !speakBtn) return;
        var remaining = Math.max(0, Math.ceil((RECORDER_MAX_MS - (Date.now() - recordingStartedAt)) / 1000));
        speakBtn.textContent = "🔴 " + remaining + "s • Tap to send";
      }, 250);
      setStatus("active", "🔴 Listening… speak now; recording sends automatically.");
      startMeter(s);
      showRecording();
    }).catch(function () {
      if (my !== seq) return;
      hangup();
      setStatus("error", "Allow the microphone and tap SPEAK again, or type the fault below.");
    });
  }

  function startNativeRecognition(my, Recognition) {
    var recognition;
    try { recognition = new Recognition(); } catch (e0) {
      startRecorder(my);
      return;
    }
    nativeRecognition = recognition;
    nativeText = "";
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;
    recognition.lang = sessionLang || (/^fa/i.test(navigator.language || "") ? "fa-IR" : "en-GB");
    recognition.onstart = function () {
      if (my !== seq) return;
      live = true;
      starting = false;
      recordingStartedAt = Date.now();
      setStatus("active", "🔴 Listening… your words will appear below.");
      showRecording();
    };
    recognition.onresult = function (event) {
      if (my !== seq) return;
      var combined = "";
      for (var i = 0; i < event.results.length; i++) combined += event.results[i][0].transcript + " ";
      nativeText = combined.replace(/\s+/g, " ").trim();
      if (textInput) textInput.value = nativeText;
      if (nativeText) {
        upsertLive("user", nativeText, false);
        queueRecognizedSend(my);
      }
    };
    recognition.onerror = function () {
      if (my !== seq || !live && !starting) return;
      if (nativeText) {
        sendRecognizedFault();
        return;
      }
      nativeRecognition = null;
      live = false;
      starting = true;
      startRecorder(my);
    };
    recognition.onend = function () {
      if (nativeRecognition !== recognition) return;
      resolveNativeStop();
      if (my === seq && live) sendRecognizedFault();
    };
    try {
      recognition.start();
      setStatus("connecting", "Starting live speech recognition...");
    } catch (e1) {
      nativeRecognition = null;
      startRecorder(my);
    }
  }

  function startLive() {
    if (live || starting || isSpeaking) return;
    var my = ++seq;
    userCollapsed = false;
    starting = true;
    agentSpoke = false;
    liveUser = null;
    liveBot = null;
    recordingRow = null;
    userText = "";
    nativeText = "";
    recChunks = [];
    clearRecordingTimers();
    stopPlayback();
    unlockAudio();
    openPanel(true);
    setSpeakUi(true);
    setStatus("connecting", "Starting speech recognition...");
    var Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (Recognition) startNativeRecognition(my, Recognition);
    else startRecorder(my);
  }

  function onSpeakPointer(ev) {
    if (ev && ev.pointerType === "mouse" && ev.button !== 0) return;
    unlockAudio();
  }

  function onSpeakClick(ev) {
    if (ev) ev.preventDefault();
    unlockAudio();
    if (isSpeaking) {
      stopPlayback();
      setStatus("", STATUS_IDLE);
      return;
    }
    if (starting) {
      setStatus("connecting", "Starting the microphone… please wait.");
      return;
    }
    if (live) {
      if (Date.now() - recordingStartedAt < 900) {
        setStatus("active", "Keep speaking for at least one second, then tap to send.");
        return;
      }
      seq += 1;
      if (nativeRecognition) sendRecognizedFault();
      else sendFault();
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
        if (live || starting) {
          stopMicHard();
        }
        stopPlayback();
        playWelcome();
      });
    }
    if (closeBtn) closeBtn.addEventListener("click", function (ev) {
      ev.preventDefault();
      ev.stopPropagation();
      if (live || starting || isSpeaking) {
        seq += 1;
        stopPlayback();
        hangup();
      }
      closePanel();
    });
    var textForm = document.getElementById("cd-voice-text-form");
    textInput = document.getElementById("cd-voice-text-input");
    if (textForm && textInput) textForm.addEventListener("submit", function (ev) {
      ev.preventDefault();
      unlockAudio();
      var value = textInput.value;
      if (!value.trim()) return;
      textInput.value = "";
      sendTextFault(value);
    });
    document.addEventListener("pointerdown", function () { unlockAudio(); }, { capture: true, once: true });
  }

  function mount() {
    restoreAudioDock();
    var existing = document.getElementById("cd-voice-root");
    if (existing && existing.getAttribute("data-cd-ptt") === "1" && document.getElementById("cd-voice-speak") && document.getElementById("cd-voice-listen")) {
      root = existing;
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
    root.setAttribute("data-cd-ptt", "1");
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
    setStatus("", STATUS_IDLE);
  }

  function boot() { mount(); }
  if (document.body) boot();
  document.addEventListener("DOMContentLoaded", boot);
  window.addEventListener("load", boot);
  setTimeout(boot, 60);
  setTimeout(boot, 500);
})();
