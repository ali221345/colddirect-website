"use strict";

const assert = require("assert");
const fs = require("fs");
const source = fs.readFileSync(require("path").join(__dirname, "../assets/js/colddirect-voice-bar.js"), "utf8");

assert.ok(/function unlockAudio\(\)[\s\S]*?source\.start\(0\)/.test(source), "A silent AudioContext buffer must start inside the user gesture");
assert.ok(/player\.playsInline = true/.test(source), "The persistent player must use inline playback");
assert.ok(/function playBytes[\s\S]*?URL\.createObjectURL/.test(source), "Compressed audio must use Blob URLs, not large data URLs");
const playBytes = source.slice(source.indexOf("function playBytes"), source.indexOf("function speakBrowser"));
assert.ok(!playBytes.includes("unlockAudio()"), "Async playback must reuse the unlocked element, not re-prime it");
assert.ok(!playBytes.includes("decodeAudioData"), "iOS playback must use the native HTMLAudioElement");
assert.ok(source.includes("chunk: true"), "Speech requests must use short chunks");
assert.ok(source.includes("return playCachedSpeech()"), "LISTEN must use cached speech");
assert.ok(source.includes("if (entry && entry.data) return Promise.resolve(entry.data)"), "Cached audio must not be fetched again");
assert.ok(source.includes("voiceEl.pause();") && !source.includes("voiceEl.removeAttribute(\"src\")"), "Stopping playback must preserve cached media");
assert.ok(source.includes("showVoiceError"), "Fallback errors must remain in the assistant bubble");
console.log("Voice frontend regression tests passed: gesture unlock, inline MP3 Blobs, chunking, cached LISTEN and error attribution.");
