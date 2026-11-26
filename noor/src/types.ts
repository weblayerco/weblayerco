export type Harakah = "fatha" | "damma" | "kasra";

export interface HarakahInfo {
  id: Harakah;
  /** combining diacritic mark */
  mark: string;
  /** Arabic name e.g. "فَتْحَة" */
  name: string;
  /** short sound hint e.g. "اَ" */
  sound: string;
}

export interface Letter {
  id: string;
  /** isolated glyph, e.g. "ط" */
  char: string;
  /** spoken name, e.g. "طاء" */
  name: string;
  /** true for the emphatic / pharyngeal letters that are hard for non-natives */
  hard?: boolean;
  /** short articulation tip (مخرج) shown to the parent/child */
  tip?: string;
}

export type PhaseId = "letters" | "qaida" | "quran";

export interface Phase {
  id: PhaseId;
  title: string;
  subtitle: string;
  /** whether the learning content is implemented yet */
  available: boolean;
}

/** A single thing the child must pronounce correctly to advance. */
export interface Step {
  letterId: string;
  harakah: Harakah;
}

export interface AssessmentResult {
  /** did it pass the gate */
  pass: boolean;
  /** 0..1 confidence from the engine, when available */
  score?: number;
  /** what the recognizer thought it heard, when available */
  heard?: string;
  /** human-readable message in Arabic */
  message: string;
  /** which engine produced this result */
  engine: string;
}
