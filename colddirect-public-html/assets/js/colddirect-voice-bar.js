/* ColdDirect Voice — Ask Your Fault, instant record-stop-reply (no WebRTC)
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
  var STOP_LABEL = "⏹ SEND";
  var ENDPOINTS = [
    "/colddirect-voice-vault.aspx",
    "/api/colddirect-voice-vault.aspx",
    "/api/colddirect-voice-vault.php",
    "/api/colddirect-voice-vault.js"
  ];
  var GREET_EN = "Hello. I am the Senior Engineer at Cold Direct. I am glad you chose our company. ";
  var FA_DISPLAY_OPEN = "درود، من مهندس ارشد در شرکت کولد دایرکت هستم و خوشحالم که ما را انتخاب کردید.";
  var FA_DISPLAY_CLOSE = "برای اعزام فوری تکنسین در لندن، با شماره 0203 952 4822 یا موبایل 07983 759320 تماس بگیرید. اگر این راهنمایی برای شما مفید بود، لطفاً دکمه سبز لایک و ثبت نظر ۵ ستاره را در پایین همین کادر بزنید.";
  var FA_AUDIO_OPEN = "درود بر شما. من مهندس ارشد شرکت کُلد دایرِکت هستم و خوشحالم که ما را انتخاب کردید. ";
  var FA_AUDIO_CLOSE = "برای اعزام فوری تکنسین در لندن، با شماره تلفن صفر دویست و سه، نهصد و پنجاه و دو، چهل و هشت، بیست و دو، و یا موبایل صفر هفت نه هشت سه، هفتصد و پنجاه و نه، سیصد و بیست تماس بگیرید. اگر این راهنمایی برای شما مفید بود، ممنون می‌شویم دکمه سبز لایک و ثبت نظر پنج ستاره را در پایین همین کادر بزنید.";
  var GREET = {
    en: GREET_EN,
    fa: FA_DISPLAY_OPEN + " ",
    tr: "Merhaba. Cold Direct'te kıdemli mühendisim ve bizi seçtiğiniz için memnunum. ",
    tl: "Kumusta. Ako ang Senior Engineer sa Cold Direct at natutuwa akong pinili ninyo kami. ",
    ar: "مرحبا. أنا المهندس الأول في كولد دايركت ويسعدني أنكم اخترتمونا. ",
    es: "Hola. Soy el ingeniero sénior de Cold Direct y me alegra que nos hayan elegido. "
  };
  var CLOSE_D = {
    en: " For a same-day engineer in London, call 0203 952 4822 or mobile 07983 759320. If this helped, please click the green Like & 5-Star Review button below.",
    fa: " " + FA_DISPLAY_CLOSE,
    tr: " Londra'da acil teknisyen için 0203 952 4822 veya cep 07983 759320'yi arayın. Bu öneri işinize yaradıysa aşağıdaki yeşil Beğen ve 5 yıldızlı yorum düğmesine tıklayın.",
    tl: " Para sa agarang technician sa London, tawagan ang 0203 952 4822 o mobile 07983 759320. Kung nakatulong ito, paki-click ang berdeng Like at 5-Star Review button sa ibaba.",
    ar: " لإرسال فني فوري في لندن اتصلوا على 0203 952 4822 أو الموبايل 07983 759320. إذا أفادتكم النصيحة، اضغطوا زر الإعجاب الأخضر وتقييم الخمس نجوم في أسفل هذا المربع.",
    es: " Para un técnico urgente en Londres llame al 0203 952 4822 o al móvil 07983 759320. Si esto le ayudó, pulse el botón verde de Like y reseña de 5 estrellas abajo."
  };
  var SILENT_WAV = "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAABErAAABAAgAZGF0YQAAAAA=";
  var DIAGNOSE_MS = 28000;
  var TTS_MS = 18000;
  var MAX_MS = 60000;

  var root, speakBtn, listenBtn, closeBtn, statusEl, logEl, ctaEl, meterEl;
  var userCollapsed = false;
  var liveUser = null;
  var liveBot = null;
  var recording = false;
  var recStarting = false;
  var recStream = null;
  var recorder = null;
  var recChunks = [];
  var recTimer = null;
  var meterTimer = null;
  var meterCtx = null;
  var meterSrc = null;
  var sr = null;
  var srText = "";
  var srFinal = "";
  var askSeq = 0;
  var lastSpoken = "";
  var lastTtsText = "";
  var lastLang = "en";
  var lastAudio = null;
  var recBeganAt = 0;
  var playing = false;
  var playSource = null;
  var unlocked = false;

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
      "#cd-voice-html5{position:absolute;width:1px;height:1px;opacity:0;pointer-events:none;}",
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
          '<button type="button" class="cd-voice-btn" id="cd-voice-listen" aria-pressed="false">🔊 LISTEN</button>' +
        "</div>" +
      "</div>" +
      '<div id="cd-voice-panel">' +
        '<div id="cd-voice-panel-head">' +
          '<div id="cd-voice-status" role="status">Tap SPEAK, then STOP &amp; SEND when you finish.</div>' +
          '<button type="button" id="cd-voice-close" aria-label="Close transcript">✕</button>' +
        "</div>" +
        '<div id="cd-voice-meter" hidden><i></i></div>' +
        '<div id="cd-voice-log" aria-live="polite"></div>' +
        '<a id="cd-voice-cta" href="' + REVIEW_HREF + '">👍 Like &amp; Leave a 5-Star Review</a>' +
        '<audio id="cd-voice-html5" playsinline webkit-playsinline preload="auto"></audio>' +
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
    if (arguments.length === 1) {
      message = kind;
      kind = "";
    }
    if (!statusEl) return;
    statusEl.textContent = message || "";
    statusEl.classList.toggle("is-error", kind === "error");
    if (root) {
      root.classList.toggle("is-busy", kind === "connecting");
      root.classList.toggle("is-live", kind === "active" || recording);
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

  function westDigits(s) {
    return String(s || "").replace(/[\u06F0-\u06F9]/g, function (c) {
      return String(c.charCodeAt(0) - 0x06F0);
    }).replace(/[\u0660-\u0669]/g, function (c) {
      return String(c.charCodeAt(0) - 0x0660);
    });
  }

  function twoSentences(text) {
    var s = String(text || "").replace(/\s+/g, " ").replace(/^\s+|\s+$/g, "");
    if (!s) return "";
    var parts = s.split(/(?<=[.!?؟])\s+/);
    if (parts.length <= 2) return s;
    return (parts[0] + " " + parts[1]).replace(/^\s+|\s+$/g, "");
  }

  function stripPersianFrame(text) {
    var s = westDigits(text);
    s = s.replace(/^دُرود بر شُما[\s\S]*?اِنتِخاب کَردید\.?\s*/u, "");
    s = s.replace(/^درود بر شما[\s\S]*?انتخاب کردید\.?\s*/u, "");
    s = s.replace(/^درود[^.!?؟]*[.!?؟]?\s*/u, "");
    s = s.replace(/^سلام[^.!?؟]*[.!?؟]?\s*/u, "");
    s = s.replace(/\s*برای اعزام فوری[\s\S]*$/u, "");
    s = s.replace(/\s*چِنانچه مُشکِل[\s\S]*$/u, "");
    s = s.replace(/\s*اگر این راهنمایی[\s\S]*$/u, "");
    s = s.replace(/\s*اَگَر این راهْنَمایی[\s\S]*$/u, "");
    s = s.replace(/\s*برای هماهنگی[\s\S]{0,80}تماس بگیرید\.?/gu, " ");
    s = s.replace(/(?:\+44\s*\(?0?\)?|0)\s*7983[\s\-]*759[\s\-]*320/g, " ");
    s = s.replace(/(?:\+44\s*\(?0?\)?|0)\s*203[\s\-]*952[\s\-]*4822/g, " ");
    s = s.replace(/(?:\+44\s*\(?0?\)?|0)\s*800[\s\-]*112[\s\-]*3427/g, " ");
    s = s.replace(/(?<!\d)(\+?\d[\d\s\-]{6,}\d)(?!\d)/g, " ");
    return twoSentences(s.replace(/\s+/g, " ").replace(/^\s+|\s+$/g, ""));
  }

  function cleanTechnicalAnswerForTTS(text) {
    var s = stripPersianFrame(text);
    s = s.replace(/سردخانه/g, "سَردخانه");
    s = s.replace(/یخچال/g, "یَخچالِ");
    s = s.replace(/کمپرسور/g, "کُمپرِسور");
    s = s.replace(/ترموستات/g, "تِرموستات");
    s = s.replace(/کندانسور/g, "کُندانسور");
    s = s.replace(/اواپراتور/g, "اِواپُراتور");
    s = s.replace(/کولد\s*دایرکت|ColdDirect|Cold Direct/gi, "کُلد دایرِکت");
    return s.replace(/\s+/g, " ").replace(/^\s+|\s+$/g, "");
  }

  function wrapPersianDisplay(text) {
    var tech = stripPersianFrame(text);
    return FA_DISPLAY_OPEN + "\n" + tech + "\n" + FA_DISPLAY_CLOSE;
  }

  function persianAudioText(text) {
    return FA_AUDIO_OPEN + cleanTechnicalAnswerForTTS(text) + " " + FA_AUDIO_CLOSE;
  }

  function ttsPayload(text, lang) {
    if (lang === "fa" || hasPersian(text)) {
      var t = String(text || "");
      if (t.indexOf("درود بر شما") === 0 || t.indexOf("دُرود بر شُما") === 0) return t;
      return persianAudioText(text);
    }
    return String(text || "");
  }

  function canonLang(code) {
    var c = String(code || "").toLowerCase().replace("_", "-");
    if (c.indexOf("fil") === 0 || c === "tagalog" || c.indexOf("tl") === 0) return "tl";
    if (c.indexOf("fa") === 0 || c.indexOf("per") === 0 || c.indexOf("far") === 0) return "fa";
    if (c.length > 2 && c.charAt(2) === "-") return c.slice(0, 2);
    return c.slice(0, 2);
  }

  function detectRequestedLang(text) {
    var t = String(text || "");
    if (/t[uü]rk|turkish|به\s*ترکی|ترکی\s*بگو|sa\s+turkish|sa\s+turko/i.test(t)) return "tr";
    if (/persian|farsi|فارسی|به\s*فارسی/i.test(t)) return "fa";
    if (/tagalog|filipino|pilipino|تاگالوگ/i.test(t)) return "tl";
    if (/arabic|عربي|عربی|به\s*عربی/i.test(t)) return "ar";
    if (/spanish|espa[nñ]ol|castellano|اسپانیایی/i.test(t)) return "es";
    if (/\benglish\b|انگلیسی|به\s*انگلیسی/i.test(t)) return "en";
    if (/french|fran[cç]ais|فرانسه/i.test(t)) return "fr";
    return "";
  }

  function hasPhones(s) {
    return /759320|952\s*4822|0203|07983|seven nine eight|s[iı]f[iı]r yedi|صفر هفت|cero siete|zero seven nine/i.test(s || "");
  }

  function hasLike(s) {
    return /like|review|5-star|five.star|لایک|ستاره|be[gğ]eni|y[iı]ld[iı]z|bituin|estrellas|نجمة|إعجاب|bintang/i.test(s || "");
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

  function withGreet(text, lang) {
    var fa = lang === "fa" || hasPersian(text);
    if (fa) return wrapPersianDisplay(text);
    var g = GREET[lang] || GREET.en;
    var t = String(text || "").replace(/^\s+/, "");
    t = t.replace(/^Hello\.\s*I am the (?:Head|Senior) Engineer[^.]*\.\s*/i, "");
    if (!t) return g.replace(/\s+$/, "");
    if (/Cold Direct|ColdDirect|کولد|کُلد/i.test(t)) return t;
    return g + t;
  }

  function ensureClosing(text, lang) {
    if (lang === "fa" || hasPersian(text)) return wrapPersianDisplay(text);
    var t = String(text || "");
    if (hasPhones(t) && hasLike(t)) return t;
    return (t ? t.replace(/\s+$/, "") : "") + (CLOSE_D[lang] || CLOSE_D.en);
  }

  function playCtx() {
    var AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return null;
    if (!window.__cdPlayCtx) window.__cdPlayCtx = new AC();
    if (window.__cdPlayCtx.state === "suspended") {
      try { window.__cdPlayCtx.resume(); } catch (e1) {}
    }
    return window.__cdPlayCtx;
  }

  function player() {
    if (!window.__cdVoicePlayer) {
      var a = document.getElementById("cd-voice-html5") || new Audio();
      a.setAttribute("playsinline", "true");
      a.setAttribute("webkit-playsinline", "true");
      a.preload = "auto";
      window.__cdVoicePlayer = a;
    }
    return window.__cdVoicePlayer;
  }

  function unlockAudio() {
    try {
      var ctx = playCtx();
      if (ctx && !unlocked) {
        var buf = ctx.createBuffer(1, 1, 22050);
        var src = ctx.createBufferSource();
        src.buffer = buf;
        src.connect(ctx.destination);
        src.start(0);
        unlocked = true;
      }
    } catch (e1) {}
    try {
      var a = player();
      if (a && !playing) {
        a.src = SILENT_WAV;
        var p = a.play();
        if (p && p.catch) p.catch(function () {});
      }
    } catch (e2) {}
  }

  function b64ToBytes(b64) {
    var bin = atob(b64);
    var out = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
    return out;
  }

  function stopPlayback() {
    playing = false;
    if (listenBtn) {
      listenBtn.classList.remove("is-on");
      listenBtn.setAttribute("aria-pressed", "false");
    }
    try { if (playSource) { playSource.onended = null; playSource.stop(); } } catch (e1) {}
    playSource = null;
    var el = window.__cdVoicePlayer;
    if (el) {
      el.onended = null;
      try { el.pause(); el.currentTime = 0; } catch (e2) {}
    }
  }

  function playBytes(bytes, mime, onDone) {
    stopPlayback();
    var ctx = playCtx();
    playing = true;
    window.__cdAudioPlayed = true;
    if (listenBtn) {
      listenBtn.classList.add("is-on");
      listenBtn.setAttribute("aria-pressed", "true");
    }
    setStatus("active", "🔊 Speaking Answer...");
    var type = mime || "audio/wav";
    var copy = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
    var blob = new Blob([bytes], { type: type });
    var url = URL.createObjectURL(blob);

    function done() {
      playing = false;
      if (listenBtn) {
        listenBtn.classList.remove("is-on");
        listenBtn.setAttribute("aria-pressed", "false");
      }
      URL.revokeObjectURL(url);
      highlightCta(true);
      if (lastLang !== "fa") setStatus("active", "If this helped, please leave a like and a 5-star review.");
      else setStatus("active", "");
      if (onDone) onDone();
    }

    function viaElement() {
      var el = player();
      el.onended = done;
      el.src = url;
      el.playbackRate = 1;
      var p = el.play();
      if (p && p.catch) p.catch(function () { done(); });
    }

    if (ctx && ctx.decodeAudioData) {
      try {
        var pdec = ctx.decodeAudioData(copy);
        if (pdec && pdec.then) {
          pdec.then(function (buf) {
            var src = ctx.createBufferSource();
            src.buffer = buf;
            src.connect(ctx.destination);
            playSource = src;
            src.onended = done;
            src.start(0);
          }).catch(viaElement);
          return;
        }
        ctx.decodeAudioData(copy, function (buf) {
          var src = ctx.createBufferSource();
          src.buffer = buf;
          src.connect(ctx.destination);
          playSource = src;
          src.onended = done;
          src.start(0);
        }, viaElement);
        return;
      } catch (e3) { viaElement(); return; }
    }
    viaElement();
  }

  function playVaultAudio(data) {
    var b64 = data && (data.audio_base64 || (data.audio && (data.audio.data || data.audio.audio_base64)));
    var mime = (data && (data.audio_mime || (data.audio && data.audio.mime))) || "audio/wav";
    if (!b64) return false;
    lastAudio = { data: b64, mime: mime };
    playBytes(b64ToBytes(b64), mime);
    return true;
  }

  function postVault(payload, timeoutMs) {
    var i = 0;
    var ms = timeoutMs == null ? DIAGNOSE_MS : timeoutMs;
    function tryNext(err) {
      if (i >= ENDPOINTS.length) return Promise.reject(err || new Error("Voice vault unavailable"));
      var url = ENDPOINTS[i++];
      var ctrl = typeof AbortController !== "undefined" ? new AbortController() : null;
      var timer = ms && ctrl ? setTimeout(function () { try { ctrl.abort(); } catch (e0) {} }, ms) : null;
      return fetch(url, {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-CD-IP": MARK, "Accept": "application/json" },
        body: JSON.stringify(payload),
        signal: ctrl ? ctrl.signal : undefined
      }).then(function (res) {
        if (res.status === 404 || res.status === 405) return tryNext(new Error("skip"));
        return res.text().then(function (txt) {
          var json = {};
          try { json = txt ? JSON.parse(txt) : {}; } catch (e4) { json = { error: txt }; }
          if (!res.ok) throw new Error(json.error || json.message || ("HTTP " + res.status));
          return json;
        });
      }).catch(function (e) {
        if (e && e.name === "AbortError") throw e;
        if (i < ENDPOINTS.length) return tryNext(e);
        throw e;
      }).finally(function () {
        if (timer) clearTimeout(timer);
      });
    }
    return tryNext();
  }

  function pickMime() {
    if (!window.MediaRecorder || !MediaRecorder.isTypeSupported) return "";
    var types = ["audio/webm;codecs=opus", "audio/webm", "audio/mp4", "audio/aac", "audio/ogg;codecs=opus"];
    for (var i = 0; i < types.length; i++) if (MediaRecorder.isTypeSupported(types[i])) return types[i];
    return "";
  }

  function setSpeakUi(on) {
    if (!speakBtn) return;
    speakBtn.classList.toggle("is-on", on);
    speakBtn.setAttribute("aria-pressed", on ? "true" : "false");
    speakBtn.textContent = on ? STOP_LABEL : SPEAK_LABEL;
    if (root) root.classList.toggle("is-live", on);
  }

  function killMic() {
    if (recStream) {
      recStream.getTracks().forEach(function (t) { try { t.stop(); } catch (e1) {} });
      recStream = null;
    }
  }

  function stopMeter() {
    if (meterTimer) { clearInterval(meterTimer); meterTimer = null; }
    try { if (meterSrc) meterSrc.disconnect(); } catch (e1) {}
    meterSrc = null;
    if (meterCtx) {
      try { meterCtx.close(); } catch (e2) {}
      meterCtx = null;
    }
    if (meterEl) {
      meterEl.hidden = true;
      var bar = meterEl.querySelector("i");
      if (bar) bar.style.width = "0";
    }
  }

  function stopSr() {
    if (sr) {
      try { sr.onresult = null; sr.onend = null; sr.onerror = null; sr.stop(); } catch (e1) {}
      sr = null;
    }
  }

  function startMeter(stream) {
    var AC = window.AudioContext || window.webkitAudioContext;
    if (!AC || !meterEl) return;
    try {
      if (meterCtx) { try { meterCtx.close(); } catch (e0) {} meterCtx = null; }
      meterCtx = new AC();
      meterSrc = meterCtx.createMediaStreamSource(stream);
      var an = meterCtx.createAnalyser();
      an.fftSize = 1024;
      meterSrc.connect(an);
      var buf = new Uint8Array(an.fftSize);
      var bar = meterEl.querySelector("i");
      meterEl.hidden = false;
      meterTimer = setInterval(function () {
        if (!recording) return;
        an.getByteTimeDomainData(buf);
        var sum = 0;
        for (var i = 0; i < buf.length; i++) { var v = (buf[i] - 128) / 128; sum += v * v; }
        var rms = Math.sqrt(sum / buf.length);
        if (bar) bar.style.width = Math.min(100, Math.round(rms * 280)) + "%";
      }, 80);
    } catch (e1) { stopMeter(); }
  }

  function startSpeechRec() {
    if (/iPad|iPhone|iPod/.test(navigator.userAgent || "")) return false;
    var Ctor = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Ctor) return false;
    try {
      srText = "";
      srFinal = "";
      sr = new Ctor();
      sr.interimResults = true;
      sr.continuous = true;
      sr.lang = "en-GB";
      sr.onresult = function (ev) {
        var finals = "";
        var inter = "";
        for (var i = 0; i < ev.results.length; i++) {
          if (ev.results[i].isFinal) finals += ev.results[i][0].transcript + " ";
          else inter += ev.results[i][0].transcript;
        }
        if (finals.replace(/\s+/g, " ").trim()) srFinal = (srFinal + " " + finals).replace(/\s+/g, " ").trim();
        srText = (srFinal + " " + inter).replace(/\s+/g, " ").trim();
        if (srText) upsertLive("user", srText, false);
      };
      sr.onend = function () {
        if (!recording) return;
        try { sr.start(); } catch (e2) {}
      };
      sr.start();
      return true;
    } catch (e3) {
      sr = null;
      return false;
    }
  }

  function startRec() {
    if (recording || recStarting) return;
    userCollapsed = false;
    openPanel(true);
    unlockAudio();
    stopPlayback();
    stopSr();
    recording = true;
    recStarting = true;
    recBeganAt = Date.now();
    recChunks = [];
    liveUser = null;
    setSpeakUi(true);
    setStatus("active", "Listening — tap STOP & SEND when you finish.");
    upsertLive("user", "Listening…", false);
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || !window.MediaRecorder) {
      recStarting = false;
      recording = false;
      setSpeakUi(false);
      setStatus("error", "Voice recording isn't supported on this browser.");
      return;
    }
    navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true }
    }).then(function (stream) {
      recStarting = false;
      if (!recording) {
        stream.getTracks().forEach(function (t) { t.stop(); });
        return;
      }
      recStream = stream;
      var mime = pickMime();
      try {
        recorder = mime ? new MediaRecorder(stream, { mimeType: mime }) : new MediaRecorder(stream);
      } catch (e1) {
        recorder = new MediaRecorder(stream);
      }
      recorder.ondataavailable = function (ev) { if (ev.data && ev.data.size) recChunks.push(ev.data); };
      recorder.start(200);
      startMeter(stream);
      startSpeechRec();
      recTimer = setTimeout(function () { if (recording) finishRec(); }, MAX_MS);
      setStatus("active", "Listening — tap STOP & SEND when you finish.");
    }).catch(function () {
      recStarting = false;
      recording = false;
      setSpeakUi(false);
      setStatus("error", "Microphone blocked — allow the mic and tap SPEAK again.");
    });
  }

  function blobToB64(blob) {
    return new Promise(function (resolve) {
      var r = new FileReader();
      r.onload = function () {
        var s = String(r.result || "");
        var i = s.indexOf(",");
        resolve(i >= 0 ? s.slice(i + 1) : "");
      };
      r.onerror = function () { resolve(""); };
      r.readAsDataURL(blob);
    });
  }

  function endCapture(onStopped) {
    recording = false;
    recStarting = false;
    setSpeakUi(false);
    if (recTimer) { clearTimeout(recTimer); recTimer = null; }
    stopSr();
    stopMeter();
    var rec = recorder;
    recorder = null;
    function finish(stoppedRec) {
      killMic();
      if (onStopped) onStopped(stoppedRec);
    }
    if (!rec) {
      finish(null);
      return;
    }
    var done = false;
    rec.onstop = function () {
      if (done) return;
      done = true;
      finish(rec);
    };
    try {
      if (rec.state !== "inactive") rec.stop();
      else rec.onstop();
    } catch (e1) { rec.onstop(); }
  }

  function cancelRec() {
    endCapture(function () { recChunks = []; });
    setStatus("", "Tap SPEAK, then STOP & SEND when you finish.");
  }

  function finishRec() {
    if (!recording && !recStarting) return;
    setStatus("connecting", "Diagnosing fault...");
    var spoken = srText;
    endCapture(function (rec) {
      var type = String((rec && rec.mimeType) || pickMime() || "audio/webm");
      var blob = new Blob(recChunks, { type: type });
      recChunks = [];
      function go(audio) {
        if (spoken && spoken.length >= 2) ask(spoken, audio);
        else if (audio) ask("", audio);
        else setStatus("error", "That was too short — tap SPEAK and try again.");
      }
      if (blob.size >= 800) {
        blobToB64(blob).then(function (b64) {
          go(b64 ? { data: b64, mime: type } : null);
        });
      } else {
        go(null);
      }
    });
  }

  function ask(text, audio) {
    var q = (text || "").replace(/\s+/g, " ").trim();
    if (!q && !(audio && audio.data)) {
      setStatus("error", "Tap SPEAK and record your question.");
      return;
    }
    var seq = ++askSeq;
    unlockAudio();
    openPanel(true);
    stopPlayback();
    if (q) upsertLive("user", q, true);
    setStatus("connecting", "Diagnosing fault...");
    var langHint = detectRequestedLang(q);
    var payload = {
      mode: "diagnose",
      text: q,
      language: langHint,
      langHint: langHint,
      page: location.pathname,
      watermark: MARK
    };
    if (audio && audio.data) {
      payload.audio = audio.data;
      payload.mime = audio.mime || "audio/webm";
    }
    postVault(payload, DIAGNOSE_MS).then(function (data) {
      if (seq !== askSeq) return;
      var rawSpoken = data.display_text || data.spoken || data.summary || "";
      var lang = canonLang(data.language || data.target_language_code || langHint) || (hasPersian(rawSpoken) ? "fa" : "en");
      if (hasPersian(rawSpoken) && !langHint) lang = "fa";
      if (langHint) lang = langHint;
      lastLang = lang;
      if (data.transcript) upsertLive("user", data.transcript, true);
      var fa = lang === "fa";
      var spokenOut = fa ? wrapPersianDisplay(rawSpoken) : ensureClosing(withGreet(rawSpoken, lang), lang);
      var serverTts = String(data.tts_text || data.spoken_text || "");
      var ttsOut = fa
        ? ((serverTts.indexOf("درود بر شما") === 0 || serverTts.indexOf("دُرود بر شُما") === 0) ? serverTts : persianAudioText(rawSpoken))
        : (serverTts || spokenOut);
      lastSpoken = spokenOut;
      lastTtsText = ttsOut;
      upsertLive("bot", spokenOut, true);
      if (playVaultAudio(data)) return;
      return postVault({ mode: "tts", text: ttsOut, language: lang, watermark: MARK }, TTS_MS).then(function (v) {
        if (seq !== askSeq) return;
        if (!playVaultAudio(v)) {
          highlightCta(true);
          setStatus("active", "Answer is written below. Tap LISTEN if audio is blocked.");
        }
      });
    }).catch(function (err) {
      if (seq !== askSeq) return;
      try { console.error("ColdDirect diagnose error", err); } catch (e1) {}
      setStatus("error", "The diagnosis could not start. Please tap SPEAK again.");
    });
  }

  function onSpeakPointer(ev) {
    if (ev && ev.pointerType === "mouse" && ev.button !== 0) return;
    if (recording || recStarting) return;
    unlockAudio();
    startRec();
  }

  function onSpeakClick(ev) {
    if (ev) ev.preventDefault();
    if ((recording || recStarting) && Date.now() - recBeganAt > 400) finishRec();
  }

  function listenNow() {
    userCollapsed = false;
    openPanel(true);
    unlockAudio();
    if (lastAudio && lastAudio.data) {
      playBytes(b64ToBytes(lastAudio.data), lastAudio.mime || "audio/wav");
      return;
    }
    if (lastSpoken) {
      setStatus("connecting", "Preparing the Head Engineer's voice…");
      postVault({ mode: "tts", text: lastTtsText || ttsPayload(lastSpoken, lastLang), language: lastLang, watermark: MARK }, TTS_MS).then(function (v) {
        if (!playVaultAudio(v)) setStatus("active", lastSpoken);
      }).catch(function () {
        setStatus("active", lastSpoken);
      });
      return;
    }
    setStatus("", "Tap SPEAK, then STOP & SEND when you finish.");
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

  function warmEngine() {
    try { playCtx(); } catch (e1) {}
    try {
      var a = player();
      a.src = SILENT_WAV;
      if (a.load) a.load();
    } catch (e2) {}
    if (navigator.permissions && navigator.permissions.query) {
      try {
        navigator.permissions.query({ name: "microphone" }).then(function (p) {
          if (p && p.state === "granted" && navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ audio: true }).then(function (s) {
              s.getTracks().forEach(function (t) { try { t.stop(); } catch (e3) {} });
            }).catch(function () {});
          }
        }).catch(function () {});
      } catch (e4) {}
    }
  }

  function bindUi() {
    speakBtn.addEventListener("pointerdown", onSpeakPointer);
    speakBtn.addEventListener("click", onSpeakClick);
    listenBtn.addEventListener("click", listenNow);
    if (closeBtn) closeBtn.addEventListener("click", function (ev) {
      ev.preventDefault();
      ev.stopPropagation();
      if (recording || recStarting) cancelRec();
      stopPlayback();
      closePanel();
    });
    document.addEventListener("pointerdown", function () { unlockAudio(); }, { capture: true, once: true });
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
    if (document.getElementById("cd-voice-html5")) window.__cdVoicePlayer = document.getElementById("cd-voice-html5");
    bindUi();
    warmEngine();
    setStatus("", "Tap SPEAK, then STOP & SEND when you finish.");
  }

  function boot() { mount(); }
  if (document.body) boot();
  document.addEventListener("DOMContentLoaded", boot);
  window.addEventListener("load", boot);
  setTimeout(boot, 60);
  setTimeout(boot, 500);
})();
