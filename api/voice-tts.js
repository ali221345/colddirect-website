"use strict";

var core = null;
var coreErr = "";
try {
  core = require("../lib/cd-voice-core");
} catch (e1) {
  coreErr = String((e1 && e1.message) || e1);
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
    res.statusCode = 200;
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.end(JSON.stringify({ ok: true, service: "voice-tts", watermark: core.MARK }));
    return;
  }
  if (req.method !== "POST") {
    res.statusCode = 405;
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.end(JSON.stringify({ ok: false, error: "POST only", watermark: core.MARK }));
    return;
  }
  var data = await core.readBody(req);
  var lockedHint = core.lockLang(data.text || data.spoken_text || "", data.language);
  var text = core.ttsScript(data.text || data.spoken_text || "", lockedHint.code).slice(0, 900);
  if (!text || /read this exactly|do not add words|never say the word slash/i.test(text)) {
    res.statusCode = 400;
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.end(JSON.stringify({ ok: false, error: "no_text", watermark: core.MARK }));
    return;
  }
  var locked = core.lockLang(text, lockedHint.bcp);
  text = core.ttsScript(text, locked.code);
  var key = String(process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY || "").trim();
  if (!key) {
    res.statusCode = 200;
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.end(JSON.stringify({ ok: false, error: "missing_key", language: locked.bcp, watermark: core.MARK }));
    return;
  }
  var voice = locked.code === "fa" ? "Charon" : "Puck";
  var out = await core.geminiJson(key, "gemini-2.5-flash-preview-tts", {
    systemInstruction: { parts: [{ text: "Male Head Engineer voice." }] },
    contents: [{ role: "user", parts: [{ text: text }] }],
    generationConfig: {
      responseModalities: ["AUDIO"],
      speechConfig: {
        languageCode: locked.bcp,
        voiceConfig: { prebuiltVoiceConfig: { voiceName: voice } }
      }
    }
  }, 12000);
  if (!out.ok) {
    out = await core.geminiJson(key, "gemini-3.8-flash-tts", {
      systemInstruction: { parts: [{ text: "Male Head Engineer voice." }] },
      contents: [{ role: "user", parts: [{ text: text }] }],
      generationConfig: {
        responseModalities: ["AUDIO"],
        speechConfig: {
          languageCode: locked.bcp,
          voiceConfig: { prebuiltVoiceConfig: { voiceName: voice } }
        }
      }
    }, 12000);
  }
  var audio = out.ok ? core.extractAudio(out.json) : null;
  res.statusCode = 200;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.end(JSON.stringify({
    ok: !!audio,
    language: locked.bcp,
    audio_base64: audio ? audio.data : "",
    audio_mime: audio ? audio.mime : "",
    watermark: core.MARK
  }));
};
