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
    assert.strictEqual(model, "gemini-3.8-flash");
    assert.strictEqual(timeout, 45000);
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

  core.geminiJson = async () => ({ ok: false, httpStatus: 404, json: { error: { code: 404, status: "NOT_FOUND", message: `Model unavailable; key=${KEY}` } } });
  const notFound = await post(mp4);
  assert.strictEqual(notFound.json.ok, false);
  assert.strictEqual(notFound.json.diagnostic.upstreamHttp, 404);
  assert.strictEqual(notFound.json.diagnostic.upstreamStatus, "NOT_FOUND");
  assert.ok(!JSON.stringify(notFound).includes(KEY));

  core.geminiJson = async () => ({ ok: false, httpStatus: 0, networkError: "TIMEOUT", json: { error: { code: 408, status: "TIMEOUT" } } });
  const timeout = await post(mp4);
  assert.strictEqual(timeout.json.diagnostic.upstreamStatus, "TIMEOUT");

  delete process.env.GEMINI_API_KEY;
  delete process.env.GOOGLE_API_KEY;
  const missing = await post(mp4);
  assert.strictEqual(missing.json.diagnostic.upstreamStatus, "API_KEY_MISSING");

  process.env.GEMINI_API_KEY = KEY;
  core.geminiJson = async () => { throw new Error("socket failed"); };
  const thrown = await post(mp4);
  assert.strictEqual(thrown.json.diagnostic.upstreamStatus, "REQUEST_EXCEPTION");
  assert.ok(!JSON.stringify(thrown).includes(KEY));

  console.log("Voice diagnosis regression tests passed: signatures, success, upstream errors, timeout, missing key and redaction.");
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
