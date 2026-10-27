"use strict";

const assert = require("assert");
const fs = require("fs");
const source = fs.readFileSync(require("path").join(__dirname, "../assets/js/colddirect-voice-bar.js"), "utf8");

assert.ok(/function unlockAudio\(\)[\s\S]*?source\.start\(0\)/.test(source), "A silent AudioContext buffer must start inside the user gesture");
assert.ok(/function unlockAudio\(\)[\s\S]*?speechSynthesis\.speak\(nativePrimer\)/.test(source), "Native speech must be unlocked inside the initial gesture");
assert.ok(/player\.playsInline = true/.test(source), "The persistent player must use inline playback");
assert.ok(/function playBytes[\s\S]*?URL\.createObjectURL/.test(source), "Compressed audio must use Blob URLs, not large data URLs");
const playBytes = source.slice(source.indexOf("function playBytes"), source.indexOf("function speakBrowser"));
assert.ok(!playBytes.includes("unlockAudio()"), "Async playback must reuse the unlocked element, not re-prime it");
assert.ok(!playBytes.includes("decodeAudioData"), "iOS playback must use the native HTMLAudioElement");
assert.ok(source.includes("summary: true"), "Speech requests must use one concise summary");
assert.ok(!source.includes("chunk: true"), "The old multi-call chunk requests must be removed");
assert.ok(source.includes("slice(0, 45)"), "Spoken summaries must be capped at 45 words");
assert.strictEqual(source.split("postJson(TTS_URLS[0]").length - 1, 1, "Only one TTS request path may exist");
assert.ok(source.includes("return playCachedSpeech()"), "LISTEN must use cached speech");
assert.ok(source.includes("if (entry && entry.data) return Promise.resolve(entry.data)"), "Cached MP3 audio must not be fetched again");
assert.ok(source.includes("if (first.native) return nativeFallback(token)"), "LISTEN must replay cached native speech without a request");
assert.ok(source.includes("return nativeFallback(token);"), "TTS and playback failures must use native speech");
assert.ok(source.includes("voiceEl.pause();") && !source.includes("voiceEl.removeAttribute(\"src\")"), "Stopping playback must preserve cached media");
assert.ok(source.includes("showVoiceError"), "Fallback errors must remain in the assistant bubble");
console.log("Voice frontend regression tests passed: one summary, native unlock, MP3/native cache and LISTEN fallback.");
