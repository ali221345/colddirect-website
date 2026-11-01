"use strict";

var MARK = "CD-UK-IP-2026-994821-VOICE-AI";
var DENY = "UK IP VIOLATION: Commercial License Required from ColdDirect.co.uk";
var ALLOW = {
  "https://www.colddirect.co.uk": 1,
  "https://colddirect.co.uk": 1,
  "http://localhost": 1,
  "http://127.0.0.1": 1,
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
  var origin = String(
    (req.headers && (req.headers.origin || req.headers.Origin)) || "",
  );
  if (hostOk(origin)) return origin.replace(/\/$/, "");
  var referer = String(
    (req.headers && (req.headers.referer || req.headers.Referer)) || "",
  );
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
  res.setHeader(
    "Access-Control-Allow-Headers",
    "Content-Type, X-CD-IP, Accept",
  );
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
    try {
      return Promise.resolve(JSON.parse(req.body || "{}"));
    } catch (e) {
      return Promise.resolve({});
    }
  }
  return new Promise(function (resolve) {
    var chunks = [];
    req.on("data", function (c) {
      chunks.push(c);
    });
    req.on("end", function () {
      try {
        resolve(JSON.parse(Buffer.concat(chunks).toString("utf8") || "{}"));
      } catch (e) {
        resolve({});
      }
    });
    req.on("error", function () {
      resolve({});
    });
  });
}

function stripTags(text) {
  return String(text || "")
    .replace(/\[\w+\]\s*/g, "")
    .replace(/<[^>]+>/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

var BANNED =
  /give the brand, error code and whether the cabinet is still cold/i;
var CTA_EN_LEGACY =
  "Please call us on 0203 952 4822 or 07983 759320, and kindly click the green Like and 5-Star Review button below.";
var CTA_FA_LEGACY =
  "لطفاً با شماره 0203 952 4822 یا 07983 759320 تماس بگیرید و دکمه سبز لایک و ۵ ستاره در پایین را بزنید.";
var LANGS = {
  en: {
    bcp: "en-GB",
    label: "English",
    greeting:
      "Hello. I am the Head Engineer at ColdDirect. I'm glad you chose our company.",
    greetingSpoken: "",
    greetingMark: /head engineer/i,
    or: "or",
    display:
      "For an immediate engineer visit across London, call ColdDirect on 0203 952 4822 or 07983 759320, or email info@colddirect.co.uk. 👍 Found this helpful? Please tap the green Like & Leave a 5-Star Review button below!",
    spoken:
      "For an immediate engineer visit across London, call Cold Direct on 0203 952 4822 or 07983 759320, or email info@colddirect.co.uk. If this advice helped, please tap the green Like and 5-Star Review button below!",
    legacy: CTA_EN_LEGACY,
  },
  fa: {
    bcp: "fa-IR",
    label: "Persian",
    greeting:
      "سلام. من سرمهندس شرکت کولد دایرکت هستم. خوشحالم که شرکت ما را انتخاب کردید.",
    greetingSpoken:
      "سلام. من سرمهندس شرکت کُلد دایرِکت هستم. خوشحالم که شرکت ما را انتخاب کردید.",
    greetingMark: /سرمهندس/,
    or: "یا",
    display:
      "برای اعزام فوری مهندس در سراسر لندن، با کولد دایرکت با شماره 0203 952 4822 یا 07983 759320 تماس بگیرید یا از طریق info@colddirect.co.uk ایمیل بفرستید. 👍 اگر این راهنما مفید بود، لطفاً دکمه سبز «Like & Leave a 5-Star Review» در پایین را بزنید!",
    spoken:
      "برای اعزام فوری مهندس در سراسر لندن، با کُلد دایرِکت با شماره 0203 952 4822 یا 07983 759320 تماس بگیرید یا از طریق info@colddirect.co.uk ایمیل بفرستید. اگر این راهنما مفید بود، لطفاً دکمه سبز لایک و نظر پنج‌ستاره در پایین را بزنید!",
    legacy: CTA_FA_LEGACY,
  },
  tr: {
    bcp: "tr-TR",
    label: "Turkish",
    greeting:
      "Merhaba. Ben ColdDirect'in Baş Mühendisiyim. Şirketimizi seçtiğiniz için teşekkür ederiz.",
    greetingSpoken: "",
    greetingMark: /baş mühendis/i,
    or: "veya",
    display:
      "Londra genelinde acil mühendis ziyareti için ColdDirect'i 0203 952 4822 veya 07983 759320 numarasından arayın ya da info@colddirect.co.uk adresine e-posta gönderin. 👍 Bu bilgi yardımcı olduysa lütfen aşağıdaki yeşil Beğen ve 5 Yıldızlı Yorum düğmesine dokunun!",
    spoken:
      "Londra genelinde acil mühendis ziyareti için Cold Direct'i 0203 952 4822 veya 07983 759320 numarasından arayın ya da info@colddirect.co.uk adresine e-posta gönderin. Bu bilgi yardımcı olduysa lütfen aşağıdaki yeşil Beğen ve 5 Yıldızlı Yorum düğmesine dokunun!",
    legacy: "",
  },
  ar: {
    bcp: "ar-SA",
    label: "Arabic",
    greeting:
      "مرحباً. أنا كبير المهندسين في كولد دايركت. يسعدني أنكم اخترتم شركتنا.",
    greetingSpoken: "",
    greetingMark: /كبير المهندسين|رئيس المهندسين/,
    or: "أو",
    display:
      "لزيارة عاجلة من مهندس في جميع أنحاء لندن، اتصل بكولد دايركت على 0203 952 4822 أو 07983 759320، أو أرسل بريداً إلكترونياً إلى info@colddirect.co.uk. 👍 إذا كانت هذه المعلومات مفيدة، فاضغط على زر الإعجاب الأخضر واترك تقييماً من خمس نجوم أدناه!",
    spoken:
      "لزيارة عاجلة من مهندس في جميع أنحاء لندن، اتصل بكولد دايركت على 0203 952 4822 أو 07983 759320، أو أرسل بريداً إلكترونياً إلى info@colddirect.co.uk. إذا كانت هذه المعلومات مفيدة، فاضغط على زر الإعجاب الأخضر واترك تقييماً من خمس نجوم أدناه!",
    legacy: "",
  },
  es: {
    bcp: "es-ES",
    label: "Spanish",
    greeting:
      "Hola. Soy el Ingeniero Jefe de ColdDirect. Me alegra que haya elegido nuestra empresa.",
    greetingSpoken: "",
    greetingMark: /ingeniero jefe/i,
    or: "o",
    display:
      "Para una visita urgente de un ingeniero en todo Londres, llame a ColdDirect al 0203 952 4822 o al 07983 759320, o escriba a info@colddirect.co.uk. 👍 Si esta información le ayudó, pulse el botón verde de Me gusta y deje una reseña de 5 estrellas abajo!",
    spoken:
      "Para una visita urgente de un ingeniero en todo Londres, llame a Cold Direct al 0203 952 4822 o al 07983 759320, o escriba a info@colddirect.co.uk. Si esta información le ayudó, pulse el botón verde de Me gusta y deje una reseña de 5 estrellas abajo!",
    legacy: "",
  },
  fr: {
    bcp: "fr-FR",
    label: "French",
    greeting:
      "Bonjour. Je suis l’Ingénieur en chef chez ColdDirect. Je suis ravi que vous ayez choisi notre entreprise.",
    greetingSpoken: "",
    greetingMark: /ingénieur en chef/i,
    or: "ou",
    display:
      "Pour une visite urgente d’un ingénieur partout à Londres, appelez ColdDirect au 0203 952 4822 ou au 07983 759320, ou écrivez à info@colddirect.co.uk. 👍 Si ces conseils vous ont aidé, touchez le bouton vert J’aime et laissez un avis 5 étoiles ci-dessous !",
    spoken:
      "Pour une visite urgente d’un ingénieur partout à Londres, appelez Cold Direct au 0203 952 4822 ou au 07983 759320, ou écrivez à info@colddirect.co.uk. Si ces conseils vous ont aidé, touchez le bouton vert J’aime et laissez un avis 5 étoiles ci-dessous !",
    legacy: "",
  },
};

function normalizeBcp(value) {
  var tag = String(value || "")
    .trim()
    .replace(/_/g, "-");
  if (!/^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$/.test(tag)) return "";
  try {
    return Intl.getCanonicalLocales(tag)[0] || "";
  } catch (e) {
    return "";
  }
}

function hasPersianEvidence(raw) {
  return (
    /[\u067E\u0686\u0698\u06AF]/.test(raw) ||
    /(?:یخچال|سرد|سرمهندس|خوشحالم|نیاز|دارد|می‌|نمی|اواپراتور|برای|شرکت)/.test(
      raw,
    )
  );
}

function lockLang(text, hint) {
  var raw = String(text || "");
  var normalized = normalizeBcp(hint);
  var hinted = normalized.split("-")[0].toLowerCase();
  var code;
  if (hasPersianEvidence(raw)) code = "fa";
  else if (/[\u0600-\u06FF]/.test(raw))
    code = hinted && hinted !== "fa" && hinted !== "ar" ? hinted : "ar";
  else if (
    /[ışğİŞĞ]/.test(raw) ||
    /\b(?:merhaba|buzdolabı|soğutmuyor|çalışmıyor|arıza)\b/i.test(raw)
  )
    code = "tr";
  else if (
    /[¿¡ñÑ]/.test(raw) ||
    /\b(?:hola|nevera|enfría|funciona|avería)\b/i.test(raw)
  )
    code = "es";
  else if (
    /[àâçéèêëîïôûùÿœ]/i.test(raw) ||
    /\b(?:bonjour|réfrigérateur|refroidit|fonctionne|panne)\b/i.test(raw)
  )
    code = "fr";
  else if (
    /\b(?:the|and|is|not|fridge|freezer|compressor|engineer)\b/i.test(raw)
  )
    code = "en";
  else if (hinted) code = hinted;
  else code = "en";
  if (LANGS[code])
    return { code: code, bcp: LANGS[code].bcp, label: LANGS[code].label };
  return { code: code, bcp: normalized, label: normalized };
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
  var m = String(mime || "audio/webm")
    .split(";")[0]
    .trim()
    .toLowerCase();
  if (!/^audio\/[a-z0-9.+-]+$/.test(m)) m = "audio/webm";
  if (m === "audio/x-m4a" || m === "audio/m4a") m = "audio/mp4";
  // Mobile browsers occasionally label an AAC/MP4 recording incorrectly. Prefer
  // the container signature over the declaration, without decoding the audio.
  if (audio) {
    try {
      var head = Buffer.from(String(audio).slice(0, 64), "base64");
      if (
        head.length >= 4 &&
        head[0] === 0x1a &&
        head[1] === 0x45 &&
        head[2] === 0xdf &&
        head[3] === 0xa3
      )
        return "audio/webm";
      if (head.length >= 8 && head.toString("ascii", 4, 8) === "ftyp")
        return "audio/mp4";
      if (
        head.length >= 12 &&
        head.toString("ascii", 0, 4) === "RIFF" &&
        head.toString("ascii", 8, 12) === "WAVE"
      )
        return "audio/wav";
      if (head.length >= 4 && head.toString("ascii", 0, 4) === "OggS")
        return "audio/ogg";
      if (head.length >= 2 && head[0] === 0xff && (head[1] & 0xf6) === 0xf0)
        return "audio/aac";
    } catch (e) {}
  }
  return m;
}

function ensureGreeting(text, lang, spoken) {
  var t = String(text || "").trim();
  var profile = LANGS[lang];
  if (!profile) return t;
  if (!profile.greetingMark.test(t)) {
    t = ((spoken && profile.greetingSpoken) || profile.greeting) + " " + t;
  } else if (lang === "fa" && spoken) {
    t = t
      .replace(/کولد دایرکت/g, "کُلد دایرِکت")
      .replace(/ColdDirect/gi, "کُلد دایرِکت");
  }
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
  var profile = LANGS[lang];
  var s = stripTags(stripInstructions(text));
  s = s.replace(/[／/]/g, " " + (profile ? profile.or : "or") + " ");
  s = s.replace(/0203\s*952\s*4822/g, "0203 952 4822");
  s = s.replace(/07983\s*759320/g, "07983 759320");
  if (lang === "fa") {
    s = s.replace(/کولد دایرکت/g, "کُلد دایرِکت");
    s = s.replace(/ColdDirect/gi, "کُلد دایرِکت");
  }
  return s.replace(/\s+/g, " ").trim();
}

function displayCta(lang) {
  return LANGS[lang] ? LANGS[lang].display : "";
}

function spokenCta(lang) {
  return LANGS[lang] ? LANGS[lang].spoken : "";
}

function withoutClose(text, lang) {
  var t = String(text || "").trim();
  var profile = LANGS[lang];
  var closes = profile ? [profile.legacy, profile.display, profile.spoken] : [];
  closes.forEach(function (close) {
    if (!close) return;
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
  var parts =
    ((((json || {}).candidates || [])[0] || {}).content || {}).parts || [];
  return parts
    .map(function (p) {
      return p.text || "";
    })
    .join("")
    .trim();
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
  var parts =
    ((((json || {}).candidates || [])[0] || {}).content || {}).parts || [];
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
  var url =
    "https://generativelanguage.googleapis.com/v1beta/models/" +
    model +
    ":generateContent?key=" +
    encodeURIComponent(key);
  try {
    var res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(timeoutMs || 12000),
    });
    var json = await res.json().catch(function () {
      return {};
    });
    return { ok: res.ok, httpStatus: res.status, json: json };
  } catch (e) {
    var timedOut = e && (e.name === "TimeoutError" || e.name === "AbortError");
    return {
      ok: false,
      httpStatus: 0,
      networkError: timedOut ? "TIMEOUT" : "NETWORK_ERROR",
      json: {
        error: {
          code: timedOut ? 408 : 503,
          status: timedOut ? "TIMEOUT" : "NETWORK_ERROR",
        },
      },
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
  geminiJson: geminiJson,
};
