/* ColdDirect Voice Bar — homepage-only test widget
 * Watermark: CD-UK-IP-2026-994821-VOICE-AI
 * Owner: ColdDirect Ltd, colddirect.co.uk, 27 Felixstowe Road, Enfield, London N9 0DX
 * UK Copyright Act 1988 & UK Trade Secrets Regulations 2018
 */
(function () {
  "use strict";

  var path = String(location.pathname || "/").replace(/\/index\.html?$/i, "/");
  if (path !== "/" && path !== "") return;

  var MARK = "CD-UK-IP-2026-994821-VOICE-AI";
  var TITLE = "Ask me anything with your language about refrigeration and catering diagnosing";
  var PHONE_DISPLAY = "07983 759320";
  var PHONE_HREF = "tel:07983759320";
  var MAIL_HREF = "mailto:info@colddirect.co.uk";
  var LICENSE_HREF = "mailto:info@colddirect.co.uk?subject=Official%20B2B%20License%20Request%20-%20ColdDirect%20Voice%20AI";
  var ENDPOINTS = [
    "/colddirect-voice-vault.aspx",
    "/api/colddirect-voice-vault.php",
    "/api/colddirect-voice-vault.js"
  ];
  var CHIPS = [
    "Foster Fridge E1",
    "Ice Machine Not Making Ice",
    "Cold Room Ice-Up"
  ];
  var MAX_MS = 60000;
  var SILENCE_MS = 3000;
  var NO_SPEECH_MS = 9000;
  var PACE = 0.95;
  var SPEAK_LABEL = "🎤 SPEAK";
  var STOP_LABEL = "⏹ STOP & SEND";

  var root, drawer, input, statusEl, speakBtn, listenBtn, toggleBtn;
  var cardEls = {};
  var audioCtx = null;
  var unlocked = false;
  var recStream = null;
  var recorder = null;
  var recChunks = [];
  var recTimer = null;
  var meterTimer = null;
  var meterSrc = null;
  var recording = false;
  var askSeq = 0;
  var voicePending = false;
  var lastSpoken = "";
  var lastLang = "en";
  var parts = [];
  var partIdx = 0;
  var partsDone = true;
  var queueOn = false;
  var waitingNext = false;
  var playing = false;
  var playSource = null;
  var playEl = null;

  function $(sel, el) { return (el || document).querySelector(sel); }

  function unlockAudio() {
    try {
      if (!audioCtx) {
        var AC = window.AudioContext || window.webkitAudioContext;
        if (AC) audioCtx = new AC();
      }
      if (audioCtx && audioCtx.state === "suspended") audioCtx.resume();
      if (!unlocked && audioCtx) {
        var buf = audioCtx.createBuffer(1, 1, 22050);
        var src = audioCtx.createBufferSource();
        src.buffer = buf;
        src.connect(audioCtx.destination);
        src.start(0);
        unlocked = true;
      }
    } catch (e) { /* iOS unlock is best-effort */ }
  }

  function setStatus(msg) {
    if (statusEl) statusEl.textContent = msg || "";
  }

  function openDrawer() {
    root.classList.add("is-open");
    toggleBtn.setAttribute("aria-expanded", "true");
    toggleBtn.textContent = "▲";
  }

  function closeDrawer() {
    root.classList.remove("is-open");
    toggleBtn.setAttribute("aria-expanded", "false");
    toggleBtn.textContent = "▼";
  }

  function toggleDrawer() {
    if (root.classList.contains("is-open")) closeDrawer();
    else openDrawer();
  }

  function showShield(extra) {
    var modal = $("#cd-voice-ip-modal");
    if (!modal) return;
    $("#cd-voice-ip-extra").textContent = extra || "This Voice AI widget is protected UK intellectual property of ColdDirect Ltd.";
    modal.hidden = false;
  }

  function hideShield() {
    var modal = $("#cd-voice-ip-modal");
    if (modal) modal.hidden = true;
  }

  function b64ToBytes(b64) {
    var bin = atob(b64);
    var out = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
    return out;
  }

  var SILENT_WAV = "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAABErAAABAAgAZGF0YQAAAAA=";

  function player() {
    if (!window.__cdVoicePlayer) {
      var a = new Audio();
      a.setAttribute("playsinline", "true");
      a.setAttribute("webkit-playsinline", "true");
      a.preload = "auto";
      window.__cdVoicePlayer = a;
    }
    playEl = window.__cdVoicePlayer;
    return playEl;
  }

  // iOS only lets an element play later (after a fetch) if it already played inside a tap.
  function primePlayer() {
    unlockAudio();
    var a = player();
    if (playing) return;
    try {
      a.src = SILENT_WAV;
      var p = a.play();
      if (p && p.catch) p.catch(function () {});
    } catch (e) {}
  }

  function stopCurrent() {
    playing = false;
    listenBtn.classList.remove("is-on");
    listenBtn.setAttribute("aria-pressed", "false");
    try { if (playSource) { playSource.onended = null; playSource.stop(); } } catch (e) {}
    playSource = null;
    if (playEl) {
      playEl.onended = null;
      try { playEl.pause(); playEl.currentTime = 0; } catch (e2) {}
    }
  }

  function stopPlayback() {
    queueOn = false;
    waitingNext = false;
    stopCurrent();
  }

  // The answer arrives as ordered parts (Piper sends sentence by sentence); play them back to back.
  function playQueue() {
    queueOn = true;
    partIdx = 0;
    playNextPart();
  }

  function playNextPart() {
    if (!queueOn) return;
    if (partIdx >= parts.length) {
      if (!partsDone) {
        waitingNext = true;
        listenBtn.classList.add("is-on");
        return;
      }
      queueOn = false;
      listenBtn.classList.remove("is-on");
      return;
    }
    var p = parts[partIdx++];
    playBytes(b64ToBytes(p.data), p.mime, playNextPart);
  }

  function addPart(p) {
    parts.push(p);
    if (waitingNext && queueOn) {
      waitingNext = false;
      playNextPart();
    }
  }

  function endParts() {
    partsDone = true;
    if (waitingNext && queueOn) {
      waitingNext = false;
      queueOn = false;
      listenBtn.classList.remove("is-on");
    }
  }

  function playBytes(bytes, mime, onDone) {
    stopCurrent();
    unlockAudio();
    playing = true;
    listenBtn.classList.add("is-on");
    listenBtn.setAttribute("aria-pressed", "true");
    var type = mime || "audio/wav";
    var blob = new Blob([bytes], { type: type });
    var url = URL.createObjectURL(blob);

    function done() {
      playing = false;
      listenBtn.classList.remove("is-on");
      listenBtn.setAttribute("aria-pressed", "false");
      URL.revokeObjectURL(url);
      if (onDone) onDone();
    }

    var el = player();
    el.onended = done;
    el.src = url;
    el.playbackRate = PACE;
    var p = el.play();
    if (p && p.catch) p.catch(function () { viaContext(); });

    function viaContext() {
      if (!audioCtx) { done(); setStatus("Tap ▶ Listen Answer to hear the diagnosis."); return; }
      audioCtx.decodeAudioData(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), function (buf) {
        var src = audioCtx.createBufferSource();
        src.buffer = buf;
        src.playbackRate.value = PACE;
        src.connect(audioCtx.destination);
        playSource = src;
        src.onended = done;
        src.start(0);
      }, function () { done(); setStatus("Tap ▶ Listen Answer to hear the diagnosis."); });
    }
  }

  var UK_MALE_PREFS = [
    /Google UK English Male/i,
    /Microsoft Ryan Online \(Natural\)/i,
    /Microsoft Thomas Online \(Natural\)/i,
    /Microsoft Alfie Online \(Natural\)/i,
    /Microsoft Oliver Online \(Natural\)/i,
    /Microsoft George/i,
    /^Daniel/i,
    /Arthur|Oliver|Reed|Rocky/i
  ];

  // Only voices known to be male are ever used. Unknown or default voices are treated as female and
  // skipped, so a device with no male voice stays silent (the answer is still written on the card).
  var FEMALE_VOICE = /female|woman|girl|libby|sonia|maisie|hazel|susan|kate|serena|martha|fiona|karen|moira|samantha|victoria|zira|tessa|veena|allison|\bava\b|nicky|zoe|amelie|anna|ellen|joana|laura|luciana|monica|paulina|sara|yuna|alice|\balva\b|danielle|carmit|damayanti|ioana|kanya|lekha|mariska|melina|milena|nora|satu|zuzana|yelda|lana|dilara|zeina|salma|aria|jenny|emma|michelle|clara|elsa|natasha|heera|kalpana|neerja|swara|catherine|shelley|sandy|flo\b|grandma|emel|seda|hoda|zariyah|amina|elvira|katja|denise|isabella|elsa|dominika|agnieszka|paulina|alina|svetlana|polina|xiaoxiao|hiujin/i;
  var MALE_VOICE = /\bmale\b|daniel|ryan|george|oliver|arthur|aaron|fred\b|\balex\b|majid|dariush|farid|thomas|alfie|david|\bmark\b|\bguy\b|james|rishi|\btom\b|gordon|\blee\b|reed|rocko|eddy|ralph|albert|bruce|jorge|diego|juan|carlos|xander|yannick|luca|maged|tarik|ahmet|hamed|madhur|prabhat|alvaro|pablo|raul|stefan|henri|conrad|killian|dmitry|ostap|marek|emil|duarte|antonio|asad|pradeep|ojas|yunxi|yunyang|cem\b/i;

  function isMale(v) {
    var n = v.name || "";
    if (FEMALE_VOICE.test(n)) return false;
    if (/^Google/i.test(n) && !/\bmale\b/i.test(n)) return false;
    return MALE_VOICE.test(n);
  }

  function pickVoice(code) {
    var voices = window.speechSynthesis.getVoices() || [];
    var same = voices.filter(function (v) { return String(v.lang || "").slice(0, 2).toLowerCase() === code && isMale(v); });
    if (code === "en") {
      var gb = same.filter(function (v) { return /en[-_]gb/i.test(v.lang || ""); });
      for (var i = 0; i < UK_MALE_PREFS.length; i++) {
        for (var j = 0; j < gb.length; j++) if (UK_MALE_PREFS[i].test(gb[j].name || "")) return gb[j];
      }
      return gb[0] || same[0] || null;
    }
    var natural = same.filter(function (v) { return /natural|neural|online/i.test(v.name || ""); });
    return natural[0] || same[0] || null;
  }

  function speakFallback(text, lang) {
    if (!text || !window.speechSynthesis) return false;
    try {
      window.speechSynthesis.cancel();
      var code = String(lang || lastLang || "en").slice(0, 2).toLowerCase();
      var u = new SpeechSynthesisUtterance(text);
      u.rate = 0.94;
      u.pitch = 0.96;
      u.voice = pickVoice(code);
      if (!u.voice) return false;
      u.lang = (u.voice && u.voice.lang) || ({ en: "en-GB", fa: "fa-IR", ar: "ar-SA", tr: "tr-TR", es: "es-ES", hi: "hi-IN" }[code] || "en-GB");
      u.onend = function () {
        playing = false;
        listenBtn.classList.remove("is-on");
        listenBtn.setAttribute("aria-pressed", "false");
      };
      playing = true;
      listenBtn.classList.add("is-on");
      listenBtn.setAttribute("aria-pressed", "true");
      window.speechSynthesis.speak(u);
      return true;
    } catch (e) {
      return false;
    }
  }

  function playDiagnosis() {
    unlockAudio();
    if (playing || queueOn) {
      stopPlayback();
      try { window.speechSynthesis && window.speechSynthesis.cancel(); } catch (e) {}
      return;
    }
    if (parts.length) {
      playQueue();
      return;
    }
    if (voicePending) {
      primePlayer();
      setStatus("Head Engineer's voice is on its way — it will play in a moment.");
      return;
    }
    if (lastSpoken) {
      if (!speakFallback(lastSpoken, lastLang)) setStatus("Voice is busy right now — your answer is written below.");
      return;
    }
    setStatus("Ask a question first, then tap LISTEN.");
  }

  function fillCard(data) {
    cardEls.badge.textContent = data.languageLabel || data.language || "Detected";
    cardEls.summary.textContent = data.summary || data.spoken || "";
    cardEls.cause.textContent = data.cause || "";
    cardEls.checks.innerHTML = "";
    (data.checks || []).forEach(function (c) {
      var li = document.createElement("li");
      li.textContent = c;
      cardEls.checks.appendChild(li);
    });
    cardEls.spoken.textContent = data.spoken || "";
    cardEls.box.hidden = false;
    lastSpoken = data.spoken || data.summary || "";
    lastLang = data.language || "en";
    parts = data.audio && data.audio.data ? [data.audio] : [];
    partsDone = true;
  }

  function postVault(payload) {
    var i = 0;
    function tryNext(err) {
      if (i >= ENDPOINTS.length) {
        return Promise.reject(err || new Error("Voice vault unavailable"));
      }
      var url = ENDPOINTS[i++];
      return fetch(url, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CD-IP": MARK,
          "Accept": "application/json"
        },
        body: JSON.stringify(payload)
      }).then(function (res) {
        if (res.status === 404 || res.status === 405) return tryNext(new Error("skip"));
        return res.text().then(function (txt) {
          var json = {};
          try { json = txt ? JSON.parse(txt) : {}; } catch (e) { json = { error: txt }; }
          if (!res.ok) {
            var msg = json.error || json.message || ("HTTP " + res.status);
            throw new Error(msg);
          }
          return json;
        });
      }).catch(function (e) {
        if (i < ENDPOINTS.length) return tryNext(e);
        throw e;
      });
    }
    return tryNext();
  }

  function requestVoice(data, seq) {
    if (!data.spoken || data.voice === "browser-no-key") {
      voicePending = false;
      if (data.spoken) voiceFallback(data);
      return;
    }
    voicePending = true;
    setStatus(langStatus(data) + " — Head Engineer's voice on its way…");
    var lang = data.language || "";
    postVault({ mode: "tts", text: data.spoken, language: lang, watermark: MARK }).then(function (v) {
      if (seq !== askSeq) return;
      voicePending = false;
      setStatus(langStatus(data));
      var got = v && v.audio_base64 ? { data: v.audio_base64, mime: v.audio_mime } : (v && v.audio && v.audio.data ? v.audio : null);
      if (!got) { voiceFallback(data); return; }
      parts = [got];
      var rest = (v.more || []).slice();
      partsDone = rest.length === 0;
      playQueue();
      fetchRest(rest, v.language || lang, seq);
    }).catch(function () {
      if (seq !== askSeq) return;
      voicePending = false;
      voiceFallback(data);
    });
  }

  // One request at a time: Piper renders faster than real time, so the next part is ready before it is needed.
  function fetchRest(rest, lang, seq) {
    if (seq !== askSeq) return;
    if (!rest.length) { endParts(); return; }
    var text = rest.shift();
    postVault({ mode: "tts", engine: "piper", text: text, language: lang, watermark: MARK }).then(function (v) {
      if (seq !== askSeq) return;
      if (!v || !v.audio_base64) { endParts(); return; }
      if (v.more && v.more.length) rest = v.more.concat(rest);
      addPart({ data: v.audio_base64, mime: v.audio_mime });
      fetchRest(rest, lang, seq);
    }).catch(function () {
      if (seq === askSeq) endParts();
    });
  }

  function voiceFallback(data) {
    if (speakFallback(data.spoken, data.language)) setStatus(langStatus(data));
    else setStatus(langStatus(data) + " — voice is busy right now, your answer is written below.");
  }

  function langStatus(data) {
    return data.languageLabel ? ("Language: " + data.languageLabel) : "Diagnosis ready";
  }

  function ask(text, audio) {
    var q = (text || "").replace(/\s+/g, " ").trim();
    if (!q && !(audio && audio.data)) {
      setStatus("Type a fault or tap SPEAK.");
      return;
    }
    var seq = ++askSeq;
    unlockAudio();
    openDrawer();
    stopPlayback();
    try { window.speechSynthesis && window.speechSynthesis.cancel(); } catch (e0) {}
    parts = [];
    partsDone = true;
    root.classList.add("is-busy");
    setStatus(audio ? "Head Engineer is listening to your recording…" : "Head Engineer is diagnosing…");
    var payload = {
      mode: "diagnose",
      text: q,
      langHint: (navigator.language || "").slice(0, 16),
      page: location.pathname,
      watermark: MARK
    };
    if (audio && audio.data) {
      payload.audio = audio.data;
      payload.mime = audio.mime || "audio/webm";
    }
    postVault(payload).then(function (data) {
      if (seq !== askSeq) return;
      if (data.transcript) input.value = data.transcript;
      fillCard(data);
      setStatus(langStatus(data));
      root.classList.remove("is-busy");
      if (data.audio && data.audio.data) {
        playBytes(b64ToBytes(data.audio.data), data.audio.mime);
      } else {
        requestVoice(data, seq);
      }
    }).catch(function (err) {
      if (seq !== askSeq) return;
      root.classList.remove("is-busy");
      setStatus(err && err.message ? err.message : "Diagnosis unavailable. Call 07983 759320.");
    });
  }

  function pickMime() {
    if (!window.MediaRecorder || !MediaRecorder.isTypeSupported) return "";
    var types = ["audio/webm;codecs=opus", "audio/webm", "audio/mp4", "audio/aac", "audio/ogg;codecs=opus"];
    for (var i = 0; i < types.length; i++) if (MediaRecorder.isTypeSupported(types[i])) return types[i];
    return "";
  }

  function setSpeakUi(on) {
    speakBtn.classList.toggle("is-on", on);
    speakBtn.setAttribute("aria-pressed", on ? "true" : "false");
    speakBtn.textContent = on ? STOP_LABEL : SPEAK_LABEL;
  }

  function stopMeter() {
    if (meterTimer) { clearInterval(meterTimer); meterTimer = null; }
    try { if (meterSrc) meterSrc.disconnect(); } catch (e) {}
    meterSrc = null;
  }

  function stopTracks() {
    if (recStream) {
      recStream.getTracks().forEach(function (t) { try { t.stop(); } catch (e) {} });
      recStream = null;
    }
  }

  function endCapture(onStopped) {
    recording = false;
    setSpeakUi(false);
    if (recTimer) { clearTimeout(recTimer); recTimer = null; }
    stopMeter();
    var rec = recorder;
    recorder = null;
    if (!rec) { stopTracks(); if (onStopped) onStopped(null); return; }
    var done = false;
    rec.onstop = function () {
      if (done) return;
      done = true;
      stopTracks();
      if (onStopped) onStopped(rec);
    };
    try {
      if (rec.state !== "inactive") rec.stop();
      else rec.onstop();
    } catch (e) { rec.onstop(); }
  }

  function cancelRec(msg) {
    endCapture(function () { recChunks = []; });
    setStatus(msg);
  }

  function startMeter(stream) {
    if (!audioCtx) return;
    try {
      meterSrc = audioCtx.createMediaStreamSource(stream);
      var an = audioCtx.createAnalyser();
      an.fftSize = 1024;
      meterSrc.connect(an);
      var buf = new Uint8Array(an.fftSize);
      var floor = 0;
      var heard = false;
      var started = Date.now();
      var lastVoice = started;
      meterTimer = setInterval(function () {
        if (!recording) return;
        an.getByteTimeDomainData(buf);
        var sum = 0;
        for (var i = 0; i < buf.length; i++) { var v = (buf[i] - 128) / 128; sum += v * v; }
        var rms = Math.sqrt(sum / buf.length);
        var now = Date.now();
        if (now - started < 500) { floor = Math.max(floor, rms); return; }
        var thr = Math.min(0.06, Math.max(0.015, floor * 2));
        if (rms > thr) { heard = true; lastVoice = now; }
        if (heard && now - lastVoice > SILENCE_MS) finishRec();
        else if (!heard && now - started > NO_SPEECH_MS) cancelRec("I didn't hear anything — tap SPEAK and try again, or type the fault.");
      }, 100);
    } catch (e) { stopMeter(); }
  }

  function startRec() {
    unlockAudio();
    openDrawer();
    try { window.speechSynthesis && window.speechSynthesis.cancel(); } catch (e0) {}
    stopPlayback();
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || !window.MediaRecorder) {
      setStatus("Voice recording isn't supported on this browser — type the fault instead.");
      return;
    }
    recording = true;
    recChunks = [];
    setSpeakUi(true);
    setStatus("Starting the microphone…");
    navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true }
    }).then(function (stream) {
      if (!recording) { stream.getTracks().forEach(function (t) { t.stop(); }); return; }
      recStream = stream;
      var mime = pickMime();
      try {
        recorder = mime ? new MediaRecorder(stream, { mimeType: mime }) : new MediaRecorder(stream);
      } catch (e) {
        recorder = new MediaRecorder(stream);
      }
      recorder.ondataavailable = function (ev) { if (ev.data && ev.data.size) recChunks.push(ev.data); };
      recorder.start(250);
      startMeter(stream);
      recTimer = setTimeout(function () { if (recording) finishRec(); }, MAX_MS);
      setStatus("Listening in any language… pause for 3 seconds or tap STOP & SEND.");
    }).catch(function () {
      recording = false;
      setSpeakUi(false);
      setStatus("Microphone blocked — allow the mic or type the fault.");
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

  function finishRec() {
    if (!recording) return;
    setStatus("Sending your voice to the Head Engineer…");
    endCapture(function (rec) {
      var type = String((rec && rec.mimeType) || pickMime() || "audio/webm");
      var blob = new Blob(recChunks, { type: type });
      recChunks = [];
      if (blob.size < 2000) {
        setStatus("That was too short — tap SPEAK and try again.");
        return;
      }
      blobToB64(blob).then(function (b64) {
        if (!b64) { setStatus("Couldn't read the recording — please try again."); return; }
        ask("", { data: b64, mime: type });
      });
    });
  }

  function toggleSpeak() {
    if (recording) finishRec();
    else startRec();
  }

  function starHtml() {
    var s = "";
    for (var i = 1; i <= 5; i++) {
      s += '<button type="button" class="cd-voice-star" data-star="' + i + '" aria-label="' + i + ' star">★</button>';
    }
    return s;
  }

  function bindFeedback() {
    var like = $("#cd-voice-like");
    var stars = root.querySelectorAll(".cd-voice-star");
    var saved = {};
    try { saved = JSON.parse(localStorage.getItem("cd-voice-fb") || "{}") || {}; } catch (e) { saved = {}; }
    if (saved.like) like.classList.add("is-on");
    if (saved.stars) {
      stars.forEach(function (b) {
        if (Number(b.getAttribute("data-star")) <= saved.stars) b.classList.add("is-on");
      });
    }
    like.addEventListener("click", function () {
      like.classList.toggle("is-on");
      saved.like = like.classList.contains("is-on");
      try { localStorage.setItem("cd-voice-fb", JSON.stringify(saved)); } catch (e) {}
      setStatus(saved.like ? "Thank you — that helps ColdDirect grow." : "");
    });
    stars.forEach(function (b) {
      b.addEventListener("click", function () {
        var n = Number(b.getAttribute("data-star"));
        saved.stars = n;
        stars.forEach(function (x) {
          x.classList.toggle("is-on", Number(x.getAttribute("data-star")) <= n);
        });
        try { localStorage.setItem("cd-voice-fb", JSON.stringify(saved)); } catch (e2) {}
        setStatus(n === 5 ? "Five stars — thank you for supporting ColdDirect." : "Thanks for the rating.");
      });
    });
  }

  function css() {
    return [
      "html.cd-voice-on{padding-top:calc(44px + env(safe-area-inset-top,0px));}",
      "html.cd-voice-on .cd-main-header,html.cd-voice-on .site-header,html.cd-voice-on header.site{top:calc(44px + env(safe-area-inset-top,0px)) !important;}",
      "@media (min-width:769px){html.cd-voice-on #cd-audio-dock{top:calc(92px + env(safe-area-inset-top,0px)) !important;}}",
      "#cd-voice-root{position:fixed;top:0;left:0;right:0;z-index:99999;font:600 12px/1.3 system-ui,-apple-system,Segoe UI,sans-serif;color:#e2e8f0;}",
      "#cd-voice-root *{box-sizing:border-box;}",
      "#cd-voice-bar{height:calc(44px + env(safe-area-inset-top,0px));padding:0 10px;padding-top:env(safe-area-inset-top,0px);display:flex;align-items:center;gap:8px;background:linear-gradient(90deg,#0b1120 0%,#0f172a 100%);border-bottom:1px solid #1e293b;}",
      "#cd-voice-left{display:flex;align-items:center;gap:8px;min-width:0;flex:1;}",
      "#cd-voice-dot{width:8px;height:8px;border-radius:50%;background:#38bdf8;box-shadow:0 0 0 0 rgba(56,189,248,.7);animation:cdVoicePulse 1.6s infinite;flex:0 0 8px;}",
      "@keyframes cdVoicePulse{0%{box-shadow:0 0 0 0 rgba(56,189,248,.65);}70%{box-shadow:0 0 0 8px rgba(56,189,248,0);}100%{box-shadow:0 0 0 0 rgba(56,189,248,0);}}",
      "#cd-voice-title{min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:11px;font-weight:650;color:#f8fafc;}",
      "#cd-voice-controls{display:flex;align-items:center;gap:6px;flex:0 0 auto;}",
      "#cd-voice-root button.cd-voice-btn{height:28px;padding:0 8px;border:1px solid #334155;border-radius:6px;background:#1e293b;color:#f8fafc;font:700 10px/1 system-ui,sans-serif;letter-spacing:.04em;cursor:pointer;display:inline-flex;align-items:center;gap:4px;}",
      "#cd-voice-root button.cd-voice-btn.is-on{background:#0ea5e9;border-color:#38bdf8;color:#04111f;}",
      "#cd-voice-root button.cd-voice-tog{width:28px;padding:0;justify-content:center;}",
      "#cd-voice-drawer{display:none;max-height:min(70vh,560px);overflow:auto;background:#0f172a;border-bottom:1px solid #1e293b;padding:10px 12px 12px;}",
      "#cd-voice-root.is-open #cd-voice-drawer{display:block;}",
      "#cd-voice-askrow{display:flex;gap:6px;}",
      "#cd-voice-input{flex:1;min-width:0;height:36px;border:1px solid #334155;border-radius:8px;background:#0b1120;color:#f8fafc;padding:0 10px;font:400 16px/1.3 system-ui,sans-serif;}",
      "#cd-voice-chips{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0;}",
      "#cd-voice-root .cd-voice-chip{height:28px;padding:0 10px;border:1px solid #334155;border-radius:999px;background:#111827;color:#cbd5e1;font:600 11px/1 system-ui,sans-serif;cursor:pointer;}",
      "#cd-voice-status{min-height:16px;margin:2px 0 8px;color:#7dd3fc;font:500 11px/1.3 system-ui,sans-serif;}",
      "#cd-voice-card{background:#111827;border:1px solid #1e293b;border-radius:10px;padding:10px;}",
      "#cd-voice-badge{display:inline-block;background:#1d4ed8;color:#fff;border-radius:999px;padding:2px 8px;font:700 10px/1.4 system-ui,sans-serif;margin-bottom:6px;}",
      "#cd-voice-card h3{margin:0 0 6px;font-size:13px;color:#f8fafc;}",
      "#cd-voice-card p,#cd-voice-spoken{margin:0 0 8px;font:400 13px/1.45 system-ui,sans-serif;color:#e2e8f0;}",
      "#cd-voice-card ul{margin:0 0 10px;padding-left:18px;color:#cbd5e1;font:400 13px/1.4 system-ui,sans-serif;}",
      "#cd-voice-ctas{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0;}",
      "#cd-voice-ctas a{display:inline-flex;align-items:center;height:32px;padding:0 10px;border-radius:7px;text-decoration:none;font:700 12px/1 system-ui,sans-serif;}",
      "#cd-voice-ctas a.call{background:#16a34a;color:#fff;}",
      "#cd-voice-ctas a.mail{background:#1e293b;color:#e2e8f0;border:1px solid #334155;}",
      "#cd-voice-fb{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-top:8px;}",
      "#cd-voice-like{height:30px;padding:0 10px;border:1px solid #334155;border-radius:7px;background:#0b1120;color:#e2e8f0;cursor:pointer;font:700 12px/1 system-ui,sans-serif;}",
      "#cd-voice-like.is-on{background:#14532d;border-color:#22c55e;color:#bbf7d0;}",
      "#cd-voice-root .cd-voice-star{border:0;background:transparent;color:#475569;font-size:18px;cursor:pointer;padding:0 1px;}",
      "#cd-voice-root .cd-voice-star.is-on{color:#fbbf24;}",
      "#cd-voice-legal{margin-top:10px;font:500 10px/1.4 system-ui,sans-serif;color:#64748b;}",
      "#cd-voice-legal a{color:#93c5fd;}",
      "#cd-voice-ip-modal{position:fixed;inset:0;z-index:100000;background:rgba(2,6,23,.72);display:flex;align-items:center;justify-content:center;padding:16px;}",
      "#cd-voice-ip-modal[hidden]{display:none !important;}",
      "#cd-voice-ip-box{max-width:420px;background:#0b1120;color:#e2e8f0;border:1px solid #334155;border-radius:12px;padding:16px;}",
      "#cd-voice-ip-box h2{margin:0 0 8px;font-size:16px;}",
      "#cd-voice-ip-box p{margin:0 0 10px;font:400 13px/1.45 system-ui,sans-serif;}",
      "#cd-voice-root.is-busy #cd-voice-dot{background:#fbbf24;}",
      "#cd-voice-root,#cd-voice-bar,#cd-voice-drawer{width:100%;max-width:100vw;box-sizing:border-box;overflow-x:hidden;}",
      "#cd-voice-root button.cd-voice-btn#cd-voice-speak.is-on{background:#dc2626;border-color:#f87171;color:#fff;}",
      "#cd-voice-askrow,#cd-voice-card,#cd-voice-chips,#cd-voice-ctas,#cd-voice-fb{max-width:100%;min-width:0;}",
      "#cd-voice-card p,#cd-voice-card li,#cd-voice-spoken,#cd-voice-legal{overflow-wrap:anywhere;word-break:break-word;}",
      "#cd-voice-card li{color:#e2e8f0 !important;opacity:1 !important;}",
      "#cd-voice-root button.cd-voice-btn#cd-voice-replay{height:32px;margin:0 0 8px;padding:0 12px;font-size:12px;background:#0ea5e9;border-color:#38bdf8;color:#04111f;}",
      "@media (max-width:480px){#cd-voice-bar{padding-left:max(8px,env(safe-area-inset-left,0px));padding-right:max(8px,env(safe-area-inset-right,0px));gap:6px;}#cd-voice-title{font-size:10px;}#cd-voice-controls{gap:4px;}#cd-voice-root button.cd-voice-btn{padding:0 6px;font-size:9.5px;letter-spacing:0;}#cd-voice-root button.cd-voice-tog{width:26px;}#cd-voice-input{font-size:16px;}#cd-voice-drawer{padding:8px max(8px,env(safe-area-inset-right,0px)) 10px max(8px,env(safe-area-inset-left,0px));}}",
      "@media (max-width:360px){#cd-voice-dot{display:none;}#cd-voice-title{font-size:9.5px;}}"
    ].join("");
  }

  function html() {
    return (
      '<!-- ' + MARK + ' ColdDirect Ltd -->' +
      '<div id="cd-voice-bar">' +
        '<div id="cd-voice-left">' +
          '<span id="cd-voice-dot" aria-hidden="true"></span>' +
          '<span id="cd-voice-title">' + TITLE + "</span>" +
        "</div>" +
        '<div id="cd-voice-controls">' +
          '<button type="button" class="cd-voice-btn" id="cd-voice-speak" aria-pressed="false" aria-label="Speak">🎤 SPEAK</button>' +
          '<button type="button" class="cd-voice-btn" id="cd-voice-listen" aria-pressed="false" aria-label="Listen">🔊 LISTEN</button>' +
          '<button type="button" class="cd-voice-btn cd-voice-tog" id="cd-voice-toggle" aria-expanded="false" aria-label="Open diagnosis drawer">▼</button>' +
        "</div>" +
      "</div>" +
      '<div id="cd-voice-drawer">' +
        '<div id="cd-voice-askrow">' +
          '<input id="cd-voice-input" type="text" maxlength="2000" autocomplete="off" placeholder="Type a fault in any language…">' +
          '<button type="button" class="cd-voice-btn" id="cd-voice-ask">Ask</button>' +
        "</div>" +
        '<div id="cd-voice-chips">' +
          CHIPS.map(function (c) { return '<button type="button" class="cd-voice-chip" data-chip="' + c.replace(/"/g, "") + '">' + c + "</button>"; }).join("") +
        "</div>" +
        '<div id="cd-voice-status" role="status"></div>' +
        '<div id="cd-voice-card" hidden>' +
          '<span id="cd-voice-badge">Language</span>' +
          "<h3>Engineer Diagnosis</h3>" +
          '<p id="cd-voice-summary"></p>' +
          "<p><strong>Likely cause:</strong> <span id=\"cd-voice-cause\"></span></p>" +
          "<p><strong>Quick checks</strong></p>" +
          '<ul id="cd-voice-checks"></ul>' +
          '<p id="cd-voice-spoken"></p>' +
          '<button type="button" class="cd-voice-btn" id="cd-voice-replay">▶ Listen Answer</button>' +
          '<div id="cd-voice-ctas">' +
            '<a class="call" href="' + PHONE_HREF + '">Call ' + PHONE_DISPLAY + "</a>" +
            '<a class="mail" href="' + MAIL_HREF + '">Email info@colddirect.co.uk</a>' +
          "</div>" +
          '<div id="cd-voice-fb">' +
            '<button type="button" id="cd-voice-like">Helpful 👍</button>' +
            '<span>' + starHtml() + "</span>" +
          "</div>" +
        "</div>" +
        '<div id="cd-voice-legal">' +
          '<a href="#cd-uk-ip" id="cd-voice-ip-link">UK IP Shield</a> · ' +
          '<a href="' + LICENSE_HREF + '">Request Official B2B License</a><br>' +
          MARK + " · ColdDirect Ltd · 27 Felixstowe Road, Enfield, London N9 0DX" +
        "</div>" +
      "</div>" +
      '<div id="cd-voice-ip-modal" hidden>' +
        '<div id="cd-voice-ip-box">' +
          "<h2>UK IP Shield</h2>" +
          "<p id=\"cd-voice-ip-extra\"></p>" +
          "<p>Protected under the UK Copyright Act 1988 and the UK Trade Secrets Regulations 2018. Unauthorised cloning, scraping or commercial reuse of ColdDirect Voice AI requires an official B2B licence from ColdDirect Ltd (colddirect.co.uk).</p>" +
          "<p>Watermark: " + MARK + "</p>" +
          '<p><a href="' + LICENSE_HREF + '">Request Official B2B License</a></p>' +
          '<button type="button" class="cd-voice-btn" id="cd-voice-ip-close">Close</button>' +
        "</div>" +
      "</div>"
    );
  }

  function mount() {
    if (document.getElementById("cd-voice-root")) return;
    document.documentElement.classList.add("cd-voice-on");
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
    document.body.insertBefore(root, document.body.firstChild);

    drawer = $("#cd-voice-drawer", root);
    input = $("#cd-voice-input", root);
    statusEl = $("#cd-voice-status", root);
    speakBtn = $("#cd-voice-speak", root);
    listenBtn = $("#cd-voice-listen", root);
    toggleBtn = $("#cd-voice-toggle", root);
    cardEls = {
      box: $("#cd-voice-card", root),
      badge: $("#cd-voice-badge", root),
      summary: $("#cd-voice-summary", root),
      cause: $("#cd-voice-cause", root),
      checks: $("#cd-voice-checks", root),
      spoken: $("#cd-voice-spoken", root)
    };

    speakBtn.addEventListener("click", function () { primePlayer(); toggleSpeak(); });
    listenBtn.addEventListener("click", playDiagnosis);
    $("#cd-voice-replay", root).addEventListener("click", function () { if (playing) stopPlayback(); playDiagnosis(); });
    toggleBtn.addEventListener("click", toggleDrawer);
    $("#cd-voice-ask", root).addEventListener("click", function () { primePlayer(); ask(input.value); });
    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter") { e.preventDefault(); primePlayer(); ask(input.value); }
    });
    root.querySelectorAll(".cd-voice-chip").forEach(function (b) {
      b.addEventListener("click", function () {
        primePlayer();
        input.value = b.getAttribute("data-chip") || b.textContent;
        ask(input.value);
      });
    });
    $("#cd-voice-ip-link", root).addEventListener("click", function (e) {
      e.preventDefault();
      showShield("UK intellectual property of ColdDirect Ltd. Commercial licence required for any copy or reuse.");
    });
    $("#cd-voice-ip-close", root).addEventListener("click", hideShield);
    $("#cd-voice-ip-modal", root).addEventListener("click", function (e) {
      if (e.target.id === "cd-voice-ip-modal") hideShield();
    });

    root.addEventListener("contextmenu", function (e) {
      e.preventDefault();
      showShield("Unauthorised inspection or copying of this widget is blocked. UK Copyright Act 1988 & UK Trade Secrets Regulations 2018.");
    });

    bindFeedback();
    try { window.speechSynthesis && window.speechSynthesis.getVoices(); } catch (e) {}
  }

  if (document.body) mount();
  else document.addEventListener("DOMContentLoaded", mount);
})();
