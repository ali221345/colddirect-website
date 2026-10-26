"use strict";

var core = require("../lib/cd-voice-core");

var SYS = [
  "You are the Head Engineer at ColdDirect Ltd, London. Commercial refrigeration only.",
  "Answer the user's ACTUAL fault question with 2 to 4 short diagnostic sentences.",
  "Do NOT repeat a canned greeting. Do NOT introduce yourself again. No slang. No stage directions.",
  "Never output bracket tags such as [happy], [greeting], [sad].",
  "If the user wrote Persian letters, reply only in Persian (fa-IR). Otherwise reply only in English (en-GB).",
  "Never use Chinese or switch language mid-answer.",
  "Mention 0203 952 4822 / 07983 759320 once at the end only.",
  "JSON only: {\"language\":\"fa-IR or en-GB\",\"transcript\":\"user words\",\"display_text\":\"on-screen answer\",\"spoken_text\":\"same answer for TTS\"}"
].join(" ");

function parseOut(text, fallbackLang) {
  var m = String(text || "").match(/\{[\s\S]*\}/);
  if (!m) return null;
  try {
    var json = JSON.parse(m[0]);
    var display = core.stripTags(json.display_text || json.spoken_text || json.technical_answer || json.spoken || "");
    var spoken = core.stripTags(json.spoken_text || display);
    if (!display) return null;
    var locked = core.lockLang(display + " " + spoken, fallbackLang);
    if (locked.code === "fa" && !/[\u0600-\u06FF]/.test(display)) return null;
    if (!/0203|07983|952\s*4822|759320/.test(display)) {
      display += " " + core.phonesLine(locked.code) + ".";
      spoken += " " + core.phonesLine(locked.code) + ".";
    }
    return { display: display, spoken: spoken, language: locked.bcp };
  } catch (e) {
    return null;
  }
}

async function diagnose(key, text, audio, mime, locked) {
  var parts = [{
    text: "User language lock is " + locked.bcp + ". Diagnose this commercial refrigeration fault. Question: " + text
  }];
  if (audio) parts.push({ inline_data: { mime_type: mime || "audio/webm", data: audio } });
  var models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.5-flash-lite"];
  for (var i = 0; i < models.length; i++) {
    var out = await core.geminiJson(key, models[i], {
      systemInstruction: { parts: [{ text: SYS }] },
      contents: [{ role: "user", parts: parts }],
      generationConfig: { temperature: 0.2, responseMimeType: "application/json" }
    });
    if (out.ok) {
      var parsed = parseOut(core.extractText(out.json), locked.bcp);
      if (parsed) return parsed;
    }
  }
  return null;
}

async function speak(key, spoken, locked) {
  var voice = locked.code === "fa" ? "Charon" : "Puck";
  var out = await core.geminiJson(key, "gemini-2.5-flash-preview-tts", {
    contents: [{ role: "user", parts: [{ text: "Read this exactly in a calm male Head Engineer voice. Do not add words:\n\n" + spoken }] }],
    generationConfig: {
      responseModalities: ["AUDIO"],
      speechConfig: {
        languageCode: locked.bcp,
        voiceConfig: { prebuiltVoiceConfig: { voiceName: voice } }
      }
    }
  });
  if (!out.ok) return null;
  return core.extractAudio(out.json);
}

module.exports = async function handler(req, res) {
  if (!core.cors(req, res)) return;
  if (req.method === "GET") {
    res.statusCode = 200;
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.end(JSON.stringify({ ok: true, service: "voice-diagnose", watermark: core.MARK }));
    return;
  }
  if (req.method !== "POST") {
    res.statusCode = 405;
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.end(JSON.stringify({ ok: false, error: "POST only", watermark: core.MARK }));
    return;
  }
  var data = await core.readBody(req);
  var text = core.stripTags(data.text || data.transcript || "").slice(0, 2000);
  var audio = String(data.audio_base64 || data.audio || "").replace(/\s+/g, "");
  var mime = String(data.mime || "audio/webm").slice(0, 80);
  if (!text && !audio) {
    res.statusCode = 400;
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.end(JSON.stringify({ ok: false, error: "Speak a fault first.", watermark: core.MARK }));
    return;
  }
  var locked = core.lockLang(text, data.language);
  var key = String(process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY || "").trim();
  var result = null;
  if (key) {
    try { result = await diagnose(key, text || "transcribe and diagnose the attached audio", audio || null, mime, locked); } catch (e) { result = null; }
  }
  if (!result) {
    var fb = core.fallbackAnswer(text || "general commercial refrigeration fault");
    locked = core.lockLang(fb + " " + text, locked.bcp);
    result = { display: fb, spoken: fb, language: locked.bcp };
  }
  locked = core.lockLang(result.display, locked.bcp);
  result.display = core.stripTags(result.display);
  result.spoken = core.stripTags(result.spoken || result.display);
  var audioOut = null;
  if (key && result.spoken) {
    try { audioOut = await speak(key, result.spoken, locked); } catch (e2) { audioOut = null; }
  }
  res.statusCode = 200;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.end(JSON.stringify({
    ok: true,
    language: locked.bcp,
    transcript: text,
    display_text: result.display,
    spoken_text: result.spoken,
    audio_base64: audioOut ? audioOut.data : "",
    audio_mime: audioOut ? audioOut.mime : "",
    watermark: core.MARK
  }));
};
