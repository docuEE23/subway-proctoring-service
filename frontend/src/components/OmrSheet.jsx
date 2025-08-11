import React from "react";

const OmrSheet = ({
  totalQuestions,
  answers,
  onAnswerChange,
  onJumpToQuestion,
}) => {
  const checkUnanswered = () => {
    const unanswered = [];
    for (let i = 1; i <= totalQuestions; i++) {
      if (!answers[i]) unanswered.push(i);
    }
    if (unanswered.length === 0) alert("모든 문항에 답변했습니다");
    else alert(`미답안: ${unanswered.join(", ")} 번`);
  };

  const handleSubmit = () => {
    // TODO: API로 답안 제출
    alert("답안이 제출되었습니다.");
  };

  return (
    <div className="card">
      <h3>OMR 답안지</h3>
      <div className="omr">
        {Array.from({ length: totalQuestions }).map((_, i) => {
          const qNum = i + 1;
          return (
            <div key={qNum} className="bubble-omr">
              <div
                className="muted"
                style={{ textAlign: "center", cursor: "pointer" }}
                onClick={() => onJumpToQuestion(qNum)}
              >
                {qNum}
              </div>
              {["A", "B", "C", "D", "E"].map((letter) => (
                <label key={letter}>
                  <input
                    type="radio"
                    name={`q${qNum}`}
                    value={letter}
                    checked={answers[qNum] === letter}
                    onChange={() => onAnswerChange(qNum, letter)}
                  />
                  <span>{letter}</span>
                </label>
              ))}
            </div>
          );
        })}
      </div>
      <div className="submit-area">
        <div className="row">
          <button className="btn warn" onClick={checkUnanswered}>
            미답안 확인
          </button>
          <button className="btn danger" onClick={handleSubmit}>
            최종 답안 제출
          </button>
        </div>
      </div>
    </div>
  );
};

export default OmrSheet;
