/**
 * Speaks Arabic text using the browser's built-in TTS as a reference model.
 * This is a stop-gap: a production app should use recorded audio from a
 * qualified reciter (قارئ) for accurate makhraj, since TTS makhraj is imperfect.
 */
export function speakArabic(text: string): void {
  if (typeof speechSynthesis === "undefined") return;
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = "ar-SA";
  u.rate = 0.7;
  const arVoice = speechSynthesis.getVoices().find((v) => v.lang.startsWith("ar"));
  if (arVoice) u.voice = arVoice;
  speechSynthesis.speak(u);
}

export function ttsHasArabic(): boolean {
  if (typeof speechSynthesis === "undefined") return false;
  return speechSynthesis.getVoices().some((v) => v.lang.startsWith("ar"));
}
