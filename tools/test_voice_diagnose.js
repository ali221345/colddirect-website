"use strict";

const assert = require("assert");
const core = require("../lib/cd-voice-core");
const handler = require("../api/voice-diagnose");

const KEY = "AIzaTestSecretThatMustNeverLeak123456";
const oldKey = process.env.GEMINI_API_KEY;
const oldVoiceModel = process.env.GEMINI_VOICE_MODEL;
const originalGemini = core.geminiJson;
const originalWarn = console.warn;

function audioWith(bytes, declared) {
  const head = Buffer.from(bytes);
  const body = Buffer.concat([head, Buffer.alloc(90, 7)]);
  return { audio_base64: body.toString("base64"), mime: declared };
}

function response() {
  return {
    headers: {},
    statusCode: 0,
    body: "",
    setHeader(name, value) { this.headers[name] = value; },
    end(value) { this.body = value || ""; }
  };
}

async function post(payload) {
  const req = { method: "POST", headers: { origin: "https://www.colddirect.co.uk" }, body: payload };
  const res = response();
  await handler(req, res);
  return { status: res.statusCode, json: JSON.parse(res.body) };
}

function validModelResponse() {
  return {
    ok: true,
    httpStatus: 200,
    json: { candidates: [{ content: { parts: [{ text: JSON.stringify({
      language: "en-GB",
      transcript: "My commercial fridge is warm and the fan is not running.",
      display_text: "The evaporator fan motor or control circuit needs an engineer inspection.",
      spoken_text: "The evaporator fan motor or control circuit needs an engineer inspection."
    }) }] } }] }
  };
}

async function run() {
  const displayClose = core.ensureClose("The evaporator fan needs an engineer inspection.", "en");
  assert.ok(displayClose.includes("0203 952 4822") && displayClose.includes("07983 759320"));
  assert.ok(displayClose.endsWith("👍 Found this helpful? Please tap the green Like & Leave a 5-Star Review button below!"));
  const spokenClose = core.ttsScript("The evaporator fan needs an engineer inspection.", "en");
  assert.ok(spokenClose.endsWith("For an immediate engineer visit across London, call Cold Direct on 0203 952 4822 or 07983 759320. If this advice helped, please tap the green Like and 5-Star Review button below!"));
  const convertedOldClose = core.ensureClose("The fan needs inspection. Please call us on 0203 952 4822 or 07983 759320, and kindly click the green Like and 5-Star Review button below.", "en");
  assert.strictEqual((convertedOldClose.match(/0203 952 4822/g) || []).length, 1, "Old CTAs must be replaced, not duplicated");
  assert.ok(!/kindly click/i.test(convertedOldClose));
  const persianClose = core.ensureClose("فن اواپراتور نیاز به بررسی مهندس دارد.", "fa");
  assert.ok(persianClose.includes("0203 952 4822") && persianClose.includes("07983 759320") && persianClose.includes("دکمه سبز"));

  assert.strictEqual(core.cleanMime("audio/x-m4a;codecs=aac"), "audio/mp4");
  const samples = [
    [[0x1a, 0x45, 0xdf, 0xa3], "audio/mp4", "audio/webm"],
    [[0, 0, 0, 24, 0x66, 0x74, 0x79, 0x70], "audio/webm", "audio/mp4"],
    [[0x52, 0x49, 0x46, 0x46, 0, 0, 0, 0, 0x57, 0x41, 0x56, 0x45], "audio/webm", "audio/wav"],
    [[0x4f, 0x67, 0x67, 0x53], "audio/webm", "audio/ogg"],
    [[0xff, 0xf1, 0x50, 0x80], "audio/webm", "audio/aac"]
  ];
  for (const [bytes, declared, expected] of samples) {
    const sample = audioWith(bytes, declared);
    assert.strictEqual(core.cleanMime(declared, sample.audio_base64), expected);
  }

  process.env.GEMINI_API_KEY = KEY;
  delete process.env.GEMINI_VOICE_MODEL;
  let seenMime = "";
  core.geminiJson = async (key, model, body, timeout) => {
    assert.strictEqual(model, "gemini-3.6-flash");
    assert.strictEqual(timeout, 30000);
    seenMime = body.contents[0].parts[1].inlineData.mimeType;
    return validModelResponse();
  };
  const mp4 = audioWith([0, 0, 0, 24, 0x66, 0x74, 0x79, 0x70], "audio/webm");
  const ok = await post(mp4);
  assert.strictEqual(ok.status, 200);
  assert.strictEqual(ok.json.ok, true);
  assert.ok(ok.json.transcript.includes("commercial fridge"));
  assert.ok(ok.json.spoken_text.length > 40);
  assert.strictEqual(seenMime, "audio/mp4");

  const attemptedModels = [];
  core.geminiJson = async (key, model, body, timeout) => {
    attemptedModels.push(model);
    if (attemptedModels.length === 1) return { ok: false, httpStatus: 503, json: { error: { code: 503, status: "UNAVAILABLE" } } };
    assert.strictEqual(timeout, 20000);
    return validModelResponse();
  };
  const recovered = await post(mp4);
  assert.strictEqual(recovered.json.ok, true);
  assert.deepStrictEqual(attemptedModels, ["gemini-3.6-flash", "gemini-2.5-flash"]);

  const quotaModels = [];
  core.geminiJson = async (key, model) => {
    quotaModels.push(model);
    return { ok: false, httpStatus: 429, json: { error: { code: 429, status: "RESOURCE_EXHAUSTED", message: "Quota exhausted" } } };
  };
  const quotaAudio = await post(mp4);
  assert.strictEqual(quotaAudio.status, 200);
  assert.strictEqual(quotaAudio.json.ok, true, "Audio quota failures must still return useful expert guidance");
  assert.strictEqual(quotaAudio.json.code, "EXPERT_FALLBACK");
  assert.strictEqual(quotaAudio.json.diagnostic.upstreamHttp, 429);
  assert.ok(!/could not hear that clearly/i.test(quotaAudio.json.display_text));
  assert.ok(/transcription/i.test(quotaAudio.json.display_text), "Audio fallback must honestly disclose unavailable transcription");
  assert.ok(/0203 952 4822/.test(quotaAudio.json.display_text));
  assert.deepStrictEqual(quotaModels, ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash"]);

  const quotaText = await post({ text: "My display cabinet shows E1 and is too warm", language: "auto", mode: "text" });
  assert.strictEqual(quotaText.json.ok, true);
  assert.strictEqual(quotaText.json.code, "EXPERT_FALLBACK");
  assert.ok(/E1|sensor|controller/i.test(quotaText.json.display_text), "Text fallback must diagnose the reported error code");
  assert.ok(!/could not hear that clearly/i.test(quotaText.json.display_text));

  core.geminiJson = async () => ({ ok: false, httpStatus: 404, json: { error: { code: 404, status: "NOT_FOUND", message: `Model unavailable; key=${KEY}` } } });
  const notFound = await post(mp4);
  assert.strictEqual(notFound.json.ok, true);
  assert.strictEqual(notFound.json.diagnostic.upstreamHttp, 404);
  assert.strictEqual(notFound.json.diagnostic.upstreamStatus, "NOT_FOUND");
  assert.ok(!JSON.stringify(notFound).includes(KEY));

  core.geminiJson = async () => ({ ok: false, httpStatus: 0, networkError: "TIMEOUT", json: { error: { code: 408, status: "TIMEOUT" } } });
  const timeout = await post(mp4);
  assert.strictEqual(timeout.json.ok, true);
  assert.strictEqual(timeout.json.diagnostic.upstreamStatus, "TIMEOUT");

  delete process.env.GEMINI_API_KEY;
  delete process.env.GOOGLE_API_KEY;
  const missing = await post(mp4);
  assert.strictEqual(missing.json.ok, true);
  assert.strictEqual(missing.json.diagnostic.upstreamStatus, "API_KEY_MISSING");

  const ruleCases = [
    "Commercial fridge evaporator fan is not running",
    "Freezer high temperature alarm is active",
    "Cold room door was left open and stock is warm",
    "Ice machine is not making ice",
    "Taylor ice cream machine is not freezing",
    "Carpigiani machine has a beater fault",
    "Compressor is hot and buzzing",
    "Defrost is not working and the coil is iced",
    "Thermostat is not controlling temperature",
    "I suspect a refrigerant gas leak",
    "Controller shows E2"
  ];
  for (const text of ruleCases) {
    const local = await post({ text, language: "auto", mode: "text" });
    assert.strictEqual(local.json.ok, true, text);
    assert.strictEqual(local.json.code, "EXPERT_FALLBACK", text);
    assert.ok(local.json.display_text.length > 120, text);
    assert.ok(/0203 952 4822/.test(local.json.display_text), text);
  }

  process.env.GEMINI_API_KEY = KEY;
  core.geminiJson = async () => { throw new Error("socket failed"); };
  const thrown = await post(mp4);
  assert.strictEqual(thrown.json.ok, true);
  assert.strictEqual(thrown.json.diagnostic.upstreamStatus, "REQUEST_EXCEPTION");
  assert.ok(!JSON.stringify(thrown).includes(KEY));

  console.log("Voice diagnosis regression tests passed: signatures, model failover, 429 expert guidance, equipment rules, timeout and redaction.");
}

run().catch((error) => {
  console.error(error);
  process.exitCode = 1;
}).finally(() => {
  core.geminiJson = originalGemini;
  console.warn = originalWarn;
  if (oldKey === undefined) delete process.env.GEMINI_API_KEY;
  else process.env.GEMINI_API_KEY = oldKey;
  if (oldVoiceModel === undefined) delete process.env.GEMINI_VOICE_MODEL;
  else process.env.GEMINI_VOICE_MODEL = oldVoiceModel;
});
