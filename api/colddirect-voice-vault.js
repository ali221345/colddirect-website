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
  "You are a commercial refrigeration diagnostic engine for Cold Direct Ltd, London. Kind, polite, no slang.",
  "NEVER introduce yourself. NEVER write a greeting. NEVER include phone numbers, Like, review, or closing text.",
  "Output ONLY 2 short sentences diagnosing the fault in the user's language. If they ask to translate, output in that requested language. If audio is Persian, write Persian.",
  "Return STRICT JSON only: {\"target_language_code\":\"BCP-47 e.g. fa-IR\",\"transcript\":\"exact customer words in native script\",\"technical_answer\":\"exactly two short diagnostic sentences, no greeting, no phones, no like/review\"}"
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
    var display = json.technical_answer || json.display_text || json.spoken || json.summary || "";
    var spokenTts = json.spoken_text || json.tts_text || "";
    if (!display && !spokenTts) return null;
    if (!display) display = spokenTts;
    var code = String(json.target_language_code || json.language || "en").toLowerCase();
    if (code.indexOf("fil") === 0 || code.indexOf("tl") === 0) code = "tl";
    else if (code.length > 2) code = code.slice(0, 2);
    if (!spokenTts) spokenTts = display;
    if (!/759320|952\s*4822|0203|07983/.test(display) || !/like|review|لایک|ستاره|beğeni|bituin|estrellas|نجمة/i.test(display)) {
      display += " 0203 952 4822 / 07983 759320. Like & 5-Star Review.";
    }
    return {
      ok: true,
      language: code,
      languageLabel: json.languageLabel || "Detected",
      spoken: display,
      display_text: display,
      tts_text: spokenTts,
      spoken_text: spokenTts,
      summary: json.summary || display,
      cause: json.cause || json.likely_cause || "",
      checks: Array.isArray(json.checks) ? json.checks.map(String) : (Array.isArray(json.quick_checks) ? json.quick_checks.map(String) : []),
      watermark: MARK,
      source: "llm"
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
  var s = String(text || "");
  s = s.replace(/^دُرود بر شُما[\s\S]*?اِنتِخاب کَردید\.?\s*/u, "");
  s = s.replace(/^درود بر شما[\s\S]*?انتخاب کردید\.?\s*/u, "");
  s = s.replace(/من مهندس ارشد[^.!?؟]*[.!?؟]\s*/gu, "");
  s = s.replace(/^درود[^.!?؟]*[.!?؟]?\s*/u, "");
  s = s.replace(/^سلام[^.!?؟]*[.!?؟]?\s*/u, "");
  s = s.replace(/\s*برای اعزام فوری[\s\S]*$/u, "");
  s = s.replace(/\s*چِنانچه مُشکِل[\s\S]*$/u, "");
  s = s.replace(/(?:\+44\s*\(?0?\)?|0)\s*7983[\s\-]*759[\s\-]*320/g, " ");
  s = s.replace(/(?:\+44\s*\(?0?\)?|0)\s*203[\s\-]*952[\s\-]*4822/g, " ");
  s = s.replace(/سردخانه/g, "سَردخانه");
  s = s.replace(/یخچال/g, "یَخچالِ");
  s = s.replace(/کمپرسور/g, "کُمپرِسور");
  s = s.replace(/ترموستات/g, "تِرموستات");
  s = s.replace(/کندانسور/g, "کُندانسور");
  s = s.replace(/اواپراتور/g, "اِواپُراتور");
  s = s.replace(/کولد\s*دایرکت|ColdDirect|Cold Direct/gi, "کُلد دایرِکت");
  s = s.replace(/\s+/g, " ").replace(/^\s+|\s+$/g, "");
  return "درود بر شما. من مهندس ارشد شرکت کُلد دایرِکت هستم و خوشحالم که ما را انتخاب کردید. "
    + s + " "
    + "برای اعزام فوری تکنسین در لندن، با شماره تلفن صفر دویست و سه، نهصد و پنجاه و دو، چهل و هشت، بیست و دو، و یا موبایل صفر هفتصد و نود و هشت، سی و هفت، پنجاه و نه، سیصد و بیست تماس بگیرید. اگر این راهنمایی برای شما مفید بود، ممنون می‌شویم دکمه سبز لایک و ثبت نظر پنج ستاره را در پایین همین کادر بزنید.";
}

async function tts(key, spoken) {
  if (/[\u0600-\u06FF]/.test(spoken)) return null;
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
