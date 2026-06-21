import { useState } from "react";
import { HomeScreen } from "./screens/HomeScreen";
import { LearnScreen } from "./screens/LearnScreen";
import { loadCompleted, resetProgress, saveCompleted } from "./services/progress";

type Screen = "home" | "learn";

export default function App() {
  const [screen, setScreen] = useState<Screen>("home");
  const [done, setDone] = useState<Set<string>>(() => loadCompleted());

  function completeStep(stepK: string) {
    setDone((prev) => {
      const next = new Set(prev);
      next.add(stepK);
      saveCompleted(next);
      return next;
    });
  }

  function handleReset() {
    if (!confirm("هل تريد إعادة ضبط كل التقدّم؟")) return;
    resetProgress();
    setDone(new Set());
    setScreen("home");
  }

  return (
    <div className="app">
      <div className="topbar">
        <div className="brand">
          <div className="logo">ن</div>
          <div>
            <h1>نور</h1>
            <p>تعلّم نطق الحروف العربية</p>
          </div>
        </div>
        {screen === "learn" ? (
          <button className="linkbtn" onClick={() => setScreen("home")}>
            ← الرئيسية
          </button>
        ) : (
          <button className="linkbtn" onClick={handleReset}>
            إعادة الضبط
          </button>
        )}
      </div>

      {screen === "home" ? (
        <HomeScreen done={done} onStart={() => setScreen("learn")} />
      ) : (
        <LearnScreen done={done} onComplete={completeStep} />
      )}
    </div>
  );
}
