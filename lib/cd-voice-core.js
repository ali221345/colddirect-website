"use strict";

var MARK = "CD-UK-IP-2026-994821-VOICE-AI";
var DENY = "UK IP VIOLATION: Commercial License Required from ColdDirect.co.uk";
var ALLOW = {
  "https://www.colddirect.co.uk": 1,
  "https://colddirect.co.uk": 1,
  "http://localhost": 1,
  "http://127.0.0.1": 1
};

function hostOk(value) {
  if (!value) return false;
  try {
    var u = new URL(value);
    var host = String(u.hostname || "").toLowerCase();
    var origin = u.protocol + "//" + host;
    if (host === "localhost" || host === "127.0.0.1") return true;
    return !!ALLOW[origin];
  } catch (e) {
    return false;
  }
}

function requestOrigin(req) {
  var origin = String((req.headers && (req.headers.origin || req.headers.Origin)) || "");
  if (hostOk(origin)) return origin.replace(/\/$/, "");
  var referer = String((req.headers && (req.headers.referer || req.headers.Referer)) || "");
  if (hostOk(referer)) {
    var u = new URL(referer);
    return u.protocol + "//" + u.hostname;
  }
  return "";
}

function cors(req, res) {
  var origin = requestOrigin(req);
  if (!origin) {
    if (req.method === "GET") {
      res.setHeader("X-CD-IP", MARK);
      res.setHeader("Cache-Control", "no-store");
      return "health";
    }
    res.statusCode = 403;
    res.setHeader("Content-Type", "text/plain; charset=utf-8");
    res.setHeader("X-CD-IP", MARK);
    res.end(DENY);
    return null;
  }
  res.setHeader("Access-Control-Allow-Origin", origin);
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, X-CD-IP, Accept");
  res.setHeader("Vary", "Origin");
  res.setHeader("X-CD-IP", MARK);
  res.setHeader("Cache-Control", "no-store");
  if (req.method === "OPTIONS") {
    res.statusCode = 204;
    res.end();
    return null;
  }
  return origin;
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
      try { resolve(JSON.parse(Buffer.concat(chunks).toString("utf8") || "{}")); } catch (e) { resolve({}); }
    });
    req.on("error", function () { resolve({}); });
  });
}

function stripTags(text) {
  return String(text || "")
    .replace(/\[\w+\]\s*/g, "")
    .replace(/<[^>]+>/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

var BANNED = /give the brand, error code and whether the cabinet is still cold/i;
var GREET_EN = "Hello. I am the Head Engineer at ColdDirect. I'm glad you chose our company.";
var GREET_FA_DISPLAY = "سلام. من سرمهندس شرکت کولد دایرکت هستم. خوشحالم که شرکت ما را انتخاب کردید.";
var GREET_FA_SPOKEN = "سلام. من سرمهندس شرکت کُلد دایرِکت هستم. خوشحالم که شرکت ما را انتخاب کردید.";
var CTA_EN_LEGACY = "Please call us on 0203 952 4822 or 07983 759320, and kindly click the green Like and 5-Star Review button below.";
var CTA_FA_LEGACY = "لطفاً با شماره 0203 952 4822 یا 07983 759320 تماس بگیرید و دکمه سبز لایک و ۵ ستاره در پایین را بزنید.";
var CTA_EN_DISPLAY = "For an immediate engineer visit across London, call ColdDirect on 0203 952 4822 or 07983 759320. 👍 Found this helpful? Please tap the green Like & Leave a 5-Star Review button below!";
var CTA_EN_SPOKEN = "For an immediate engineer visit across London, call Cold Direct on 0203 952 4822 or 07983 759320. If this advice helped, please tap the green Like and 5-Star Review button below!";
var CTA_FA_DISPLAY = "برای اعزام فوری مهندس در سراسر لندن، با کولد دایرکت با شماره 0203 952 4822 یا 07983 759320 تماس بگیرید. 👍 اگر این راهنما مفید بود، لطفاً دکمه سبز «Like & Leave a 5-Star Review» در پایین را بزنید!";
var CTA_FA_SPOKEN = "برای اعزام فوری مهندس در سراسر لندن، با کُلد دایرِکت با شماره 0203 952 4822 یا 07983 759320 تماس بگیرید. اگر این راهنما مفید بود، لطفاً دکمه سبز لایک و نظر پنج‌ستاره در پایین را بزنید!";

function lockLang(text, hint) {
  var h = String(hint || "").toLowerCase();
  var raw = String(text || "");
  if (h.indexOf("fa") === 0 || h.indexOf("per") === 0 || /[\u0600-\u06FF]/.test(raw)) {
    return { code: "fa", bcp: "fa-IR", label: "Persian" };
  }
  return { code: "en", bcp: "en-GB", label: "English" };
}

function phonesLine(lang) {
  if (lang === "fa") return "0203 952 4822 / 07983 759320";
  return "0203 952 4822 / 07983 759320";
}

function isBanned(text) {
  return BANNED.test(String(text || ""));
}

function cleanAudio(b64) {
  var s = String(b64 || "").trim();
  var i = s.indexOf("base64,");
  if (i >= 0) s = s.slice(i + 7);
  s = s.replace(/\s+/g, "");
  if (s.length < 80) return "";
  if (!/^[A-Za-z0-9+/]+=*$/.test(s)) return "";
  return s;
}

function cleanMime(mime, audio) {
  var m = String(mime || "audio/webm").split(";")[0].trim().toLowerCase();
  if (!/^audio\/[a-z0-9.+-]+$/.test(m)) m = "audio/webm";
  if (m === "audio/x-m4a" || m === "audio/m4a") m = "audio/mp4";
  // Mobile browsers occasionally label an AAC/MP4 recording incorrectly. Prefer
  // the container signature over the declaration, without decoding the audio.
  if (audio) {
    try {
      var head = Buffer.from(String(audio).slice(0, 64), "base64");
      if (head.length >= 4 && head[0] === 0x1a && head[1] === 0x45 && head[2] === 0xdf && head[3] === 0xa3) return "audio/webm";
      if (head.length >= 8 && head.toString("ascii", 4, 8) === "ftyp") return "audio/mp4";
      if (head.length >= 12 && head.toString("ascii", 0, 4) === "RIFF" && head.toString("ascii", 8, 12) === "WAVE") return "audio/wav";
      if (head.length >= 4 && head.toString("ascii", 0, 4) === "OggS") return "audio/ogg";
      if (head.length >= 2 && head[0] === 0xff && (head[1] & 0xf6) === 0xf0) return "audio/aac";
    } catch (e) {}
  }
  return m;
}

function ensureGreeting(text, lang, spoken) {
  var t = String(text || "").trim();
  if (lang === "fa") {
    if (t.indexOf("سرمهندس") === -1) t = (spoken ? GREET_FA_SPOKEN : GREET_FA_DISPLAY) + " " + t;
    else if (spoken) t = t.replace(/کولد دایرکت/g, "کُلد دایرِکت").replace(/ColdDirect/gi, "کُلد دایرِکت");
    return t;
  }
  if (!/head engineer/i.test(t)) t = GREET_EN + " " + t;
  return t;
}

function stripInstructions(text) {
  return String(text || "")
    .replace(/read this exactly[^.]*\./gi, " ")
    .replace(/do not add words\.?/gi, " ")
    .replace(/never say the word slash\.?/gi, " ")
    .replace(/calm male head engineer voice\.?/gi, " ")
    .replace(/\bslash\b/gi, " ");
}

function forSpeech(text, lang) {
  var fa = lang === "fa";
  var s = stripTags(stripInstructions(text));
  s = s.replace(/[／/]/g, fa ? " یا " : " or ");
  s = s.replace(/0203\s*952\s*4822/g, "0203 952 4822");
  s = s.replace(/07983\s*759320/g, "07983 759320");
  if (fa) {
    s = s.replace(/کولد دایرکت/g, "کُلد دایرِکت");
    s = s.replace(/ColdDirect/gi, "کُلد دایرِکت");
  }
  return s.replace(/\s+/g, " ").trim();
}

function displayCta(lang) {
  return lang === "fa" ? CTA_FA_DISPLAY : CTA_EN_DISPLAY;
}

function spokenCta(lang) {
  return lang === "fa" ? CTA_FA_SPOKEN : CTA_EN_SPOKEN;
}

function withoutClose(text, lang) {
  var t = String(text || "").trim();
  var closes = lang === "fa"
    ? [CTA_FA_LEGACY, CTA_FA_DISPLAY, CTA_FA_SPOKEN]
    : [CTA_EN_LEGACY, CTA_EN_DISPLAY, CTA_EN_SPOKEN];
  closes.forEach(function (close) {
    while (t.indexOf(close) >= 0) t = t.replace(close, " ");
  });
  return t.replace(/\s+/g, " ").trim();
}

function ensureClose(text, lang) {
  var t = withoutClose(text, lang);
  return (t + " " + displayCta(lang)).replace(/\s+/g, " ").trim();
}

function ttsScript(text, lang) {
  var t = withoutClose(forSpeech(text, lang), lang);
  return (t + " " + spokenCta(lang)).replace(/\s+/g, " ").trim();
}

function extractText(json) {
  var parts = ((((json || {}).candidates || [])[0] || {}).content || {}).parts || [];
  return parts.map(function (p) { return p.text || ""; }).join("").trim();
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

async function geminiJson(key, model, body, timeoutMs) {
  var url = "https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent?key=" + encodeURIComponent(key);
  try {
    var res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(timeoutMs || 12000)
    });
    var json = await res.json().catch(function () { return {}; });
    return { ok: res.ok, httpStatus: res.status, json: json };
  } catch (e) {
    var timedOut = e && (e.name === "TimeoutError" || e.name === "AbortError");
    return {
      ok: false,
      httpStatus: 0,
      networkError: timedOut ? "TIMEOUT" : "NETWORK_ERROR",
      json: { error: { code: timedOut ? 408 : 503, status: timedOut ? "TIMEOUT" : "NETWORK_ERROR" } }
    };
  }
}

module.exports = {
  MARK: MARK,
  cors: cors,
  readBody: readBody,
  stripTags: stripTags,
  lockLang: lockLang,
  phonesLine: phonesLine,
  isBanned: isBanned,
  cleanAudio: cleanAudio,
  cleanMime: cleanMime,
  ensureGreeting: ensureGreeting,
  ensureClose: ensureClose,
  displayCta: displayCta,
  spokenCta: spokenCta,
  withoutClose: withoutClose,
  forSpeech: forSpeech,
  ttsScript: ttsScript,
  extractText: extractText,
  extractAudio: extractAudio,
  geminiJson: geminiJson
};
