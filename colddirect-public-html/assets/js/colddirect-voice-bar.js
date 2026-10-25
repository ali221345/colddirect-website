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
  var CLOSING_EN = "If this advice helped you, please click the green Like and 5-Star Review button right below in this box to help our website grow.";
  var CLOSING_FA = "اگر این راهنمایی برای شما مفید بود و دوست دارید به رشد سایت ما کمک کنید، ممنون می‌شویم دکمه لایک و ثبت نظر را در پایین همین صفحه بزنید.";
  var KEEP_OPEN = "Keep your technical diagnostic response concise (3 to 4 sentences max) so you always have plenty of room to finish your complete closing sentence clearly: '" + CLOSING_EN + "' NEVER trigger any end-call tool while answering a question—wait for the user to reply.";
  var CLOSING_RULE = [
    "MANDATORY CLOSING RULE FOR EVERY RESPONSE: At the very end of EVERY single answer you give (regardless of the language), you MUST verbally ask the user to click the Like / Review button inside the box to help our website grow.",
    "Never skip this spoken closing. Say it out loud after the technical answer. Do not only show it as text.",
    "If speaking English, always end by saying: \"" + CLOSING_EN + "\"",
    "If speaking Persian, always end by saying: \"" + CLOSING_FA + "\"",
    "If speaking any other language, translate that exact closing sentence naturally into that language.",
    KEEP_OPEN
  ].join(" ");

  var vapi = null;
  var root, speakBtn, listenBtn, closeBtn, statusEl, logEl, ctaEl;
  var callActive = false;
  var callStarting = false;
  var userCollapsed = false;
  var liveUser = null;
  var liveBot = null;

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
      "#cd-voice-root.is-live #cd-voice-dot{background:#22c55e;}",
      "@keyframes cdVoicePulse{0%{box-shadow:0 0 0 0 rgba(34,197,94,.65);}70%{box-shadow:0 0 0 8px rgba(34,197,94,0);}100%{box-shadow:0 0 0 0 rgba(34,197,94,0);}}",
      "#cd-voice-title{white-space:nowrap;font-size:12px;font-weight:800;color:#f8fafc;}",
      "#cd-voice-controls{display:flex;align-items:center;gap:5px;flex:0 0 auto;flex-wrap:wrap;}",
      "#cd-voice-root .cd-voice-langwrap{display:inline-flex;align-items:center;height:26px;padding:0 7px;border:1px solid #38bdf8;border-radius:6px;background:#082f49;color:#e0f2fe;font:700 10px/1 system-ui,sans-serif;white-space:nowrap;}",
      "#cd-voice-root button.cd-voice-btn{height:26px;padding:0 8px;border:1px solid #334155;border-radius:6px;background:#1e293b;color:#f8fafc;font:700 10px/1 system-ui,sans-serif;letter-spacing:.03em;cursor:pointer;display:inline-flex;align-items:center;gap:3px;white-space:nowrap;}",
      "#cd-voice-root button.cd-voice-btn.is-on{background:#0ea5e9;border-color:#38bdf8;color:#04111f;}",
      "#cd-voice-root button.cd-voice-btn#cd-voice-speak.is-on{background:#dc2626;border-color:#f87171;color:#fff;}",
      "#cd-voice-panel{display:none;position:absolute;left:0;top:calc(100% + 8px);z-index:100000;width:min(420px,calc(100vw - 20px));padding:12px;background:#0b1120;border:1px solid #1e293b;border-radius:12px;box-shadow:0 18px 40px rgba(2,6,23,.35);}",
      "#cd-voice-root.is-open #cd-voice-panel{display:block;animation:cdVoiceDrop .18s ease forwards;}",
      "@keyframes cdVoiceDrop{from{opacity:0;transform:translateY(-8px);}to{opacity:1;transform:translateY(0);}}",
      "#cd-voice-panel-head{display:flex;align-items:flex-start;gap:8px;margin:0 0 8px;}",
      "#cd-voice-status{flex:1;min-height:18px;margin:0;color:#7dd3fc;font:500 12px/1.4 system-ui,sans-serif;}",
      "#cd-voice-status.is-error{color:#fca5a5;}",
      "#cd-voice-close{flex:0 0 28px;width:28px;height:28px;padding:0;border:1px solid #334155;border-radius:6px;background:#1e293b;color:#f8fafc;font:700 16px/1 system-ui,sans-serif;cursor:pointer;}",
      "#cd-voice-log{max-height:min(42vh,320px);overflow:auto;-webkit-overflow-scrolling:touch;display:flex;flex-direction:column;gap:8px;padding:4px 2px 8px;}",
      "#cd-voice-log .cd-voice-row{max-width:92%;padding:8px 10px;border-radius:10px;font:400 14px/1.5 system-ui,sans-serif;white-space:pre-wrap;overflow-wrap:anywhere;}",
      "#cd-voice-log .cd-voice-row.is-user{align-self:flex-end;background:#1e3a5f;color:#e0f2fe;}",
      "#cd-voice-log .cd-voice-row.is-bot{align-self:flex-start;background:#111827;color:#f8fafc;border:1px solid #334155;}",
      "#cd-voice-log .cd-voice-row.is-partial{opacity:.78;}",
      "#cd-voice-log .cd-voice-who{display:block;margin:0 0 4px;font:700 10px/1 system-ui,sans-serif;letter-spacing:.04em;color:#93c5fd;}",
      "#cd-voice-cta{display:flex;margin-top:12px;width:100%;min-height:48px;align-items:center;justify-content:center;gap:8px;padding:12px 14px;border:0;border-radius:10px;background:linear-gradient(180deg,#16a34a 0%,#15803d 100%);color:#fff;font:800 13px/1.3 system-ui,sans-serif;text-decoration:none;cursor:pointer;box-shadow:0 0 0 2px rgba(74,222,128,.55),0 8px 18px rgba(22,163,74,.38);}",
      "#cd-voice-cta.is-hot{background:#22c55e;color:#052e16;box-shadow:0 0 0 4px rgba(74,222,128,.75),0 0 28px rgba(34,197,94,.7);animation:cdVoiceCta .9s ease-in-out infinite;}",
      "@keyframes cdVoiceCta{0%,100%{transform:scale(1);}50%{transform:scale(1.045);}}",
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
          '<button type="button" class="cd-voice-btn" id="cd-voice-speak" aria-pressed="false">🎤 SPEAK</button>' +
          '<button type="button" class="cd-voice-btn" id="cd-voice-listen" aria-pressed="false">🔊 LISTEN</button>' +
        "</div>" +
      "</div>" +
      '<div id="cd-voice-panel">' +
        '<div id="cd-voice-panel-head">' +
          '<div id="cd-voice-status" role="status">Ready to start a voice conversation.</div>' +
          '<button type="button" id="cd-voice-close" aria-label="Close transcript">✕</button>' +
        "</div>" +
        '<div id="cd-voice-log" aria-live="polite"></div>' +
        '<a id="cd-voice-cta" href="' + REVIEW_HREF + '">👍 Like &amp; Leave a 5-Star Review</a>' +
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

  function openPanel(force) {
    if (userCollapsed && !force) return;
    if (root) root.classList.add("is-open");
  }

  function closePanel() {
    userCollapsed = true;
    if (root) root.classList.remove("is-open");
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

  function onSpeechEnd() {
    highlightCta(true);
    setStatus("active", "If this helped, please leave a like and a 5-star review.");
  }

  function assistantOverrides() {
    return {
      variableValues: {
        closingRule: CLOSING_RULE,
        keepCallOpen: KEEP_OPEN
      },
      model: {
        maxTokens: 600
      },
      silenceTimeoutSeconds: 45,
      endCallFunctionEnabled: false,
      endCallPhrases: [],
      modelOutputInMessagesEnabled: true,
      clientMessages: [
        "transcript",
        "conversation-update",
        "model-output",
        "speech-update",
        "status-update",
        "hang",
        "function-call",
        "tool-calls",
        "user-interrupted",
        "voice-input"
      ]
    };
  }

  function injectClosingRule() {
    if (!vapi) return;
    try {
      vapi.send({
        type: "add-message",
        message: { role: "system", content: CLOSING_RULE },
        triggerResponseEnabled: false
      });
    } catch (e1) {}
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

  function lastRowText(role) {
    if (!logEl) return "";
    var sel = role === "user" ? ".cd-voice-row.is-user" : ".cd-voice-row.is-bot";
    var rows = logEl.querySelectorAll(sel);
    if (!rows.length) return "";
    var body = rows[rows.length - 1].querySelector(".cd-voice-txt");
    return body ? String(body.textContent || "") : "";
  }

  function preferLonger(prev, next) {
    prev = String(prev || "");
    next = String(next || "");
    if (!next) return prev;
    if (!prev) return next;
    if (next.length >= prev.length) return next;
    if (prev.indexOf(next) === 0) return prev;
    return next;
  }

  function livePointer(role, row) {
    var body = row && row.querySelector(".cd-voice-txt");
    var cur = { row: row, body: body };
    if (role === "user") liveUser = cur;
    else liveBot = cur;
    return cur;
  }

  function upsertLive(role, text, final) {
    text = String(text || "");
    var cur = role === "user" ? liveUser : liveBot;
    if (cur) {
      text = preferLonger(cur.body.textContent, text);
      cur.body.textContent = text || "";
      applyDir(cur.body, text);
      cur.row.classList.toggle("is-partial", !final);
    } else {
      var prev = lastRowText(role);
      text = preferLonger(prev, text);
      if (prev && (text.indexOf(prev) === 0 || prev.indexOf(text) === 0)) {
        patchLastRow(role, text);
        var sel = role === "user" ? ".cd-voice-row.is-user" : ".cd-voice-row.is-bot";
        var rows = logEl ? logEl.querySelectorAll(sel) : [];
        if (rows.length) cur = livePointer(role, rows[rows.length - 1]);
      } else {
        cur = addRow(role, text, !final);
        if (role === "user") liveUser = cur;
        else liveBot = cur;
      }
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
    userCollapsed = false;
    openPanel(true);
    resetTranscript();
    if (speakBtn) speakBtn.disabled = true;
    if (listenBtn) listenBtn.disabled = true;
    setStatus("connecting", "Requesting microphone access…");
    Promise.resolve(vapi.start(ASSISTANT_ID, assistantOverrides())).then(function () {
      injectClosingRule();
    }).catch(function () {
      setIdleState();
      setStatus("error", "The call could not start. Check microphone permission.");
    });
  }

  function stopCall() {
    // NEVER call this from speech-end, message, hang, or a timer. User END / ✕ only.
    if (!vapi) return;
    if (!callActive && !callStarting) return;
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
    userCollapsed = false;
    openPanel(true);
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
    if (typeof msg.content === "string") return msg.content;
    if (Array.isArray(msg.content)) {
      return msg.content.map(function (part) {
        if (typeof part === "string") return part;
        return (part && (part.text || part.content || part.transcript)) || "";
      }).join("");
    }
    if (typeof msg.output === "string") return msg.output;
    if (msg.message && typeof msg.message.content === "string") return msg.message.content;
    if (msg.message && typeof msg.message.transcript === "string") return msg.message.transcript;
    return "";
  }

  function isFinalTranscript(msg, type) {
    var tt = String((msg && (msg.transcriptType || msg.transcript_type)) || "").toLowerCase();
    return tt === "final" || type === "transcript-final" || !!(msg && (msg.isFinal === true || msg.is_final === true));
  }

  function patchLastRow(role, text) {
    if (!logEl || !text) return;
    var sel = role === "user" ? ".cd-voice-row.is-user" : ".cd-voice-row.is-bot";
    var rows = logEl.querySelectorAll(sel);
    if (!rows.length) {
      addRow(role, text, false);
      return;
    }
    var body = rows[rows.length - 1].querySelector(".cd-voice-txt");
    if (!body) return;
    var merged = preferLonger(body.textContent, text);
    body.textContent = merged;
    applyDir(body, merged);
    rows[rows.length - 1].classList.remove("is-partial");
  }

  function handleConversation(msg) {
    var conv = msg.conversation || msg.messages || (msg.message && msg.message.messages);
    if (!Array.isArray(conv) || !logEl) return;
    var keptBot = lastRowText("bot");
    var keptUser = lastRowText("user");
    logEl.innerHTML = "";
    liveUser = null;
    liveBot = null;
    conv.forEach(function (item) {
      var role = roleFrom(item) || "bot";
      var text = textFrom(item) || (typeof item.content === "string" ? item.content : "");
      if (text) addRow(role, text, false);
    });
    patchLastRow("bot", keptBot);
    patchLastRow("user", keptUser);
  }

  function handleMessage(msg) {
    if (!msg) return;
    var type = String(msg.type || "").toLowerCase();
    if (type === "hang") return;
    if (type === "conversation-update") {
      handleConversation(msg);
      return;
    }
    if (type === "model-output") {
      var chunk = textFrom(msg);
      if (!chunk) return;
      var prev = (liveBot && liveBot.body && liveBot.body.textContent) || lastRowText("bot");
      var next = chunk.indexOf(prev) === 0 ? chunk : preferLonger(prev, prev + chunk);
      upsertLive("bot", next, false);
      return;
    }
    if (type === "transcript" || type === "transcript-final" || type.indexOf("transcript") !== -1) {
      var role = roleFrom(msg) || (String(msg.transcriptType || "").indexOf("assistant") !== -1 ? "bot" : "user");
      var text = textFrom(msg);
      if (!text) return;
      var final = isFinalTranscript(msg, type);
      upsertLive(role, text, final);
      if (final && role === "bot") highlightCta(true);
      return;
    }
    if (type === "speech-end" || type === "speech-stopped") {
      onSpeechEnd();
      return;
    }
    if (type === "speech-update") {
      var st = String(msg.status || msg.speechUpdateType || "").toLowerCase();
      if (st === "started" || st === "speech-started") {
        setStatus("active", "Head engineer is speaking…");
      }
      if (st === "stopped" || st === "speech-stopped" || st === "end" || st === "speech-end") {
        onSpeechEnd();
      }
    }
  }

  function bindCall(instance) {
    vapi = instance;
    speakBtn.addEventListener("click", toggleSpeak);
    listenBtn.addEventListener("click", listenNow);
    vapi.on("call-start", function () {
      setLiveState();
      injectClosingRule();
    });
    vapi.on("call-end", function () {
      setIdleState();
      if (logEl && logEl.children.length) highlightCta(true);
    });
    vapi.on("speech-end", onSpeechEnd);
    vapi.on("message", handleMessage);
    vapi.on("transcript", function (msg) {
      if (typeof msg === "string") msg = { type: "transcript", transcript: msg, transcriptType: "final" };
      else if (!msg || typeof msg !== "object") msg = { type: "transcript" };
      else if (!msg.type) msg = Object.assign({ type: "transcript" }, msg);
      handleMessage(msg);
    });
    vapi.on("conversation-update", function (msg) {
      if (!msg || typeof msg !== "object") msg = { type: "conversation-update" };
      else if (!msg.type) msg = Object.assign({ type: "conversation-update" }, msg);
      handleMessage(msg);
    });
    vapi.on("error", function () {
      setIdleState();
      setStatus("error", "A voice connection error occurred. Please try again.");
    });
  }

  function isMobileVoice() {
    try { return window.matchMedia("(max-width: 768px)").matches; } catch (e1) { return false; }
  }

  function restoreAudioDock() {
    var dock = document.getElementById("cd-audio-dock");
    if (!dock) return;
    dock.removeAttribute("hidden");
    dock.removeAttribute("aria-hidden");
    dock.style.removeProperty("display");
    dock.style.removeProperty("position");
    dock.style.removeProperty("top");
    dock.style.removeProperty("right");
    if (!document.getElementById("cd-audio-dock-restore")) {
      var style = document.createElement("style");
      style.id = "cd-audio-dock-restore";
      style.textContent = [
        "#cd-audio-dock{display:block !important;visibility:visible !important;opacity:1 !important;pointer-events:auto !important;}",
        "@media (min-width:769px){#cd-audio-dock{position:absolute !important;top:12px !important;right:10px !important;left:auto !important;bottom:auto !important;z-index:401 !important;width:240px !important;max-width:min(240px,calc(100vw - 24px)) !important;}}",
        "@media (max-width:768px){#cd-audio-dock{position:relative !important;top:auto !important;right:auto !important;left:auto !important;bottom:auto !important;width:auto !important;max-width:none !important;flex:1 1 40%;min-width:0;margin:0 !important;z-index:1 !important;overflow:hidden !important;box-sizing:border-box;}}"
      ].join("");
      (document.body || document.documentElement).appendChild(style);
    }
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
      if (dock && node && dock.nextSibling !== node) {
        strip.insertBefore(dock, node);
      }
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

  function mount() {
    restoreAudioDock();
    if (document.getElementById("cd-voice-root")) {
      root = document.getElementById("cd-voice-root");
      syncVoicePlacement();
      return;
    }
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
    if (closeBtn) closeBtn.addEventListener("click", function (ev) {
      ev.preventDefault();
      ev.stopPropagation();
      closePanel();
      if (callActive || callStarting) stopCall();
    });

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
