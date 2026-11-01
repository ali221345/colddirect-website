"use strict";

const assert = require("assert");
const core = require("../lib/cd-voice-core");
const handler = require("../api/voice-tts");

const originalGemini = core.geminiJson;
const originalFetch = global.fetch;
const originalWarn = console.warn;
const envNames = [
  "GEMINI_API_KEY",
  "GOOGLE_API_KEY",
  "GEMINI_API_KEY_SECONDARY",
  "SECONDARY_GEMINI_API_KEY",
  "GEMINI_API_KEY_2",
  "GOOGLE_API_KEY_2",
  "AZURE_SPEECH_KEY",
  "ELEVENLABS_API_KEY",
  "XI_API_KEY",
  "OPENAI_API_KEY",
];
const originalEnv = Object.fromEntries(
  envNames.map((name) => [name, process.env[name]]),
);

async function post(
  text = "The evaporator fan needs an engineer inspection.",
  extra = {},
) {
  const req = {
    method: "POST",
    headers: { origin: "https://www.colddirect.co.uk" },
    body: { text, language: "en-GB", ...extra },
  };
  const res = {
    headers: {},
    setHeader(name, value) {
      this.headers[name] = value;
    },
    end(value) {
      this.body = value;
    },
  };
  await handler(req, res);
  return JSON.parse(res.body);
}

function audioResponse() {
  return {
    ok: true,
    httpStatus: 200,
    json: {
      candidates: [
        {
          content: {
            parts: [
              {
                inlineData: {
                  mimeType: "audio/pcm",
                  data: Buffer.alloc(48000, 2).toString("base64"),
                },
              },
            ],
          },
        },
      ],
    },
  };
}

async function run() {
  for (const name of envNames) delete process.env[name];
  process.env.GEMINI_API_KEY = "test-key-not-a-real-credential";
  console.warn = () => {};

  let calls = 0;
  let spokenText = "";
  core.geminiJson = async (key, model, body) => {
    calls++;
    assert.strictEqual(model, "gemini-3.8-flash-tts");
    spokenText = body.contents[0].parts[0].text;
    return audioResponse();
  };
  const longAnswer =
    "Hello. I am the Head Engineer at ColdDirect. I'm glad you chose our company. The evaporator fan is not running and the cabinet is becoming warm. Switch the unit off to protect the compressor and stored stock. An engineer should inspect the fan motor, power supply and controller before restarting it. Please call us on 0203 952 4822 or 07983 759320, and kindly click the green Like and 5-Star Review button below.";
  const recovered = await post(longAnswer);
  assert.strictEqual(recovered.ok, true, JSON.stringify(recovered.diagnostic));
  assert.strictEqual(recovered.audio_mime, "audio/mpeg");
  assert.strictEqual(recovered.provider, "gemini");
  assert.strictEqual(
    calls,
    1,
    "one diagnosis must make one primary TTS request",
  );
  const summaryWords = spokenText.split(/\s+/).filter(Boolean).length;
  assert.ok(
    summaryWords >= 40 && summaryWords <= 72,
    `Expected a concise 40-72 word summary, received ${summaryWords}`,
  );
  assert.ok(
    /evaporator fan/i.test(spokenText),
    "The technical diagnosis must remain in the summary",
  );
  assert.ok(
    /Head Engineer/i.test(spokenText),
    "The greeting must remain in spoken audio",
  );
  assert.ok(
    /0203 952 4822/.test(spokenText) && /07983 759320/.test(spokenText),
    "Both naturally formatted phone numbers must be spoken",
  );
  assert.ok(
    spokenText.includes("info@colddirect.co.uk"),
    "The email must be spoken",
  );
  assert.ok(
    spokenText.endsWith(
      "If this advice helped, please tap the green Like and 5-Star Review button below!",
    ),
    "The mandatory spoken CTA must be last",
  );
  assert.strictEqual(
    (spokenText.match(/5-Star Review/g) || []).length,
    1,
    "The CTA must not be duplicated",
  );
  assert.strictEqual(recovered.summary_words, summaryWords);
  const mp3 = Buffer.from(recovered.audio_base64, "base64");
  assert.ok(mp3.length > 1000 && mp3.length < 15000);
  assert.ok(mp3[0] === 0xff && (mp3[1] & 0xe0) === 0xe0);

  calls = 0;
  core.geminiJson = async () => {
    calls++;
    if (calls === 1)
      return {
        ok: true,
        httpStatus: 200,
        json: { candidates: [{ content: { parts: [] } }] },
      };
    return audioResponse();
  };
  const retried = await post();
  assert.strictEqual(retried.ok, true, "NO_AUDIO must be retried");
  assert.strictEqual(calls, 2);
  assert.strictEqual(retried.audio_mime, "audio/mpeg");

  calls = 0;
  core.geminiJson = async () => {
    calls++;
    return {
      ok: false,
      httpStatus: 429,
      json: { error: { code: 429, status: "RESOURCE_EXHAUSTED" } },
    };
  };
  const exhausted = await post();
  assert.strictEqual(exhausted.ok, false);
  assert.strictEqual(exhausted.error, "TTS_UNAVAILABLE");
  assert.strictEqual(exhausted.audio_base64, "");
  assert.strictEqual(exhausted.diagnostic.upstreamHttp, 429);
  assert.strictEqual(
    calls,
    2,
    "Retryable quota failure must have one bounded retry",
  );
  assert.ok(!JSON.stringify(exhausted).includes("test-key"));

  process.env.OPENAI_API_KEY = "test-openai-fallback-not-a-real-credential";
  const fallbackBytes = Buffer.alloc(2400, 7);
  fallbackBytes[0] = 0xff;
  fallbackBytes[1] = 0xfb;
  let fallbackCalls = 0;
  global.fetch = async (url, options) => {
    fallbackCalls++;
    assert.strictEqual(url, "https://api.openai.com/v1/audio/speech");
    assert.strictEqual(JSON.parse(options.body).response_format, "mp3");
    return { ok: true, status: 200, arrayBuffer: async () => fallbackBytes };
  };
  calls = 0;
  const failedOver = await post();
  assert.strictEqual(
    failedOver.ok,
    true,
    JSON.stringify(failedOver.diagnostic),
  );
  assert.strictEqual(failedOver.provider, "openai");
  assert.strictEqual(
    Buffer.from(failedOver.audio_base64, "base64").length,
    2400,
  );
  assert.strictEqual(calls, 2);
  assert.strictEqual(fallbackCalls, 1);

  delete process.env.GEMINI_API_KEY;
  delete process.env.OPENAI_API_KEY;
  process.env.AZURE_SPEECH_KEY = "test-azure-fallback-not-a-real-credential";
  const azureCases = [
    {
      language: "tr-TR",
      text: "Kompresör çalışmıyor.",
      voice: "tr-TR-AhmetNeural",
    },
    { language: "ar-SA", text: "الضاغط لا يعمل.", voice: "ar-SA-HamedNeural" },
  ];
  for (const testCase of azureCases) {
    let ssml = "";
    global.fetch = async (url, options) => {
      ssml = options.body;
      return { ok: true, status: 200, arrayBuffer: async () => fallbackBytes };
    };
    const azureReply = await post(testCase.text, {
      language: testCase.language,
    });
    assert.strictEqual(azureReply.ok, true);
    assert.strictEqual(azureReply.language, testCase.language);
    assert.ok(ssml.includes(`xml:lang='${testCase.language}'`));
    assert.ok(ssml.includes(`name='${testCase.voice}'`));
  }

  console.log(
    "Voice TTS regression tests passed: concise native speech, NO_AUDIO retry, bounded quota retry, dynamic Azure locales and provider failover.",
  );
}

run()
  .catch((error) => {
    console.error(error);
    process.exitCode = 1;
  })
  .finally(() => {
    core.geminiJson = originalGemini;
    global.fetch = originalFetch;
    console.warn = originalWarn;
    for (const name of envNames) {
      if (originalEnv[name] === undefined) delete process.env[name];
      else process.env[name] = originalEnv[name];
    }
  });
