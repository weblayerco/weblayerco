import type { Step } from "../types";
import { HARAKAT, LETTERS } from "../data/curriculum";

const STORAGE_KEY = "noor.progress.letters.v1";

/** The full ordered list of gated steps for the letters phase. */
export const LETTER_STEPS: Step[] = LETTERS.flatMap((letter) =>
  HARAKAT.map((h) => ({ letterId: letter.id, harakah: h.id })),
);

export function stepKey(step: Step): string {
  return `${step.letterId}:${step.harakah}`;
}

export function loadCompleted(): Set<string> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return new Set();
    return new Set(JSON.parse(raw) as string[]);
  } catch {
    return new Set();
  }
}

export function saveCompleted(done: Set<string>): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify([...done]));
}

export function resetProgress(): void {
  localStorage.removeItem(STORAGE_KEY);
}

/** Index of the first step the child has not yet completed (the active step). */
export function currentStepIndex(done: Set<string>): number {
  const idx = LETTER_STEPS.findIndex((s) => !done.has(stepKey(s)));
  return idx === -1 ? LETTER_STEPS.length : idx;
}

/** Linear gating: a step is unlocked only when every earlier step is done. */
export function isStepUnlocked(index: number, done: Set<string>): boolean {
  return index <= currentStepIndex(done);
}

export type LetterStatus = "locked" | "active" | "done";

export function letterStatus(letterId: string, done: Set<string>): LetterStatus {
  const steps = LETTER_STEPS.filter((s) => s.letterId === letterId);
  const allDone = steps.every((s) => done.has(stepKey(s)));
  if (allDone) return "done";
  const firstIdx = LETTER_STEPS.findIndex((s) => s.letterId === letterId);
  return isStepUnlocked(firstIdx, done) ? "active" : "locked";
}
