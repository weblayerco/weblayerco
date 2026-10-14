import type { AssessmentResult, HarakahInfo, Letter } from "../types";
import { applyHarakah } from "../data/curriculum";
import { blobToWav } from "./wav";

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

/**
 * Default, fully-local assessor. There is no real AI in this offline mode, so
 * we don't try to judge correctness — we just hand control to the parent, who
 * listens to the child's attempt and decides. (Hooking up a real AI engine is
 * what ServerAssessor / the deployed backend is for.)
 */
export class HeuristicAssessor implements PronunciationAssessor {
  readonly name = "heuristic";

  async assess(target: AssessTarget): Promise<AssessmentResult> {
    const glyph = applyHarakah(target.letter, target.harakah);
    return {
      pass: true,
      score: 1,
      message: `استمع لمحاولة طفلك لنطق «${glyph}». إن كان النطق صحيحاً اضغط «نعم، صحيح» لينتقل إلى الحرف التالي.`,
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
    const wav = await blobToWav(target.recordingBlob);
    const form = new FormData();
    form.append("audio", wav, "attempt.wav");
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
