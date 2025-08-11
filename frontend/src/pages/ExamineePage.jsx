import React, { useState, useEffect, useRef } from "react";
import "../css/ExamineePage.css";
import WebcamViewer from "../components/WebcamViewer";

// --- Mock Data ---
const MOCK_QUESTIONS = Array.from({ length: 30 }).map((_, i) => ({
  id: `q${i + 1}`,
  text: `문제 ${i + 1}: 다음 중 프로그래밍 언어가 아닌 것은?`,
  options: ["Java", "Python", "C++", "HTML", "JavaScript"],
}));

const ExamineePage = () => {
  // --- State Variables ---
  const [questions] = useState(MOCK_QUESTIONS);
  const [currentQ, setCurrentQ] = useState(1);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(120 * 60);
  const [chatHistory, setChatHistory] = useState([
    { who: "them", text: "감독관: 입실 후 신분증 준비해주세요." },
    { who: "you", text: "응시자: 네, 준비했습니다." },
  ]);
  const [chatInput, setChatInput] = useState("");
  const [toast, setToast] = useState({ show: false, message: "" });
  const [webcamStream, setWebcamStream] = useState(null); // New state for webcam stream

  const chatListRef = useRef(null);

  // --- Timer Effect ---
  useEffect(() => {
    const timer = setInterval(
      () => setTimeLeft((prev) => (prev > 0 ? prev - 1 : 0)),
      1000
    );
    return () => clearInterval(timer);
  }, []);

  // --- Chat Scroll Effect ---
  useEffect(() => {
    if (chatListRef.current) {
      chatListRef.current.scrollTop = chatListRef.current.scrollHeight;
    }
  }, [chatHistory]);

  // --- Webcam Effect ---
  useEffect(() => {
    let currentStream; // Declare a variable to hold the stream for cleanup

    const startWebcam = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
        });
        setWebcamStream(stream);
        currentStream = stream; // Store the stream for cleanup
      } catch (err) {
        console.error("Error accessing webcam:", err);
        showToast("웹캠 접근에 실패했습니다. 권한을 허용해주세요.");
      }
    };

    startWebcam();

    // Cleanup: stop webcam stream when component unmounts
    return () => {
      if (currentStream) {
        // Use the stream from the closure
        currentStream.getTracks().forEach((track) => track.stop());
      }
    };
  }, []); // Empty dependency array: runs only once on mount

  // --- Utility Functions ---
  const formatTime = (seconds) => {
    const m = String(Math.floor(seconds / 60)).padStart(2, "0");
    const s = String(seconds % 60).padStart(2, "0");
    return `남은시간 ${m}:${s}`;
  };

  const showToast = (message) => {
    setToast({ show: true, message });
    setTimeout(() => setToast({ show: false, message: "" }), 1800);
  };

  // --- Event Handlers ---
  const handleAnswerChange = (qNumber, answer) => {
    setAnswers((prev) => ({ ...prev, [qNumber]: answer }));
  };

  const handleSendChat = () => {
    if (!chatInput.trim()) {
      showToast("메시지를 입력하세요");
      return;
    }
    setChatHistory((prev) => [
      ...prev,
      { who: "you", text: `응시자: ${chatInput}` },
    ]);
    setChatInput("");
  };

  const handleReviewAnswers = () => {
    const unanswered = [];
    for (let i = 1; i <= questions.length; i++) {
      if (!answers[i]) unanswered.push(i);
    }
    if (unanswered.length === 0) {
      showToast("모든 문항에 답변했습니다");
    } else {
      showToast(
        `미답안: ${unanswered.slice(0, 10).join(", ")}${
          unanswered.length > 10 ? " 외 ..." : ""
        }`
      );
    }
  };

  const handleSubmit = () => {
    handleReviewAnswers();
    setTimeout(() => showToast("제출 완료 감독관에게 전송되었습니다"), 600);
  };

  const prevQ = () => {
    const newQ = Math.max(1, currentQ - 1);
    setCurrentQ(newQ);
    showToast(`문항 ${newQ}`);
  };

  const nextQ = () => {
    const newQ = Math.min(questions.length, currentQ + 1);
    setCurrentQ(newQ);
    showToast(`문항 ${newQ}`);
  };

  // --- JSX ---
  return (
    <div className="app">
      {/* Sticky Examinee Banner */}
      <div className="exam-banner" role="region" aria-label="시험/세션 정보">
        <div className="exam-title">2025 공개채용 필기 – 코딩테스트</div>
        <div className="kv">
          <div className="chip">
            세션: <b>A세션</b>
          </div>
          <div className="chip">
            응시자: <b>홍길동</b>
          </div>
          <div className="chip">
            세션코드: <b>ABCD-1234</b>
          </div>
          <div className="chip">
            시작: <b>2025-09-01 10:00</b>
          </div>
          <div className="chip">
            종료: <b>12:00</b>
          </div>
        </div>
        <div className="pill">{formatTime(timeLeft)}</div>
      </div>

      {/* 3-Column Examinee Board */}
      <div className="layout">
        {/* LEFT: Self cams + chat */}
        <section className="col" aria-label="응시자 모니터링 보드">
          <div className="card">
            <h3>내 웹캠</h3>
            <div className="video">
              <WebcamViewer stream={webcamStream} />
            </div>
            <div className="row">
              <button
                className="btn secondary"
                onClick={() =>
                  showToast("신원 확인을 시작합니다. 감독관이 확인합니다.")
                }
              >
                신원 확인
              </button>
              <button
                className="btn secondary"
                onClick={() =>
                  showToast("주변 확인을 시작합니다. 휴대폰 연결이 필요합니다.")
                }
              >
                주변 확인
              </button>
            </div>
          </div>
          <div className="card">
            <h3>보조 카메라(모바일)</h3>
            <div className="video"></div>
            <div className="hint">QR로 모바일 연결 후 책상/주변 시야 확보</div>
          </div>
          <div className="card">
            <h3>감독관 메시지</h3>
            <div ref={chatListRef} className="chat" aria-live="polite">
              {chatHistory.map((msg, i) => (
                <div key={i} className={`bubble ${msg.who}`}>
                  {msg.text}
                </div>
              ))}
            </div>
            <div className="row" style={{ marginTop: "8px" }}>
              <input
                placeholder="메시지를 입력하세요"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
              />
              <button className="btn" onClick={handleSendChat}>
                전송
              </button>
            </div>
          </div>
        </section>

        {/* CENTER: Questions */}
        <section className="col" aria-label="문제 영역">
          <div className="card q-card">
            <div className="q-head">
              <b>
                문항 {currentQ}/{questions.length}
              </b>
              <div className="row q-nav-buttons" style={{ flex: "0 0 auto" }}>
                <button className="btn secondary" onClick={prevQ}>
                  이전
                </button>
                <button className="btn secondary" onClick={nextQ}>
                  다음
                </button>
              </div>
            </div>
            <div>
              <p className="muted">{questions[currentQ - 1].text}</p>
              {questions[currentQ - 1].options.map((opt, i) => (
                <div className="opt" key={i}>
                  <input
                    type="radio"
                    name={`q${currentQ}`}
                    id={`q${currentQ}o${i}`}
                    value={String.fromCharCode(65 + i)}
                    checked={answers[currentQ] === String.fromCharCode(65 + i)}
                    onChange={() =>
                      handleAnswerChange(currentQ, String.fromCharCode(65 + i))
                    }
                  />
                  <label htmlFor={`q${currentQ}o${i}`}>
                    <b>{String.fromCharCode(65 + i)}.</b> {opt}
                  </label>
                </div>
              ))}
            </div>
          </div>
          <div className="card q-card">
            <div className="q-head">
              <b>유의사항</b>
              <span className="muted">부정행위 시 감점/시험 중단</span>
            </div>
            <ul className="muted" style={{ margin: "0 0 4px 18px" }}>
              <li>시험 중 탭 전환/창 최소화 금지</li>
              <li>감독관 메시지 수신 확인 필수</li>
              <li>최종 제출 전 OMR 선택 상태 확인</li>
            </ul>
          </div>
        </section>

        {/* RIGHT: OMR + Final Submit */}
        <section className="col" aria-label="OMR 및 제출">
          <div className="card">
            <h3>OMR 답안지</h3>
            <div className="omr" aria-live="polite">
              {questions.map((q, i) => {
                const qNum = i + 1;
                return (
                  <div key={qNum} className="bubble-omr">
                    <div
                      className="muted"
                      style={{ textAlign: "center", cursor: "pointer" }}
                      onClick={() => setCurrentQ(qNum)}
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
                          onChange={() => handleAnswerChange(qNum, letter)}
                        />
                        <span>{letter}</span>
                      </label>
                    ))}
                  </div>
                );
              })}
            </div>
            <div className="submit-area" aria-label="최종 제출 영역">
              <div className="row">
                <button className="btn warn" onClick={handleReviewAnswers}>
                  미답안 확인
                </button>
                <button className="btn danger" onClick={handleSubmit}>
                  최종 답안 제출
                </button>
              </div>
              <div className="hint" style={{ marginTop: "6px" }}>
                제출 후 수정 불가. 네트워크 안정 상태 확인 후 제출하세요.
              </div>
            </div>
          </div>
        </section>
      </div>

      {toast.show && (
        <div className="toast" style={{ display: "block" }}>
          {toast.message}
        </div>
      )}
    </div>
  );
};

export default ExamineePage;
