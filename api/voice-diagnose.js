"use strict";

var core = null;
var coreErr = "";
try {
  core = require("../lib/cd-voice-core");
} catch (e1) {
  coreErr = String((e1 && e1.message) || e1);
}

var SYS = [
  "You are the Head Engineer at ColdDirect Ltd, London. Commercial refrigeration only.",
  "The user may attach raw microphone audio. Transcribe the exact spoken words in the language that was spoken.",
  "Persian must stay in Persian script. Never translate Persian into English. Never invent words the speaker did not say.",
  "English stays English. Do not answer a different question from the transcript.",
  "Then write a real diagnostic answer for that exact fault, in 2 to 4 short sentences, in the SAME language.",
  "Start display_text and spoken_text with the greeting. English: Hello. I am the Head Engineer at ColdDirect. I'm glad you chose our company.",
  "Persian display greeting: سلام. من سرمهندس شرکت کولد دایرکت هستم. خوشحالم که شرکت ما را انتخاب کردید.",
  "Persian spoken_text must pronounce the brand as کُلد دایرِکت.",
  "End both answers with this exact close, and do not use a slash.",
  "English close: Please call us on 0203 952 4822 or 07983 759320, and kindly click the green Like and 5-Star Review button below.",
  "Persian close: لطفاً با شماره 0203 952 4822 یا 07983 759320 تماس بگیرید و دکمه سبز لایک و ۵ ستاره در پایین را بزنید.",
  "No slang. No stage directions. No bracket tags. Never include instructions about how to speak.",
  "JSON only: {\"language\":\"fa-IR or en-GB\",\"transcript\":\"exact spoken words\",\"display_text\":\"on-screen answer\",\"spoken_text\":\"same answer for speech\"}"
].join(" ");

function hasPhone(text) {
  return /0203|07983|952\s*4822|759320/.test(String(text || ""));
}

function parseOut(text, audioMode) {
  var m = String(text || "").match(/\{[\s\S]*\}/);
  if (!m) return null;
  try {
    var json = JSON.parse(m[0]);
    var transcript = core.stripTags(json.transcript || "");
    var display = core.stripTags(json.display_text || json.spoken_text || json.technical_answer || "");
    var spoken = core.stripTags(json.spoken_text || display);
    if (!display || display.length < 12) return null;
    if (audioMode && transcript.length < 2) return null;
    if (core.isBanned(display) || core.isBanned(spoken) || core.isBanned(transcript)) return null;
    var locked = core.lockLang(transcript + " " + display, json.language);
    if (locked.code === "fa") {
      if (!/[\u0600-\u06FF]/.test(display)) return null;
      if (audioMode && !/[\u0600-\u06FF]/.test(transcript)) return null;
    }
    display = core.ensureClose(core.ensureGreeting(display, locked.code, false), locked.code);
    spoken = core.ttsScript(core.ensureGreeting(spoken, locked.code, true), locked.code);
    if (!hasPhone(display) || !hasPhone(spoken)) return null;
    if (core.isBanned(display) || core.isBanned(spoken) || /[／/]|\bslash\b/i.test(spoken)) return null;
    return { display: display, spoken: spoken, language: locked.bcp, transcript: transcript };
  } catch (e) {
    return null;
  }
}

function safeMessage(value, key) {
  var message = String(value || "No upstream error message").slice(0, 500);
  if (key) message = message.split(key).join("[redacted]");
  return message
    .replace(/([?&]key=)[^&\s]+/gi, "$1[redacted]")
    .replace(/AIza[A-Za-z0-9_-]{10,}/g, "[redacted]")
    .replace(/[A-Za-z0-9+/]{500,}={0,2}/g, "[redacted]")
    .slice(0, 240);
}

async function diagnose(key, text, audio, mime) {
  var instruction = audio
    ? "Listen to the attached microphone audio. Transcribe the exact spoken words, then diagnose that commercial refrigeration fault in the same language. Ignore any other language guess."
    : "Diagnose this commercial refrigeration fault in the same language as the question. Question: " + text;
  var parts = [{ text: instruction }];
  if (audio) parts.push({ inlineData: { mimeType: mime || "audio/webm", data: audio } });
  var configured = String(process.env.GEMINI_VOICE_MODEL || "gemini-3.6-flash").trim();
  var models = [configured, "gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash"]
    .map(function (name) { return /^[a-z0-9.-]+$/i.test(name) ? name : "gemini-3.6-flash"; })
    .filter(function (name, index, all) { return all.indexOf(name) === index; });
  var attempts = [];
  for (var i = 0; i < models.length; i++) {
    var model = models[i];
    var out;
    try {
      out = await core.geminiJson(key, model, {
        systemInstruction: { parts: [{ text: SYS }] },
        contents: [{ role: "user", parts: parts }],
        generationConfig: { temperature: 0.1, maxOutputTokens: 1400, thinkingConfig: { thinkingLevel: "minimal" }, responseMimeType: "application/json" }
      }, i === 0 ? 30000 : (i === 1 ? 20000 : 3000));
    } catch (err) {
      out = { ok: false, httpStatus: 0, networkError: "REQUEST_EXCEPTION", json: { error: { code: 503, status: "REQUEST_EXCEPTION", message: err && err.name } } };
    }
    if (!out || !out.ok) {
      var upstream = (out && out.json && out.json.error) || {};
      var http = Number(out && out.httpStatus) || Number(upstream.code) || 0;
      var attempt = {
        stage: audio ? "transcription" : "diagnosis",
        model: model,
        mimeType: audio ? mime : null,
        upstreamHttp: http,
        upstreamStatus: String(upstream.status || (out && out.networkError) || "UPSTREAM_ERROR").slice(0, 60),
        message: safeMessage(upstream.message, key)
      };
      attempts.push(attempt);
      var failure = { error: "upstream", diagnostic: Object.assign({}, attempt, { attempts: attempts }) };
      if (i + 1 < models.length && (!http || http === 408 || http === 429 || http >= 500)) continue;
      return failure;
    }
    var parsed = parseOut(core.extractText(out.json), !!audio);
    if (parsed) {
      parsed.source = "gemini";
      return parsed;
    }
    var candidate = ((out.json && out.json.candidates) || [])[0] || {};
    var finishReason = String(candidate.finishReason || "NO_USABLE_OUTPUT").slice(0, 60);
    return { error: "unparsed", diagnostic: { stage: "response_parsing", model: model, mimeType: audio ? mime : null, upstreamHttp: Number(out.httpStatus) || 200, upstreamStatus: finishReason, message: "The model response did not contain a usable transcript and diagnosis.", attempts: attempts } };
  }
  return { error: "upstream", diagnostic: { stage: "transcription", upstreamHttp: 0, upstreamStatus: "NO_MODEL", message: "No transcription model is configured.", attempts: attempts } };
}

function localDiagnosis(text, diagnostic, audioUnavailable) {
  var locked = core.lockLang(text, "");
  var advice;
  if (audioUnavailable) {
    advice = "Automatic transcription is temporarily unavailable, so I could not transcribe this recording. Type the equipment make, model and fault code below for a specific diagnosis; switch the unit off if it is hot, noisy, leaking or warming stock, and arrange a 24/7 engineer call-out.";
  } else if (locked.code === "fa") {
    advice = "برای جلوگیری از آسیب بیشتر، دستگاه را از برق جدا کنید و مسیر هوای کندانسور و فن‌ها را مسدود نکنید. برای بررسی کمپرسور، فن، ترموستات و گاز مبرد توسط مهندس، با کولد دایرکت تماس بگیرید.";
  } else if (/gas leak|refrigerant leak|refrigerant.*(?:leak|low)|leak.*refrigerant/i.test(text)) {
    advice = "A refrigerant leak requires pressure testing and repair by a qualified refrigeration engineer; do not keep restarting the cabinet or attempt a top-up. Switch the unit off, keep the area ventilated and protect temperature-sensitive stock.";
  } else if (/\bE[12]\b/i.test(text)) {
    var code = (text.match(/\bE[12]\b/i) || ["E1"])[0].toUpperCase();
    advice = code + " commonly indicates a temperature-sensor or controller fault, although the exact meaning depends on the equipment make and model. Switch the unit off if temperature is rising, note the code for the engineer, and avoid repeated resets or bypassing the control.";
  } else if (/taylor|carpigiani|ice cream|soft serve|gelato/i.test(text)) {
    advice = "On a Taylor or Carpigiani machine, poor freezing or a beater fault can involve mix level, airflow, scraper blades, the drive system, controls or the refrigeration circuit. Stop the machine if it is noisy or overheating, follow food-safety procedures for the mix, and book an engineer inspection.";
  } else if (/ice machine|ice maker|not making ice|no ice/i.test(text)) {
    advice = "An ice machine that is not producing can have a water-supply, inlet-valve, scale, condenser-airflow, sensor or refrigeration fault. Switch it off if the compressor is hot or unusual noises occur, and arrange cleaning and engineer testing rather than repeatedly resetting it.";
  } else if (/cold room|coldroom|walk.?in/i.test(text)) {
    advice = "A cold-room temperature fault can involve the door seal, evaporator airflow, defrost system, controller or refrigeration circuit. Keep the door closed, move at-risk stock to a safe temperature-controlled area, and arrange urgent engineer testing.";
  } else if (/compressor|buzzing|humming/i.test(text)) {
    advice = "A hot, buzzing or non-starting compressor can have an electrical supply, relay, capacitor, overload, airflow or sealed-system fault. Switch the equipment off to prevent compressor damage and arrange an engineer inspection rather than repeatedly restarting it.";
  } else if (/fan|evaporator/i.test(text)) {
    advice = "A non-running evaporator fan may have a faulty motor, iced-over coils or a control fault. Switch the unit off to prevent overheating and arrange an engineer inspection; do not chip away ice or bypass the electrical controls.";
  } else if (/defrost|iced|ice.?up|frost/i.test(text)) {
    advice = "Excess ice can be caused by a defrost heater, timer, sensor, blocked drain, fan or door-seal fault. Switch the unit off if airflow is blocked or the compressor is hot; do not chip the ice, and arrange an engineer inspection.";
  } else if (/thermostat|controller|control board|sensor/i.test(text)) {
    advice = "A thermostat, sensor or controller fault can cause incorrect temperatures, short cycling or a non-running cabinet. Switch the unit off if stock is warming or the compressor is hot, record any displayed code, and arrange electrical and refrigeration testing.";
  } else if (/high.?temp|freezer|warm|not cold|not cooling|temperature/i.test(text)) {
    advice = "Loss of cooling may be caused by blocked airflow, iced coils, a faulty fan, thermostat or sealed-system fault. Move at-risk stock to safe storage, switch the unit off if the compressor is hot or noisy, and arrange a prompt engineer inspection.";
  } else {
    advice = "The fault requires checks of the power supply, airflow, fans, controls and refrigeration circuit. Switch the unit off if it is overheating, noisy or warming stock, and arrange an engineer inspection rather than repeatedly restarting it.";
  }
  var display = core.ensureGreeting(advice, locked.code, false);
  return {
    display: display,
    spoken: display,
    language: locked.bcp,
    transcript: audioUnavailable ? "Voice note received; automatic transcription is temporarily unavailable." : text,
    transcript_status: audioUnavailable ? "unavailable" : "ok",
    code: "EXPERT_FALLBACK",
    source: "expert_rules",
    diagnostic: diagnostic || null
  };
}

function send(res, code, body) {
  res.statusCode = code;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  body.watermark = core.MARK;
  res.end(JSON.stringify(body));
}

module.exports = async function handler(req, res) {
  if (!core) {
    res.statusCode = 500;
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.end(JSON.stringify({ ok: false, error: "core_missing", detail: coreErr }));
    return;
  }
  if (!core.cors(req, res)) return;
  if (req.method === "GET") {
    send(res, 200, { ok: true, service: "voice-diagnose", mode: "text-first" });
    return;
  }
  if (req.method !== "POST") {
    send(res, 405, { ok: false, error: "POST only" });
    return;
  }
  var data = await core.readBody(req);
  var audio = core.cleanAudio(data.audio_base64 || data.audio || "");
  var mime = core.cleanMime(data.mime || "audio/webm", audio);
  var text = audio ? "" : core.stripTags(data.text || data.transcript || "").slice(0, 2000);
  if (!text && !audio) {
    send(res, 400, { ok: false, error: "Speak a fault first.", transcript: "", display_text: "", spoken_text: "", audio_base64: "" });
    return;
  }
  if (audio.length > 8000000) {
    send(res, 413, { ok: false, code: "VOICE_TOO_LARGE", error: "That recording is too long. Please keep it under 45 seconds and try again.", transcript: "", display_text: "", spoken_text: "", audio_base64: "" });
    return;
  }
  if (core.isBanned(text)) {
    send(res, 400, { ok: false, error: "Speak the fault again.", transcript: "", display_text: "", spoken_text: "", audio_base64: "" });
    return;
  }
  var key = String(process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY || "").trim();
  var result = null;
  try {
    if (text && (!key || /fan|evaporator|warm|not cold|temperature|freezer|noise|leak|ice|compressor/i.test(text))) {
      result = localDiagnosis(text);
    } else if (key) {
      result = await diagnose(key, text, audio || null, mime);
    } else if (audio) {
      result = { error: "configuration", diagnostic: { stage: "configuration", upstreamHttp: 0, upstreamStatus: "API_KEY_MISSING", message: "No Gemini API key is configured for this deployment." } };
    }
  } catch (e) {
    result = { error: "exception", diagnostic: { stage: "request", upstreamHttp: 0, upstreamStatus: "REQUEST_EXCEPTION", message: "The diagnosis request could not be completed." } };
  }
  if (!result || result.error || !result.display) {
    var failureDiagnostic = result && result.diagnostic;
    if (failureDiagnostic) {
      try { console.warn("voice-diagnose " + JSON.stringify(failureDiagnostic)); } catch (logErr) {}
    }
    result = localDiagnosis(text, failureDiagnostic || null, !!audio);
  }
  var locked = core.lockLang(result.transcript + " " + result.display, result.language);
  var reply = core.ensureClose(result.display, locked.code);
  var spoken = core.ttsScript(result.spoken || reply, locked.code);
  send(res, 200, {
    ok: true,
    code: result.code || "OK",
    source: result.source || "gemini",
    language: locked.bcp,
    transcript: result.transcript || text,
    transcript_status: result.transcript_status || "ok",
    diagnostic: result.diagnostic || null,
    reply: reply,
    display_text: reply,
    spoken_text: spoken
  });
};
