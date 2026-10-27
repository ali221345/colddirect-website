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
  if (!lamejsModule) lamejsModule = import("../lib/cd-lamejs.mjs");
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

function conciseSummary(raw, lang) {
  var text = core.forSpeech(raw, lang)
    .replace(/Hello\. I am the Head Engineer at ColdDirect\. I'm glad you chose our company\./gi, " ")
    .replace(/سلام\.\s*من سرمهندس شرکت .*?خوشحالم که شرکت ما را انتخاب کردید\./g, " ")
    .replace(/Please call us on 0203 952 4822 or 07983 759320, and kindly click the green Like and 5-Star Review button below\./gi, " ")
    .replace(/لطفاً با شماره 0203 952 4822 یا 07983 759320 تماس بگیرید و دکمه سبز لایک و ۵ ستاره در پایین را بزنید\./g, " ")
    .replace(/\s+/g, " ").trim();
  var sentences = text.match(/[^.!?؟]+[.!?؟]+|[^.!?؟]+$/g) || [text];
  var selected = [];
  var words = 0;
  for (var i = 0; i < sentences.length && selected.length < 3; i++) {
    var sentence = sentences[i].trim();
    if (!sentence) continue;
    var count = sentence.split(/\s+/).filter(Boolean).length;
    if (selected.length && words + count > 45) break;
    if (count > 45) {
      sentence = sentence.split(/\s+/).slice(0, 45).join(" ");
      count = 45;
    }
    selected.push(sentence);
    words += count;
    if (words >= 45) break;
  }
  return selected.join(" ").trim();
}

function failure(provider, http, status) {
  return { audio: null, provider: provider, http: Number(http) || 0, status: String(status || "NO_AUDIO").slice(0, 140) };
}

async function geminiAudio(key, text, lang, timeoutMs) {
  var voice = lang === "fa" ? "Charon" : "Puck";
  var body = {
    contents: [{ role: "user", parts: [{ text: text }] }],
    generationConfig: {
      responseModalities: ["AUDIO"],
      speechConfig: { voiceConfig: { prebuiltVoiceConfig: { voiceName: voice } } }
    }
  };
  var model = "gemini-3.8-flash-tts";
  var out = await core.geminiJson(key, model, body, timeoutMs);
  var audio = out.ok ? core.extractAudio(out.json) : null;
  if (audio) {
    try {
      audio = await encodeMp3(audio);
      return { audio: audio, provider: "gemini", http: 200, status: "OK" };
    } catch (error) {
      return failure("gemini", 500, "MP3_ENCODING_FAILED");
    }
  }
  var upstream = (out && out.json && out.json.error) || {};
  return failure("gemini", Number(out && out.httpStatus) || Number(upstream.code), upstream.status || (out && out.networkError) || "NO_AUDIO");
}

async function binaryAudio(provider, url, options, timeoutMs) {
  try {
    options.signal = AbortSignal.timeout(timeoutMs);
    var res = await fetch(url, options);
    if (!res.ok) {
      await res.arrayBuffer().catch(function () {});
      return failure(provider, res.status, res.status === 429 ? "RESOURCE_EXHAUSTED" : "UPSTREAM_ERROR");
    }
    var bytes = Buffer.from(await res.arrayBuffer());
    if (bytes.length < 100) return failure(provider, res.status, "EMPTY_AUDIO");
    return { audio: { mime: "audio/mpeg", data: bytes.toString("base64") }, provider: provider, http: res.status, status: "OK" };
  } catch (error) {
    var timedOut = error && (error.name === "TimeoutError" || error.name === "AbortError");
    return failure(provider, timedOut ? 408 : 503, timedOut ? "TIMEOUT" : "NETWORK_ERROR");
  }
}

function openaiAudio(key, text, lang, timeoutMs) {
  return binaryAudio("openai", "https://api.openai.com/v1/audio/speech", {
    method: "POST",
    headers: { "Authorization": "Bearer " + key, "Content-Type": "application/json" },
    body: JSON.stringify({ model: "gpt-4o-mini-tts", voice: "onyx", input: text, response_format: "mp3" })
  }, timeoutMs);
}

function azureAudio(key, text, lang, timeoutMs) {
  var region = String(process.env.AZURE_SPEECH_REGION || "uksouth").trim();
  var voice = String(process.env.AZURE_SPEECH_VOICE || (lang === "fa" ? "fa-IR-FaridNeural" : "en-GB-RyanNeural")).trim();
  var locale = lang === "fa" ? "fa-IR" : "en-GB";
  var escaped = text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&apos;");
  var ssml = "<speak version='1.0' xml:lang='" + locale + "'><voice xml:lang='" + locale + "' name='" + voice + "'>" + escaped + "</voice></speak>";
  return binaryAudio("azure", "https://" + region + ".tts.speech.microsoft.com/cognitiveservices/v1", {
    method: "POST",
    headers: { "Ocp-Apim-Subscription-Key": key, "Content-Type": "application/ssml+xml", "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3" },
    body: ssml
  }, timeoutMs);
}

function elevenlabsAudio(key, text, lang, timeoutMs) {
  var voiceId = String(process.env.ELEVENLABS_VOICE_ID || "ErXwobaYiN019PkySvjV").trim();
  return binaryAudio("elevenlabs", "https://api.elevenlabs.io/v1/text-to-speech/" + encodeURIComponent(voiceId) + "?output_format=mp3_44100_32", {
    method: "POST",
    headers: { "xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg" },
    body: JSON.stringify({ text: text, model_id: "eleven_multilingual_v2" })
  }, timeoutMs);
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
  var text = conciseSummary(String(data.text || data.spoken_text || ""), lockedHint.code);
  if (!text || /read this exactly|do not add words|never say the word slash/i.test(text)) {
    res.statusCode = 400;
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.end(JSON.stringify({ ok: false, error: "no_text", watermark: core.MARK }));
    return;
  }
  var locked = core.lockLang(text, lockedHint.bcp);
  text = conciseSummary(text, locked.code);

  var primary = String(process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY || "").trim();
  var secondary = String(process.env.GEMINI_API_KEY_SECONDARY || process.env.SECONDARY_GEMINI_API_KEY || process.env.GEMINI_API_KEY_2 || process.env.GOOGLE_API_KEY_2 || "").trim();
  var azure = String(process.env.AZURE_SPEECH_KEY || "").trim();
  var elevenlabs = String(process.env.ELEVENLABS_API_KEY || process.env.XI_API_KEY || "").trim();
  var openai = String(process.env.OPENAI_API_KEY || "").trim();
  var providers = [];
  if (primary) providers.push(function (timeout) { return geminiAudio(primary, text, locked.code, timeout); });
  if (secondary && secondary !== primary) providers.push(function (timeout) { return geminiAudio(secondary, text, locked.code, timeout); });
  if (azure) providers.push(function (timeout) { return azureAudio(azure, text, locked.code, timeout); });
  if (elevenlabs) providers.push(function (timeout) { return elevenlabsAudio(elevenlabs, text, locked.code, timeout); });
  if (openai) providers.push(function (timeout) { return openaiAudio(openai, text, locked.code, timeout); });

  var audio = null;
  var attempts = [];
  var last = null;
  var started = Date.now();
  for (var i = 0; i < providers.length; i++) {
    var remaining = 22000 - (Date.now() - started);
    if (remaining < 1500) break;
    last = await providers[i](Math.min(9000, remaining));
    attempts.push({ provider: last.provider, upstreamHttp: last.http, upstreamStatus: last.status });
    if (last.audio) { audio = last.audio; break; }
    if (last.http && last.http !== 408 && last.http !== 429 && last.http < 500) break;
  }

  if (!audio && !last) last = failure("configuration", 0, "API_KEY_MISSING");
  var diagnostic = null;
  if (!audio) {
    diagnostic = {
      stage: "tts",
      model: last.provider,
      upstreamHttp: last.http,
      upstreamStatus: last.status,
      attempts: attempts
    };
    try { console.warn("voice-tts " + JSON.stringify(diagnostic)); } catch (logErr) {}
  }
  res.statusCode = 200;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.end(JSON.stringify({
    ok: !!audio,
    error: audio ? "" : "TTS_UNAVAILABLE",
    language: locked.bcp,
    summary_words: text.split(/\s+/).filter(Boolean).length,
    provider: audio ? last.provider : "",
    audio_base64: audio ? audio.data : "",
    audio_mime: audio ? audio.mime : "",
    diagnostic: diagnostic,
    watermark: core.MARK
  }));
};
