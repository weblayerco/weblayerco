import { PHASES } from "../data/curriculum";
import { LETTER_STEPS, currentStepIndex } from "../services/progress";

export function HomeScreen({
  done,
  onStart,
}: {
  done: Set<string>;
  onStart: () => void;
}) {
  const index = currentStepIndex(done);
  const started = index > 0;
  const total = LETTER_STEPS.length;

  return (
    <div>
      <div className="phase-list">
        {PHASES.map((phase) => (
          <div key={phase.id} className={`phase ${phase.available ? "" : "locked"}`}>
            <div>
              <p className="ptitle">{phase.title}</p>
              <p className="psub">{phase.subtitle}</p>
              {phase.id === "letters" && (
                <p className="psub" style={{ marginTop: 6 }}>
                  {index} / {total} خطوة مكتملة
                </p>
              )}
            </div>
            {phase.available ? (
              <button className="startbtn" onClick={onStart}>
                {started ? "متابعة" : "ابدأ"}
              </button>
            ) : (
              <span className="badge soon">قريباً</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
