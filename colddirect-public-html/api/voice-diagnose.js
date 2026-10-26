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
  "End display_text with 0203 952 4822 / 07983 759320.",
  "spoken_text must NEVER contain a slash character or the word slash. English ending: 0203 952 4822 or 07983 759320.",
  "Persian spoken ending uses number words: صفر دو صفر سه، نه پنج دو، چهار هشت دو دو یا صفر هفت نه هشت سه، هفت پنج نه، سه دو صفر.",
  "No slang. No stage directions. No bracket tags.",
  "JSON only: {\"language\":\"fa-IR or en-GB\",\"transcript\":\"exact spoken words\",\"display_text\":\"on-screen answer\",\"spoken_text\":\"TTS answer\"}"
].join(" ");

function hasPhone(text) {
  return /0203|07983|952\s*4822|759320|صفر دو صفر سه|صفر هفت نه هشت سه/.test(String(text || ""));
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
    display = core.ensureGreeting(display, locked.code, false);
    spoken = core.ensureGreeting(spoken, locked.code, true);
    if (!hasPhone(display)) display += " 0203 952 4822 / 07983 759320.";
    if (!hasPhone(spoken)) {
      spoken += locked.code === "fa"
        ? " صفر دو صفر سه، نه پنج دو، چهار هشت دو دو یا صفر هفت نه هشت سه، هفت پنج نه، سه دو صفر."
        : " 0203 952 4822 or 07983 759320.";
    }
    spoken = core.forSpeech(spoken, locked.code);
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
  var models = ["gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-flash-latest"];
  var lastErr = "";
  for (var i = 0; i < models.length; i++) {
    var out = null;
    for (var attempt = 0; attempt < 2; attempt++) {
      try {
        out = await core.geminiJson(key, models[i], {
          systemInstruction: { parts: [{ text: SYS }] },
          contents: [{ role: "user", parts: parts }],
          generationConfig: { temperature: 0.2, responseMimeType: "application/json" }
        });
      } catch (err) {
        out = { ok: false, json: { error: { code: 408 } } };
      }
      var code = out && out.json && out.json.error && out.json.error.code;
      if (out && out.ok) break;
      if (code !== 503 && code !== 429 && code !== 408) break;
    }
    if (!out || !out.ok) {
      lastErr = models[i];
      continue;
    }
    var parsed = parseOut(core.extractText(out.json), !!audio);
    if (parsed) return parsed;
    lastErr = models[i] + ":unparsed";
  }
  return { error: lastErr || "no_model" };
}

async function speak(key, spoken, locked) {
  var voice = locked.code === "fa" ? "Charon" : "Puck";
  var script = core.forSpeech(spoken, locked.code);
  var out = await core.geminiJson(key, "gemini-3.8-flash-tts", {
    contents: [{ role: "user", parts: [{ text: "Read this exactly in a calm male Head Engineer voice. Do not add words. Never say the word slash:\n\n" + script }] }],
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
    send(res, 200, { ok: true, service: "voice-diagnose", audio: "gemini-multimodal" });
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
  if (!result || result.error || !result.display) {
    send(res, 502, {
      ok: false,
      error: "The Head Engineer could not hear that. Tap SPEAK and try again.",
      transcript: "",
      display_text: "",
      spoken_text: "",
      audio_base64: ""
    });
    return;
  }
  var locked = core.lockLang(result.transcript + " " + result.display, result.language);
  result.spoken = core.forSpeech(result.spoken || result.display, locked.code);
  var audioOut = null;
  if (result.spoken) {
    try { audioOut = await speak(key, result.spoken, locked); } catch (e2) { audioOut = null; }
  }
  send(res, 200, {
    ok: true,
    language: locked.bcp,
    transcript: result.transcript || text,
    display_text: result.display,
    spoken_text: result.spoken,
    audio_base64: audioOut ? audioOut.data : "",
    audio_mime: audioOut ? audioOut.mime : ""
  });
};
