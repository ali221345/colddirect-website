"use strict";

var core = require("../lib/cd-voice-core");

module.exports = async function handler(req, res) {
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
  var text = core.stripTags(data.text || data.spoken_text || "").slice(0, 1800);
  if (!text) {
    res.statusCode = 400;
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.end(JSON.stringify({ ok: false, error: "no_text", watermark: core.MARK }));
    return;
  }
  var locked = core.lockLang(text, data.language);
  var key = String(process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY || "").trim();
  if (!key) {
    res.statusCode = 200;
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.end(JSON.stringify({ ok: false, error: "missing_key", language: locked.bcp, watermark: core.MARK }));
    return;
  }
  var voice = locked.code === "fa" ? "Charon" : "Puck";
  var out = await core.geminiJson(key, "gemini-2.5-flash-preview-tts", {
    contents: [{ role: "user", parts: [{ text: "Read this exactly in a calm male Head Engineer voice. Do not add words:\n\n" + text }] }],
    generationConfig: {
      responseModalities: ["AUDIO"],
      speechConfig: {
        languageCode: locked.bcp,
        voiceConfig: { prebuiltVoiceConfig: { voiceName: voice } }
      }
    }
  });
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
