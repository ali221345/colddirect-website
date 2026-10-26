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

async function diagnose(key, text, audio, mime) {
  var instruction = audio
    ? "Listen to the attached microphone audio. Transcribe the exact spoken words, then diagnose that commercial refrigeration fault in the same language. Ignore any other language guess."
    : "Diagnose this commercial refrigeration fault in the same language as the question. Question: " + text;
  var parts = [{ text: instruction }];
  if (audio) parts.push({ inlineData: { mimeType: mime || "audio/webm", data: audio } });
  // Keep the complete retry sequence below common serverless timeout limits.
  var models = [
    ["gemini-2.5-flash", 3500],
    ["gemini-2.0-flash", 3000]
  ];
  var lastErr = "";
  for (var i = 0; i < models.length; i++) {
    var out = null;
    try {
      out = await core.geminiJson(key, models[i][0], {
        systemInstruction: { parts: [{ text: SYS }] },
        contents: [{ role: "user", parts: parts }],
        generationConfig: { temperature: 0.1, maxOutputTokens: 400, responseMimeType: "application/json" }
      }, models[i][1]);
    } catch (err) {
      out = { ok: false, json: { error: { code: 408 } } };
    }
    if (!out || !out.ok) {
      lastErr = models[i][0];
      continue;
    }
    var parsed = parseOut(core.extractText(out.json), !!audio);
    if (parsed) return parsed;
    lastErr = models[i][0] + ":unparsed";
  }
  return { error: lastErr || "no_model" };
}

function localDiagnosis(text) {
  var locked = core.lockLang(text, "");
  var advice;
  if (locked.code === "fa") {
    advice = "برای جلوگیری از آسیب بیشتر، دستگاه را از برق جدا کنید و مسیر هوای کندانسور و فن‌ها را مسدود نکنید. برای بررسی کمپرسور، فن، ترموستات و گاز مبرد توسط مهندس، با کولد دایرکت تماس بگیرید.";
  } else if (/fan|evaporator/i.test(text)) {
    advice = "A non-running evaporator fan may have a faulty motor, iced-over coils, or a control fault. Switch the unit off to prevent overheating and arrange an engineer inspection; do not chip away ice or bypass the electrical controls.";
  } else if (/warm|not cold|temperature|freezer/i.test(text)) {
    advice = "Loss of cooling may be caused by blocked airflow, iced coils, a faulty fan, thermostat, or sealed-system fault. Switch the unit off if the compressor is hot or noisy, protect stock, and arrange a prompt engineer inspection.";
  } else {
    advice = "The fault requires checks of the power supply, airflow, fans, controls, and refrigeration circuit. Switch the unit off if it is overheating or noisy and arrange an engineer inspection rather than repeatedly restarting it.";
  }
  var display = core.ensureGreeting(advice, locked.code, false);
  return { display: display, spoken: display, language: locked.bcp, transcript: text };
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
  var mime = core.cleanMime(data.mime || "audio/webm");
  var text = audio ? "" : core.stripTags(data.text || data.transcript || "").slice(0, 2000);
  if (!text && !audio) {
    send(res, 400, { ok: false, error: "Speak a fault first.", transcript: "", display_text: "", spoken_text: "", audio_base64: "" });
    return;
  }
  if (core.isBanned(text)) {
    send(res, 400, { ok: false, error: "Speak the fault again.", transcript: "", display_text: "", spoken_text: "", audio_base64: "" });
    return;
  }
  var key = String(process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY || "").trim();
  if (!key) {
    send(res, 503, { ok: false, error: "The Head Engineer could not hear that. Tap SPEAK and try again.", transcript: "", display_text: "", spoken_text: "", audio_base64: "" });
    return;
  }
  var result = null;
  try {
    result = await diagnose(key, text, audio || null, mime);
  } catch (e) {
    result = { error: "exception" };
  }
  if (text && (!result || result.error || !result.display)) {
    result = localDiagnosis(text);
  }
  if (!result || result.error || !result.display) {
    // Silent, clipped or unintelligible microphone audio is an input failure, not a site outage.
    // Return a structured response so the widget can offer its typed-fault fallback without a console 502.
    send(res, 200, {
      ok: false,
      code: audio ? "VOICE_NOT_UNDERSTOOD" : "DIAGNOSIS_UNAVAILABLE",
      error: audio ? "We could not hear that clearly. Type the fault below or tap SPEAK and try again." : "The diagnosis service is temporarily unavailable. Please try again or call us.",
      transcript: "",
      display_text: "",
      spoken_text: "",
      audio_base64: ""
    });
    return;
  }
  var locked = core.lockLang(result.transcript + " " + result.display, result.language);
  var reply = core.ensureClose(result.display, locked.code);
  var spoken = core.ttsScript(result.spoken || reply, locked.code);
  send(res, 200, {
    ok: true,
    language: locked.bcp,
    transcript: result.transcript || text,
    reply: reply,
    display_text: reply,
    spoken_text: spoken
  });
};
