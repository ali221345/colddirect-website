/**
 * Live Voice-in → Voice-out: SPEAK tap, silence auto-stop, auto-play via __cdPlayCtx.
 */
const { chromium } = require("playwright");

const URL = process.env.VOICE_E2E_URL || "https://www.colddirect.co.uk/";

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ["--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream", "--autoplay-policy=no-user-gesture-required"],
  });
  const context = await browser.newContext({
    permissions: ["microphone"],
  });
  const page = await context.newPage();
  const errors = [];
  page.on("console", (msg) => {
    const t = msg.text() || "";
    if (/NotAllowedError|play\(\) failed/i.test(t)) errors.push(t);
  });
  page.on("pageerror", (err) => {
    if (/NotAllowedError/i.test(String(err))) errors.push(String(err));
  });

  await page.addInitScript(() => {
    const orig = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
    navigator.mediaDevices.getUserMedia = async (constraints) => {
      if (constraints && constraints.audio) {
        const AC = window.AudioContext || window.webkitAudioContext;
        const ctx = new AC();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        const dest = ctx.createMediaStreamDestination();
        osc.connect(gain);
        gain.connect(dest);
        osc.start();
        setTimeout(() => {
          try { gain.gain.setValueAtTime(0, ctx.currentTime); } catch (e) {}
        }, 700);
        window.__cdFakeMicCtx = ctx;
        return dest.stream;
      }
      return orig(constraints);
    };
  });

  await page.goto(URL, { waitUntil: "domcontentloaded", timeout: 45000 });
  await page.waitForSelector("#cd-voice-speak", { timeout: 20000 });

  async function runLang(lang) {
    if (lang !== "auto") {
      await page.selectOption("#cd-voice-lang", lang).catch(() => {});
    }
    await page.click("#cd-voice-speak");
    await page.waitForTimeout(5500);
    const shot = await page.evaluate(() => ({
      playState: window.__cdPlayCtx ? window.__cdPlayCtx.state : "missing",
      audioPlayed: !!window.__cdAudioPlayed,
      speaking: !!(window.speechSynthesis && window.speechSynthesis.speaking),
      status: (document.getElementById("cd-voice-status") || {}).textContent || "",
      card: !document.getElementById("cd-voice-card")?.hidden,
    }));
    return shot;
  }

  const results = {};
  for (const lang of ["fa", "en", "tl"]) {
    await page.evaluate(() => { window.__cdAudioPlayed = false; });
    results[lang] = await runLang(lang);
    console.log(lang, JSON.stringify(results[lang]));
  }

  await browser.close();

  const ok = ["fa", "en", "tl"].every((lang) => {
    const r = results[lang];
    return r.card && (r.audioPlayed || r.speaking || r.playState === "running") && r.playState !== "missing";
  });
  if (errors.length) {
    console.error("NotAllowedError", errors);
    process.exit(1);
  }
  if (!ok) {
    console.error("FAIL autoplay", results);
    process.exit(1);
  }
  console.log("OK voice-in voice-out autoplay");
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
