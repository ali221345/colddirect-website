"use strict";

const assert = require("assert");
const core = require("../lib/cd-voice-core");
const handler = require("../api/voice-tts");

const originalGemini = core.geminiJson;
const originalKey = process.env.GEMINI_API_KEY;
const originalWarn = console.warn;

async function post(chunk = false) {
  const req = { method: "POST", headers: { origin: "https://www.colddirect.co.uk" }, body: { text: "The evaporator fan needs an engineer inspection.", language: "en-GB", chunk } };
  const res = { headers: {}, setHeader(name, value) { this.headers[name] = value; }, end(value) { this.body = value; } };
  await handler(req, res);
  return JSON.parse(res.body);
}

function audioResponse() {
  return { ok: true, httpStatus: 200, json: { candidates: [{ content: { parts: [{ inlineData: { mimeType: "audio/pcm", data: Buffer.alloc(48000, 2).toString("base64") } }] } }] } };
}

async function run() {
  process.env.GEMINI_API_KEY = "test-key-not-a-real-credential";
  console.warn = () => {};
  const models = [];
  core.geminiJson = async (key, model) => {
    models.push(model);
    if (models.length === 1) return { ok: false, httpStatus: 503, json: { error: { code: 503, status: "UNAVAILABLE" } } };
    return audioResponse();
  };
  const recovered = await post();
  assert.strictEqual(recovered.ok, true, JSON.stringify(recovered.diagnostic));
  assert.strictEqual(recovered.audio_mime, "audio/mpeg");
  const mp3 = Buffer.from(recovered.audio_base64, "base64");
  assert.ok(mp3.length > 1000 && mp3.length < 15000);
  assert.ok(mp3[0] === 0xff && (mp3[1] & 0xe0) === 0xe0);
  assert.deepStrictEqual(models, ["gemini-3.8-flash-lite-tts", "gemini-3.8-flash-tts"]);

  let chunkText = "";
  core.geminiJson = async (key, model, body) => { chunkText = body.contents[0].parts[0].text; return audioResponse(); };
  const chunked = await post(true);
  assert.strictEqual(chunked.ok, true);
  assert.ok(!/5-star review button/i.test(chunkText), "TTS chunks must not repeat the closing CTA");

  let calls = 0;
  core.geminiJson = async () => { calls++; return { ok: false, httpStatus: 400, json: { error: { code: 400, status: "INVALID_ARGUMENT" } } }; };
  const rejected = await post();
  assert.strictEqual(rejected.ok, false);
  assert.strictEqual(rejected.diagnostic.upstreamHttp, 400);
  assert.strictEqual(calls, 1);
  assert.ok(!JSON.stringify(rejected).includes("test-key"));
  console.log("Voice TTS regression tests passed: current-model fallback, compact MP3 output, chunk text and safe errors.");
}

run().catch((error) => { console.error(error); process.exitCode = 1; }).finally(() => {
  core.geminiJson = originalGemini;
  console.warn = originalWarn;
  if (originalKey === undefined) delete process.env.GEMINI_API_KEY;
  else process.env.GEMINI_API_KEY = originalKey;
});
