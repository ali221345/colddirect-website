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
  source.includes("blob.size < 2000"),
  "Recordings under 2000 bytes must use the microphone guidance",
);
assert.ok(
  source.includes(
    "Microphone is blocked or too quiet. On your computer: Settings > Microphone Privacy > Turn ON. In browser: Click lock icon > Allow microphone > Refresh. Then try again.",
  ),
  "Small recordings must show the exact microphone recovery instructions",
);
assert.ok(
  /RECORDER_SILENCE_MS = 4000/.test(source),
  "MediaRecorder must allow at least 4 seconds of silence after speech",
);
assert.ok(
  /RECORDER_MAX_MS = 30000/.test(source),
  "MediaRecorder must allow up to 30 seconds before automatic submission",
);
assert.ok(
  source.includes("window.__cdVoiceAudioController") &&
    source.includes("stopAll: function"),
  "One global audio controller must own playback cancellation",
);
assert.ok(
  source.includes('document.querySelectorAll("audio")') &&
    source.includes("window.speechSynthesis.cancel()"),
  "Starting playback must pause HTML audio and cancel browser speech",
);
assert.ok(
  source.includes("serverAudioPlaying()") &&
    /function nativeFallback[\s\S]*?serverAudioPlaying\(\)/.test(source),
  "Browser fallback must never start while server audio is playing",
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
const recorderSource = source.slice(
  source.indexOf("function startRecorder"),
  source.indexOf("function startLive"),
);
assert.ok(
  recorderSource.includes("MediaRecorder.isTypeSupported(mimeCandidates[mi])"),
  "Recorder must feature-detect each candidate MIME type",
);
for (const mime of ["audio/webm", "audio/mp4", "audio/aac"]) {
  assert.ok(
    recorderSource.includes(`"${mime}"`),
    `Recorder feature detection must include ${mime}`,
  );
}
assert.ok(
  recorderSource.includes("mediaRec.mimeType"),
  "The recorder's actual MIME type must be retained",
);
assert.ok(
  source.includes("blob.type || recMime"),
  "The final Blob type must take precedence for the uploaded MIME type",
);
const finishRecordingSource = source.slice(
  source.indexOf("function finishRecording"),
  source.indexOf("var SPEECH_PROFILES"),
);
assert.ok(
  !finishRecordingSource.includes("setTimeout(done"),
  "Recorder finalization must wait for onstop instead of racing a timeout",
);
const playSpeechSource = source.slice(
  source.indexOf("function playSpeech"),
  source.indexOf("function speakAnswer"),
);
assert.ok(
  playSpeechSource.includes("if (!audio) return nativeFallback(token);"),
  "Device speech is allowed only when the server has no audio payload",
);
assert.ok(
  !/return playBytes[\s\S]*?\.catch\(function \(\) \{\s*return nativeFallback/.test(
    playSpeechSource,
  ),
  "Server audio playback failures must not trigger robotic device speech",
);
console.log(
  "Voice frontend regression tests passed: MediaRecorder-only capture, raw audio submission, dynamic language and LISTEN fallback.",
);
