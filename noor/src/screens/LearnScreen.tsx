import { useRef, useState } from "react";
import type { AssessmentResult } from "../types";
import { applyHarakah, harakahById, letterById } from "../data/curriculum";
import {
  LETTER_STEPS,
  currentStepIndex,
  stepKey,
} from "../services/progress";
import { AudioRecorder, isRecordingSupported, type Recording } from "../services/recorder";
import { getAssessor } from "../services/assessment";
import { speakArabic } from "../services/speak";
import { LetterGrid } from "../components/LetterGrid";

type Status = "idle" | "recording" | "assessing" | "recorded";

export function LearnScreen({
  done,
  onComplete,
}: {
  done: Set<string>;
  onComplete: (stepK: string) => void;
}) {
  const recorderRef = useRef<AudioRecorder | null>(null);
  const lastRec = useRef<Recording | null>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const index = currentStepIndex(done);
  const finished = index >= LETTER_STEPS.length;

  if (finished) {
    return (
      <div className="done-screen card">
        <div className="big">🎉</div>
        <h2>أتممت كل الحروف!</h2>
        <p className="psub">
          أحسنت! المرحلة التالية هي «القاعدة النورانية» (قريباً بإذن الله).
        </p>
      </div>
    );
  }

  const step = LETTER_STEPS[index];
  const letter = letterById(step.letterId);
  const harakah = harakahById(step.harakah);
  const glyph = applyHarakah(letter, harakah);
  const total = LETTER_STEPS.length;
  const pct = Math.round((index / total) * 100);

  function clearAttempt() {
    if (lastRec.current) {
      URL.revokeObjectURL(lastRec.current.url);
      lastRec.current = null;
    }
    setResult(null);
    setError(null);
  }

  async function toggleRecord() {
    setError(null);
    if (status === "recording") {
      try {
        const rec = await recorderRef.current!.stop();
        lastRec.current = rec;
        setStatus("assessing");
        const res = await getAssessor().assess({
          letter,
          harakah,
          recordingBlob: rec.blob,
        });
        setResult(res);
        setStatus("recorded");
      } catch (e) {
        setError((e as Error).message);
        setStatus("idle");
      }
      return;
    }
    try {
      clearAttempt();
      recorderRef.current = new AudioRecorder();
      await recorderRef.current.start();
      setStatus("recording");
    } catch {
      setError("لا يمكن الوصول إلى الميكروفون. تأكد من منح الإذن.");
      setStatus("idle");
    }
  }

  function playAttempt() {
    if (lastRec.current) new Audio(lastRec.current.url).play();
  }

  function pass() {
    clearAttempt();
    setStatus("idle");
    onComplete(stepKey(step));
  }

  function retry() {
    clearAttempt();
    setStatus("idle");
  }

  return (
    <div>
      <div className="progress-wrap">
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${pct}%` }} />
        </div>
        <div className="progress-label">
          الحرف {index + 1} من {total} · {pct}%
        </div>
      </div>

      <div className="card">
        <p className="harakah-name">
          {letter.name} مع {harakah.name}
        </p>
        <div className={`glyph ${letter.hard ? "hard" : ""}`}>{glyph}</div>
        <p className="letter-name">انطق: «{glyph}»</p>

        {letter.hard && letter.tip && <div className="tip">💡 {letter.tip}</div>}

        <div className="controls">
          <button className="iconbtn play" onClick={() => speakArabic(glyph)}>
            🔊 استمع للنموذج
          </button>
          {status === "recorded" && (
            <button className="iconbtn ghost" onClick={playAttempt}>
              ▶️ محاولتك
            </button>
          )}
        </div>

        {!isRecordingSupported() ? (
          <div className="feedback bad">
            هذا المتصفح لا يدعم تسجيل الصوت. جرّب متصفحاً حديثاً (Chrome/Safari).
          </div>
        ) : (
          <>
            <button
              className={`mic ${status === "recording" ? "recording" : ""}`}
              onClick={toggleRecord}
              disabled={status === "assessing"}
              aria-label="تسجيل"
            >
              {status === "recording" ? "■" : "🎙️"}
            </button>
            <p className="mic-hint">
              {status === "recording"
                ? "جارٍ التسجيل… اضغط للإيقاف"
                : status === "assessing"
                  ? "جارٍ التحليل…"
                  : "اضغط وانطق الحرف"}
            </p>
          </>
        )}

        {error && <div className="feedback bad">{error}</div>}

        {result && (
          <>
            <div className={`feedback ${result.pass ? "ok" : "bad"}`}>
              {result.message}
            </div>
            {result.pass ? (
              <>
                <div className="confirm-row">
                  <button className="btn-pass" onClick={pass}>
                    أحسنت ✓ التالي
                  </button>
                  <button className="btn-retry" onClick={retry}>
                    نُعيد
                  </button>
                </div>
                <p className="parent-note">
                  ملاحظة لوليّ الأمر: استمع لمحاولة الطفل وأكِّد صحة النطق قبل الانتقال.
                  (التقييم التلقائي الدقيق للمخارج يُضاف عبر محرّك الذكاء الاصطناعي.)
                </p>
              </>
            ) : (
              <div className="confirm-row">
                <button className="btn-retry" onClick={retry}>
                  حاول مرة أخرى
                </button>
              </div>
            )}
          </>
        )}
      </div>

      <LetterGrid done={done} />
    </div>
  );
}
