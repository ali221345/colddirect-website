"use strict";

const assert = require("assert");
const fs = require("fs");
const source = fs.readFileSync(
  require("path").join(__dirname, "../assets/js/colddirect-voice-bar.js"),
  "utf8",
);

assert.ok(
  /function unlockAudio\(\)[\s\S]*?source\.start\(0\)/.test(source),
  "A silent AudioContext buffer must start inside the user gesture",
);
assert.ok(
  /function unlockAudio\(\)[\s\S]*?speechSynthesis\.speak\(nativePrimer\)/.test(
    source,
  ),
  "Native speech must be unlocked inside the initial gesture",
);
assert.ok(
  /player\.playsInline = true/.test(source),
  "The persistent player must use inline playback",
);
assert.ok(
  /function playBytes[\s\S]*?URL\.createObjectURL/.test(source),
  "Compressed audio must use Blob URLs, not large data URLs",
);
const playBytes = source.slice(
  source.indexOf("function playBytes"),
  source.indexOf("function speakBrowser"),
);
assert.ok(
  !playBytes.includes("unlockAudio()"),
  "Async playback must reuse the unlocked element, not re-prime it",
);
assert.ok(
  !playBytes.includes("decodeAudioData"),
  "iOS playback must use the native HTMLAudioElement",
);
assert.ok(
  source.includes("summary: true"),
  "Speech requests must use one concise summary",
);
assert.ok(
  !source.includes("chunk: true"),
  "The old multi-call chunk requests must be removed",
);
assert.ok(
  source.includes("SPOKEN_SUMMARY_MAX_WORDS = 72"),
  "Spoken summaries must have a 72-word total budget",
);
assert.ok(
  source.includes("SPOKEN_TECHNICAL_MAX_WORDS = 39"),
  "Technical advice must leave room for the complete CTA",
);
assert.ok(
  source.includes(
    "For an immediate engineer visit across London, call Cold Direct on 0203 952 4822 or 07983 759320. If this advice helped, please tap the green Like and 5-Star Review button below!",
  ),
  "Native browser speech must include both phone numbers and the review CTA",
);
assert.strictEqual(
  source.split("postJson(TTS_URLS[0]").length - 1,
  1,
  "Only one TTS request path may exist",
);
assert.ok(
  source.includes("return playCachedSpeech()"),
  "LISTEN must use cached speech",
);
assert.ok(
  source.includes(
    "if (entry && entry.data) return Promise.resolve(entry.data)",
  ),
  "Cached MP3 audio must not be fetched again",
);
assert.ok(
  source.includes("if (first.native) return nativeFallback(token)"),
  "LISTEN must replay cached native speech without a request",
);
assert.ok(
  source.includes("return nativeFallback(token);"),
  "TTS and playback failures must use native speech",
);
assert.ok(
  source.includes("voiceEl.pause();") &&
    !source.includes('voiceEl.removeAttribute("src")'),
  "Stopping playback must preserve cached media",
);
assert.ok(
  source.includes("showVoiceError"),
  "Fallback errors must remain in the assistant bubble",
);
assert.ok(
  !source.includes("SpeechRecognition") &&
    !source.includes("webkitSpeechRecognition"),
  "Browser speech recognition must be completely removed",
);
const startLive = source.slice(
  source.indexOf("function startLive"),
  source.indexOf("function onSpeakPointer"),
);
assert.ok(
  startLive.includes("startRecorder(my);"),
  "SPEAK must always start MediaRecorder directly",
);
assert.ok(
  source.includes("audio_base64: b64"),
  "The raw recording must be sent to the diagnosis endpoint",
);
assert.ok(
  /RECORDER_SILENCE_MS = 2000/.test(source),
  "MediaRecorder must stop after 2 seconds of detected silence",
);
assert.ok(
  /RECORDER_MAX_MS = 6000/.test(source),
  "MediaRecorder must retain its 6-second maximum",
);
assert.ok(
  source.includes("rec.requestData();") && source.includes("rec.onstop ="),
  "iOS recording must flush the final chunk before creating the Blob",
);
assert.ok(
  !source.includes("}, 45000);"),
  "The old 45-second recorder wait must be removed",
);
assert.ok(
  !source.includes("navigator.language"),
  "Browser locale must not select the customer language",
);
assert.ok(
  source.includes("u.lang = lang"),
  "Native speech must preserve the response BCP-47 tag",
);
assert.ok(
  source.includes("info@colddirect.co.uk"),
  "Browser speech must include email",
);
assert.ok(
  !source.includes(".replace(/Hello\\. I am the Head Engineer"),
  "The greeting must remain in speech",
);
console.log(
  "Voice frontend regression tests passed: MediaRecorder-only capture, raw audio submission, dynamic language and LISTEN fallback.",
);
