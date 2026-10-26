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

function lockLang(text, hint) {
  var raw = String(text || "") + " " + String(hint || "");
  if (/[\u0600-\u06FF]/.test(raw)) return { code: "fa", bcp: "fa-IR", label: "Persian" };
  return { code: "en", bcp: "en-GB", label: "English" };
}

function phonesLine(lang) {
  if (lang === "fa") return "0203 952 4822 / 07983 759320";
  return "0203 952 4822 / 07983 759320";
}

function fallbackAnswer(text) {
  var q = String(text || "").toLowerCase();
  var fa = /[\u0600-\u06FF]/.test(text);
  var kind = "generic";
  if (/سرد نم|خنک نم|not cool|warm|not cold|high temp/.test(q) || /سرد نمی‌کند|خنک نمی‌کند/.test(text)) kind = "warm";
  else if (/یخ|ice|frost|defrost/.test(q)) kind = "ice";
  else if (/کمپرسور|compressor|trip|overload/.test(q)) kind = "comp";
  else if (/یخساز|ice machine|no ice/.test(q)) kind = "ice_m";
  var pack = {
    warm: {
      fa: "اگر یخچال تجاری خنک نمی‌کند، اول کندانسور را از روغن و پرز تمیز کنید و واشر در را چک کنید. جریان هوای اواپراتور را باز بگذارید؛ اگر بعد از تمیزکاری دما بالای ۸ درجه ماند، فن یا گاز نیاز به بازدید دارد.",
      en: "If a commercial fridge is not cooling, clean the condenser and check the door gasket first. Keep evaporator airflow clear; if the cabinet stays above 8°C after cleaning, the fan or refrigerant charge needs a site visit."
    },
    ice: {
      fa: "یخ‌زدگی معمولاً از نفوذ هوای گرم یا توقف سیکل دیفراست است. کویل را نتراشید؛ در را ببندید، زهکش را باز کنید و اگر دیفراست کار نمی‌کند تکنسین بفرستید.",
      en: "Heavy ice usually means warm air ingress or a failed defrost cycle. Do not chip the coil; check the door closer and drain, then book an engineer if defrost is dead."
    },
    comp: {
      fa: "تریپ کمپرسور اغلب از کندانسور کثیف، ولتاژ ضعیف یا اضافه بار است. دستگاه را ریست بی‌مورد نکنید؛ کندانسور را تمیز کنید و اگر دوباره قطع شد اعزام لازم است.",
      en: "A tripping compressor is usually a dirty condenser, weak voltage or overload. Do not keep resetting it; clean the condenser and call out if it cuts again."
    },
    ice_m: {
      fa: "نبود یخ معمولاً آب، رسوب یا کندانسور کثیف است نه مرگ دستگاه. شیر آب، فیلتر ورودی و سوییچ سطل را چک کنید.",
      en: "No ice is usually water, scale or a dirty condenser, not a dead machine. Check the stopcock, inlet filter and bin switch."
    },
    generic: {
      fa: "برند، کد خطا و اینکه کابین هنوز سرد است را بگویید تا تشخیص دقیق شود. تا رسیدن تکنسین در را بسته نگه دارید و کندانسور را تمیز کنید.",
      en: "Give the brand, error code and whether the cabinet is still cold. Keep the door shut and clean the condenser until an engineer arrives."
    }
  };
  return pack[kind][fa ? "fa" : "en"] + " " + phonesLine(fa ? "fa" : "en") + ".";
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

module.exports = {
  MARK: MARK,
  cors: cors,
  readBody: readBody,
  stripTags: stripTags,
  lockLang: lockLang,
  phonesLine: phonesLine,
  fallbackAnswer: fallbackAnswer,
  extractText: extractText,
  extractAudio: extractAudio,
  geminiJson: geminiJson
};
