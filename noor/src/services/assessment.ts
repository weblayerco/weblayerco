import type { AssessmentResult, HarakahInfo, Letter } from "../types";
import { applyHarakah } from "../data/curriculum";

export interface AssessTarget {
  letter: Letter;
  harakah: HarakahInfo;
  recordingBlob: Blob;
}

export interface PronunciationAssessor {
  /** identifier shown in results, e.g. "heuristic" or "server-gop" */
  readonly name: string;
  assess(target: AssessTarget): Promise<AssessmentResult>;
}

interface AudioStats {
  durationSec: number;
  rms: number;
  hasSpeech: boolean;
}

/** Decode the recording and compute crude loudness/length stats, fully local. */
async function analyzeAudio(blob: Blob): Promise<AudioStats> {
  const Ctx = window.AudioContext || (window as any).webkitAudioContext;
  const ctx: AudioContext = new Ctx();
  try {
    const buf = await ctx.decodeAudioData(await blob.arrayBuffer());
    const data = buf.getChannelData(0);
    let sumSq = 0;
    for (let i = 0; i < data.length; i++) sumSq += data[i] * data[i];
    const rms = Math.sqrt(sumSq / data.length);
    return {
      durationSec: buf.duration,
      rms,
      hasSpeech: buf.duration >= 0.25 && rms > 0.01,
    };
  } finally {
    ctx.close();
  }
}

/**
 * Default, fully-local assessor. It can reliably detect "nothing was said"
 * or "too short", which already removes a class of false passes. It does NOT
 * yet verify that the correct letter/makhraj was produced — that requires a
 * phoneme-level model (see ServerAssessor) — so the parent confirms the gate.
 */
export class HeuristicAssessor implements PronunciationAssessor {
  readonly name = "heuristic";

  async assess(target: AssessTarget): Promise<AssessmentResult> {
    const stats = await analyzeAudio(target.recordingBlob);
    const glyph = applyHarakah(target.letter, target.harakah);
    if (!stats.hasSpeech) {
      return {
        pass: false,
        score: 0,
        message: "لم نسمع صوتاً واضحاً. اضغط على الميكروفون وانطق الحرف بصوت مسموع.",
        engine: this.name,
      };
    }
    return {
      pass: true,
      score: Math.min(1, stats.rms * 8),
      message: `سجّلنا محاولتك لنطق «${glyph}». استمع إليها، فإن كان النطق صحيحاً اضغط «أحسنت».`,
      engine: this.name,
    };
  }
}

/**
 * Sends the audio to a backend that runs a real pronunciation model
 * (e.g. phoneme-level Goodness-of-Pronunciation tuned for Arabic makharij and
 * children's speech). Not enabled by default — wire VITE_ASSESS_URL to use it.
 */
export class ServerAssessor implements PronunciationAssessor {
  readonly name = "server";
  constructor(private endpoint: string) {}

  async assess(target: AssessTarget): Promise<AssessmentResult> {
    const form = new FormData();
    form.append("audio", target.recordingBlob, "attempt.webm");
    form.append("letter", target.letter.id);
    form.append("harakah", target.harakah.id);
    const res = await fetch(this.endpoint, { method: "POST", body: form });
    if (!res.ok) throw new Error(`assessment server error: ${res.status}`);
    const data = (await res.json()) as Partial<AssessmentResult>;
    return {
      pass: !!data.pass,
      score: data.score,
      heard: data.heard,
      message: data.message ?? "تم تقييم النطق.",
      engine: data.engine ?? this.name,
    };
  }
}

let cached: PronunciationAssessor | null = null;

export function getAssessor(): PronunciationAssessor {
  if (cached) return cached;
  const url = import.meta.env.VITE_ASSESS_URL as string | undefined;
  cached = url ? new ServerAssessor(url) : new HeuristicAssessor();
  return cached;
}
