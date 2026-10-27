"use strict";

var core = null;
var coreErr = "";
try {
  core = require("../lib/cd-voice-core");
} catch (e1) {
  coreErr = String((e1 && e1.message) || e1);
}

var lamejsModule = null;

async function encodeMp3(audio) {
  if (!audio || audio.mime !== "audio/wav") return audio;
  if (!lamejsModule) lamejsModule = import("@breezystack/lamejs");
  var lamejs = await lamejsModule;
  var wav = Buffer.from(audio.data, "base64");
  if (wav.length < 44 || wav.toString("ascii", 0, 4) !== "RIFF") throw new Error("invalid_wav");
  var rate = 24000;
  var offset = 12;
  var pcm = null;
  while (offset + 8 <= wav.length) {
    var chunk = wav.toString("ascii", offset, offset + 4);
    var size = wav.readUInt32LE(offset + 4);
    var start = offset + 8;
    if (chunk === "fmt " && size >= 16) rate = wav.readUInt32LE(start + 4);
    if (chunk === "data") { pcm = wav.subarray(start, Math.min(start + size, wav.length)); break; }
    offset = start + size + (size % 2);
  }
  if (!pcm || pcm.length < 2) throw new Error("missing_pcm");
  var samples = new Int16Array(Math.floor(pcm.length / 2));
  for (var i = 0; i < samples.length; i++) samples[i] = pcm.readInt16LE(i * 2);
  var encoder = new lamejs.Mp3Encoder(1, rate, 48);
  var chunks = [];
  for (var at = 0; at < samples.length; at += 1152) {
    var encoded = encoder.encodeBuffer(samples.subarray(at, Math.min(at + 1152, samples.length)));
    if (encoded.length) chunks.push(Buffer.from(encoded));
  }
  var end = encoder.flush();
  if (end.length) chunks.push(Buffer.from(end));
  var mp3 = Buffer.concat(chunks);
  if (mp3.length < 100) throw new Error("mp3_encoding_failed");
  return { mime: "audio/mpeg", data: mp3.toString("base64") };
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
  var isChunk = data.chunk === true;
  var lockedHint = core.lockLang(data.text || data.spoken_text || "", data.language);
  var rawText = String(data.text || data.spoken_text || "");
  var text = (isChunk ? core.forSpeech(rawText, lockedHint.code) : core.ttsScript(rawText, lockedHint.code)).slice(0, isChunk ? 500 : 900);
  if (!text || /read this exactly|do not add words|never say the word slash/i.test(text)) {
    res.statusCode = 400;
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.end(JSON.stringify({ ok: false, error: "no_text", watermark: core.MARK }));
    return;
  }
  var locked = core.lockLang(text, lockedHint.bcp);
  text = isChunk ? core.forSpeech(text, locked.code) : core.ttsScript(text, locked.code);
  var key = String(process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY || "").trim();
  if (!key) {
    res.statusCode = 200;
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.end(JSON.stringify({ ok: false, error: "missing_key", language: locked.bcp, watermark: core.MARK }));
    return;
  }
  var voice = locked.code === "fa" ? "Charon" : "Puck";
  var speech = {
    contents: [{ role: "user", parts: [{ text: text }] }],
    generationConfig: {
      responseModalities: ["AUDIO"],
      speechConfig: { voiceConfig: { prebuiltVoiceConfig: { voiceName: voice } } }
    }
  };
  var models = ["gemini-3.8-flash-lite-tts", "gemini-3.8-flash-tts"];
  var out = null;
  var audio = null;
  var model = models[0];
  for (var i = 0; i < models.length; i++) {
    model = models[i];
    out = await core.geminiJson(key, model, speech, i === 0 ? 12000 : 14000);
    audio = out.ok ? core.extractAudio(out.json) : null;
    if (audio) break;
    var http = Number(out.httpStatus) || Number(out.json && out.json.error && out.json.error.code) || 0;
    if (http && http !== 408 && http !== 429 && http < 500) break;
  }
  var encodeError = "";
  if (audio) {
    try { audio = await encodeMp3(audio); } catch (encodeErr) { audio = null; encodeError = "MP3_ENCODING_FAILED: " + String((encodeErr && encodeErr.message) || "encoder error").replace(/[^a-z0-9 _@./:-]/gi, "").slice(0, 90); }
  }
  var diagnostic = null;
  if (!audio) {
    var upstream = (out && out.json && out.json.error) || {};
    diagnostic = {
      stage: "tts",
      model: model,
      upstreamHttp: Number(out && out.httpStatus) || Number(upstream.code) || 0,
      upstreamStatus: String(encodeError || upstream.status || (out && out.networkError) || "NO_AUDIO").slice(0, 140)
    };
    try { console.warn("voice-tts " + JSON.stringify(diagnostic)); } catch (logErr) {}
  }
  res.statusCode = 200;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.end(JSON.stringify({
    ok: !!audio,
    language: locked.bcp,
    audio_base64: audio ? audio.data : "",
    audio_mime: audio ? audio.mime : "",
    diagnostic: diagnostic,
    watermark: core.MARK
  }));
};
