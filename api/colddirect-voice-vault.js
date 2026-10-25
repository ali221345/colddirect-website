/**
 * ColdDirect Voice Vault — Node / serverless twin of the PHP vault.
 * On Plesk IIS this file is blocked from static download; use the PHP endpoint.
 * Watermark: CD-UK-IP-2026-994821-VOICE-AI
 * Owner: ColdDirect Ltd, 27 Felixstowe Road, Enfield, London N9 0DX
 */
"use strict";

var MARK = "CD-UK-IP-2026-994821-VOICE-AI";
var DENY = "UK IP VIOLATION: Commercial License Required from ColdDirect.co.uk";

var SYSTEM_PROMPT = [
  "You are the Head Engineer at ColdDirect Ltd (colddirect.co.uk), 27 Felixstowe Road, Enfield, London N9 0DX.",
  "You have 30 years of hands-on commercial refrigeration and catering-equipment experience across London.",
  "CRITICAL LANGUAGE LOCK — ZERO MIXING:",
  "1. Detect the exact language the customer spoke or typed.",
  "2. If English: reply 100% in warm conversational British English. Never mix Farsi or any other language.",
  "3. If Persian / Farsi: reply 100% in warm everyday colloquial Tehran spoken Persian. No bookish words such as می‌باشد.",
  "4. If any other language: reply 100% in that exact language only.",
  "Persian replies must open exactly: درود، من سرپرست مهندسین در شرکت کولد دایرکت هستم و خوشحالم که ما را انتخاب کردید.",
  "Persian replies must close by asking them to click the green Like and 5-Star Review button below.",
  "TTS pronounces کولد دایرکت as کُلد دایرِکت. Never read a phone number as one giant numeral.",
  "Write the company name as کولد دایرکت. Phone numbers must be written as 07983 759320, 0203 952 4822 or 0800 112 3427 — never as one giant numeral.",
  "Commercial refrigeration and catering only. Return STRICT JSON:",
  '{"language":"en","languageLabel":"English","spoken":"...","summary":"...","cause":"...","checks":["..."]}'
].join(" ");

function hostOk(value) {
  if (!value) return false;
  try {
    var u = new URL(value);
    var host = String(u.hostname || "").toLowerCase();
    var scheme = String(u.protocol || "").replace(":", "").toLowerCase();
    if (host === "localhost" || host === "127.0.0.1") return true;
    if (scheme !== "https") return false;
    return host === "colddirect.co.uk" || host === "www.colddirect.co.uk";
  } catch (e) {
    return false;
  }
}

function requestOrigin(req) {
  var origin = String((req.headers && (req.headers.origin || req.headers.Origin)) || "");
  if (hostOk(origin)) return origin;
  var referer = String((req.headers && (req.headers.referer || req.headers.Referer)) || "");
  if (hostOk(referer)) {
    var u = new URL(referer);
    return u.protocol + "//" + u.hostname;
  }
  return "";
}

function readBody(req) {
  if (req.body && typeof req.body === "object" && !Buffer.isBuffer(req.body)) {
    return Promise.resolve(req.body);
  }
  if (typeof req.body === "string") {
    try { return Promise.resolve(JSON.parse(req.body || "{}")); } catch (e) { return Promise.resolve({}); }
  }
  return new Promise(function (resolve) {
    var chunks = [];
    req.on("data", function (c) { chunks.push(c); });
    req.on("end", function () {
      var raw = Buffer.concat(chunks).toString("utf8");
      try { resolve(JSON.parse(raw || "{}")); } catch (e) { resolve({}); }
    });
    req.on("error", function () { resolve({}); });
  });
}

function detectLang(text) {
  if (/[پچژگ]/.test(text) || /[آ-ی]/.test(text)) return ["fa", "Persian"];
  if (/[\u0600-\u06FF]/.test(text)) return ["ar", "Arabic"];
  if (/[ğüşöçıİĞÜŞÖÇ]/.test(text)) return ["tr", "Turkish"];
  if (/[\u0900-\u097F]/.test(text)) return ["hi", "Hindi"];
  return ["en", "English"];
}

function fallbackPack(text) {
  var lang = detectLang(text);
  var q = String(text || "").toLowerCase();
  var kind = "generic";
  if (/e\s*1|e1/.test(q) || (q.indexOf("foster") >= 0 && q.indexOf("fridge") >= 0)) kind = "e1";
  else if (/ice machine|not making ice/.test(q)) kind = "ice";
  else if (/cold room|ice-?up/.test(q)) kind = "room";
  var en = {
    e1: {
      spoken: "You mentioned a Foster fridge showing E one — that is E for Echo, one as in the number one. That is usually a high-temperature or probe alarm. Clean the condenser, check the door gasket, and keep stock off the return air. Please tap Helpful or leave a five-star review so ColdDirect can grow. Call oh seven nine eight three, seven five nine, three two oh.",
      summary: "Foster E1 is typically a high-temperature or cabinet-probe alarm.",
      cause: "Dirty condenser, open door or weak gasket, blocked airflow, or a failed probe.",
      checks: ["Brush the condenser fins clean.", "Confirm the door seals and fans spin.", "If air is above 8°C call 07983 759320."]
    },
    ice: {
      spoken: "No ice usually means water, scale or heat rejection — not a dead machine. Check the tap, inlet filter, bin switch and condenser. Please tap Like or leave a five-star review. Call oh seven nine eight three, seven five nine, three two oh.",
      summary: "No ice usually means water supply, scale, a dirty condenser or a harvest/bin switch fault.",
      cause: "Closed stopcock, blocked filter, limescale, dirty condenser or a full-bin switch.",
      checks: ["Confirm water reaches the machine.", "Look for a thin uneven ice sheet — that is scale.", "Clean the condenser or call 07983 759320."]
    },
    room: {
      spoken: "Ice-up means the room cannot breathe — warm air in, or defrost has stopped. Do not chip the coil. Please tap Helpful or leave a five-star review. Call oh seven nine eight three, seven five nine, three two oh.",
      summary: "Cold-room ice-up is usually door air ingress or a failed defrost cycle.",
      cause: "Open door, tired gasket, failed defrost heater or a blocked drain.",
      checks: ["Check door closer, curtains and gasket.", "See if the drain is clear.", "Protect stock and call 07983 759320."]
    },
    generic: {
      spoken: "Tell me the make, the error code and whether the cabinet is still cold. Please tap the Like button or leave a five-star review. Call oh seven nine eight three, seven five nine, three two oh.",
      summary: "Share the make, error code and whether the cabinet is still holding temperature.",
      cause: "Needs the symptom, brand and error code to narrow the fault.",
      checks: ["Note the brand, model and controller code.", "Feel the condenser and check the gasket.", "Call 07983 759320 if stock is warming."]
    }
  };
  var row = en[kind] || en.generic;
  return {
    ok: true,
    language: lang[0],
    languageLabel: lang[1],
    spoken: row.spoken,
    summary: row.summary,
    cause: row.cause,
    checks: row.checks,
    watermark: MARK,
    source: "vault-fallback"
  };
}

function pcmToWav(pcm, rate) {
  rate = rate || 24000;
  var header = Buffer.alloc(44);
  header.write("RIFF", 0);
  header.writeUInt32LE(36 + pcm.length, 4);
  header.write("WAVE", 8);
  header.write("fmt ", 12);
  header.writeUInt32LE(16, 16);
  header.writeUInt16LE(1, 20);
  header.writeUInt16LE(1, 22);
  header.writeUInt32LE(rate, 24);
  header.writeUInt32LE(rate * 2, 28);
  header.writeUInt16LE(2, 32);
  header.writeUInt16LE(16, 34);
  header.write("data", 36);
  header.writeUInt32LE(pcm.length, 40);
  return Buffer.concat([header, pcm]);
}

function extractText(json) {
  var parts = ((((json || {}).candidates || [])[0] || {}).content || {}).parts || [];
  return parts.map(function (p) { return p.text || ""; }).join("").trim();
}

function extractAudio(json) {
  var parts = ((((json || {}).candidates || [])[0] || {}).content || {}).parts || [];
  for (var i = 0; i < parts.length; i++) {
    var inline = parts[i].inlineData || parts[i].inline_data;
    if (inline && inline.data) {
      var mime = inline.mimeType || inline.mime_type || "audio/pcm";
      var bin = Buffer.from(inline.data, "base64");
      if (!/wav/i.test(mime)) {
        bin = pcmToWav(bin, 24000);
        mime = "audio/wav";
      }
      return { mime: mime, data: bin.toString("base64") };
    }
  }
  return null;
}

function parseModelJson(text) {
  var m = String(text || "").match(/\{[\s\S]*\}/);
  if (!m) return null;
  try {
    var json = JSON.parse(m[0]);
    if (!json.spoken && !json.summary) return null;
    return {
      ok: true,
      language: json.language || "en",
      languageLabel: json.languageLabel || "Detected",
      spoken: json.spoken || json.summary || "",
      summary: json.summary || json.spoken || "",
      cause: json.cause || "",
      checks: Array.isArray(json.checks) ? json.checks.map(String) : [],
      watermark: MARK,
      source: "gemini"
    };
  } catch (e) {
    return null;
  }
}

async function geminiJson(key, model, body) {
  var url = "https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent?key=" + encodeURIComponent(key);
  var res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  var json = await res.json().catch(function () { return {}; });
  return { ok: res.ok, json: json };
}

async function diagnose(key, text, audio, mime) {
  var parts = [{ text: text || "Please transcribe the attached kitchen-fault audio and diagnose it." }];
  if (audio) parts.push({ inline_data: { mime_type: mime || "audio/webm", data: audio } });
  var models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.5-flash-lite"];
  for (var i = 0; i < models.length; i++) {
    var out = await geminiJson(key, models[i], {
      systemInstruction: { parts: [{ text: SYSTEM_PROMPT }] },
      contents: [{ role: "user", parts: parts }],
      generationConfig: { temperature: 0.35, responseMimeType: "application/json" }
    });
    if (out.ok) {
      var parsed = parseModelJson(extractText(out.json));
      if (parsed) return parsed;
    }
  }
  return null;
}

function persianTtsText(text) {
  var s = String(text || "").replace(/[\u06F0-\u06F9]/g, function (c) {
    return String(c.charCodeAt(0) - 0x06F0);
  }).replace(/[\u0660-\u0669]/g, function (c) {
    return String(c.charCodeAt(0) - 0x0660);
  });
  var digitsFa = ["صفر", "یک", "دو", "سه", "چهار", "پنج", "شش", "هفت", "هشت", "نه"];
  s = s.replace(/کولد\s*\u200C?\s*دایرکت|کلد\s*\u200C?\s*دایرکت|کل\s*\u200C?\s*دایرکت|ColdDirect|Cold\s*Direct/gi, "کُلد دایرِکت");
  s = s.replace(/(?:\+44\s*\(?0?\)?|0)\s*7983[\s\-]*759[\s\-]*320/g, " صفر هفت نه هشت سه، هفت پنج نه، سه دو صفر ");
  s = s.replace(/(?:\+44\s*\(?0?\)?|0)\s*203[\s\-]*952[\s\-]*4822/g, " صفر دو صفر سه، نه پنج دو، چهار هشت دو دو ");
  s = s.replace(/(?:\+44\s*\(?0?\)?|0)\s*800[\s\-]*112[\s\-]*3427/g, " صفر هشتصد، یک یک دو، سه چهار دو هفت ");
  s = s.replace(/(?<!\d)(\+?\d[\d\s\-]{6,}\d)(?!\d)/g, function (m) {
    var digits = m.replace(/\+44/g, "0").replace(/\D/g, "");
    var groups = [];
    var i, j, chunk, parts;
    if (digits.length < 7) return m;
    for (i = 0; i < digits.length; i += 4) {
      chunk = digits.slice(i, i + 4);
      parts = [];
      for (j = 0; j < chunk.length; j++) parts.push(digitsFa[chunk.charCodeAt(j) - 48]);
      groups.push(parts.join(" "));
    }
    return " " + groups.join("، ") + " ";
  });
  return s.replace(/\s+/g, " ").replace(/^\s+|\s+$/g, "");
}

async function tts(key, spoken) {
  if (/[\u0600-\u06FF]/.test(spoken)) spoken = persianTtsText(spoken);
  var out = await geminiJson(key, "gemini-2.5-flash-preview-tts", {
    contents: [{ role: "user", parts: [{ text: "Speak as a warm, calm, experienced male Head Engineer. Conversational pace. Read this exactly:\n\n" + spoken }] }],
    generationConfig: {
      responseModalities: ["AUDIO"],
      speechConfig: { voiceConfig: { prebuiltVoiceConfig: { voiceName: "Puck" } } }
    }
  });
  if (!out.ok) return null;
  return extractAudio(out.json);
}

async function handler(req, res) {
  var origin = requestOrigin(req);
  if (!origin) {
    res.statusCode = 403;
    res.setHeader("Content-Type", "text/plain; charset=utf-8");
    res.setHeader("X-CD-IP", MARK);
    res.end(DENY);
    return;
  }
  res.setHeader("Access-Control-Allow-Origin", origin);
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, X-CD-IP, Accept");
  res.setHeader("X-CD-IP", MARK);
  res.setHeader("Cache-Control", "no-store");
  if (req.method === "OPTIONS") {
    res.statusCode = 204;
    res.end();
    return;
  }
  if (req.method !== "POST") {
    res.statusCode = 405;
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.end(JSON.stringify({ ok: false, error: "POST only", watermark: MARK }));
    return;
  }
  var data = await readBody(req);
  var text = String(data.text || "").replace(/<[^>]+>/g, "").trim().slice(0, 2000);
  var audio = String(data.audio || "").replace(/\s+/g, "");
  var mime = String(data.mime || "audio/webm").slice(0, 80);
  if (!text && !audio) {
    res.statusCode = 400;
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.end(JSON.stringify({ ok: false, error: "Type a fault or speak, then try again.", watermark: MARK }));
    return;
  }
  var key = String(process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY || "").trim();
  var result = null;
  if (key) {
    try { result = await diagnose(key, text, audio || null, mime); } catch (e) { result = null; }
  }
  if (!result) result = fallbackPack(text || "general commercial refrigeration fault");
  if (key && result.spoken) {
    try {
      var audioOut = await tts(key, result.spoken);
      if (audioOut) {
        result.audio = audioOut;
        result.voice = "Puck";
      }
    } catch (e2) { /* fallback speech is client-side */ }
  }
  res.statusCode = 200;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.end(JSON.stringify(result));
}

module.exports = handler;
module.exports.default = handler;
module.exports.hostOk = hostOk;
module.exports.fallbackPack = fallbackPack;
module.exports.detectLang = detectLang;
