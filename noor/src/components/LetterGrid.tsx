import { LETTERS } from "../data/curriculum";
import { letterStatus } from "../services/progress";

export function LetterGrid({ done }: { done: Set<string> }) {
  return (
    <>
      <p className="grid-title">خريطة التقدّم</p>
      <div className="letter-grid">
        {LETTERS.map((letter) => {
          const status = letterStatus(letter.id, done);
          return (
            <div key={letter.id} className={`cell ${status}`} title={letter.name}>
              {letter.char}
              {status === "locked" && <span className="lock">🔒</span>}
            </div>
          );
        })}
      </div>
    </>
  );
}
