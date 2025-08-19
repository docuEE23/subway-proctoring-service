import React, { useState } from "react";
import "../css/login.css"; // mockup 스타일 재사용

const AdminPage = () => {
  // 세션 정보 상태
  const [sessionName, setSessionName] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [aiRules, setAiRules] = useState({
    gaze: true,
    windowSwitch: true,
    forbiddenItem: false,
  });
  const [examParticipants, setExamParticipants] = useState("");

  // API 응답 및 UI 상태
  const [createdSession, setCreatedSession] = useState(null); // 생성된 세션 정보 저장 {id, name, ...}
  const [sessionList, setSessionList] = useState([]); // New state for list of created sessions
  const [selectedSessionDetails, setSelectedSessionDetails] = useState(null); // New state for modal details
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleCheckboxChange = (e) => {
    const { name, checked } = e.target;
    setAiRules((prev) => ({ ...prev, [name]: checked }));
  };

  // 세션 생성 API 호출
  const handleCreateSession = async () => {
    setLoading(true);
    setError("");
    try {
      // Map frontend state to backend CreateSessionRequest model
      const requestBody = {
        exam_title: sessionName,
        proctor_name: "자동 생성 감독관", // Default name for auto-generated proctor
        num_examinees: parseInt(examParticipants, 10), // Convert to number
        detect_rule: {
          detect_gaze_off_screen: aiRules.gaze,
          detect_window_switch: aiRules.windowSwitch,
          detect_prohibited_items: aiRules.forbiddenItem,
          detect_multiple_faces: false, // Assuming default false for now
          detect_audio_noise: false, // Assuming default false for now
        },
        exam_start: new Date(startTime).toISOString(), // Convert to ISO string
        exam_end: new Date(endTime).toISOString(), // Convert to ISO string
        expected_num_examinees: parseInt(examParticipants, 10), // Use examParticipants for this too
      };

      const response = await fetch("/api/v1/session/create_session", {
        // Corrected endpoint
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: 'include', // Send cookies with the request
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "세션 생성에 실패했습니다.");
      }

      const sessionData = await response.json(); // This will be SessionCreationResponse
      setCreatedSession(sessionData); // Store the full response
      setSessionList((prev) => [...prev, sessionData]); // Add to list
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main>
      <header>
        <h1>관리자 대시보드</h1>
      </header>
      <section className="view show">
        <div className="grid cols-2">
          <div className="card">
            <h3>시험 세션 생성 (UC-101 / FS-01-01)</h3>

            <label htmlFor="sessName">세션 이름</label>
            <input
              id="sessName"
              value={sessionName}
              onChange={(e) => setSessionName(e.target.value)}
              placeholder="2025 공개채용 필기 A세션"
            />

            <div className="row">
              <div>
                <label htmlFor="startAt">시작 일시</label>
                <input
                  type="datetime-local"
                  id="startAt"
                  value={startTime}
                  onChange={(e) => setStartTime(e.target.value)}
                />
              </div>
              <div>
                <label htmlFor="endAt">종료 일시</label>
                <input
                  type="datetime-local"
                  id="endAt"
                  value={endTime}
                  onChange={(e) => setEndTime(e.target.value)}
                />
              </div>
            </div>

            <label>AI 감지 규칙</label>
            <div className="row">
              <label
                className={
                  aiRules.gaze
                    ? "ai-rule-checked ai-rule-label"
                    : "ai-rule-label"
                }
              >
                <input
                  type="checkbox"
                  name="gaze"
                  checked={aiRules.gaze}
                  onChange={handleCheckboxChange}
                />{" "}
                시선 이탈
              </label>
              <label
                className={
                  aiRules.windowSwitch
                    ? "ai-rule-checked ai-rule-label"
                    : "ai-rule-label"
                }
              >
                <input
                  type="checkbox"
                  name="windowSwitch"
                  checked={aiRules.windowSwitch}
                  onChange={handleCheckboxChange}
                />{" "}
                창 전환
              </label>
              <label
                className={
                  aiRules.forbiddenItem
                    ? "ai-rule-checked ai-rule-label"
                    : "ai-rule-label"
                }
              >
                <input
                  type="checkbox"
                  name="forbiddenItem"
                  checked={aiRules.forbiddenItem}
                  onChange={handleCheckboxChange}
                />{" "}
                금지 물품
              </label>
            </div>

            {/* New input field for Exam Participants */}
            <label htmlFor="examParticipants">시험 인수</label>
            <input
              id="examParticipants"
              type="number"
              value={examParticipants}
              onChange={(e) => setExamParticipants(e.target.value)}
              placeholder="시험에 참여할 인원수를 입력하세요"
            />

            <div className="row" style={{ marginTop: "10px" }}>
              <button
                className="btn"
                onClick={handleCreateSession}
                disabled={loading}
              >
                {loading ? "생성 중..." : "세션 생성"}
              </button>
            </div>
          </div>
          <div className="card">
            <h3>생성된 세션 목록</h3>
            {error ? (
              <p style={{ color: "red" }}>{error}</p>
            ) : sessionList.length > 0 ? (
              <div className="list">
                {sessionList.map((session) => (
                  <div
                    key={session.session_id}
                    className="item"
                    onClick={() => setSelectedSessionDetails(session)}
                    style={{
                      cursor: "pointer",
                      borderBottom: "1px solid #eee",
                      paddingBottom: "5px",
                      marginBottom: "5px",
                    }}
                  >
                    <span>
                      <b>{session.exam_title}</b> ({session.join_code})
                    </span>
                    <span
                      style={{
                        float: "right",
                        fontSize: "0.8em",
                        color: "#666",
                      }}
                    >
                      클릭하여 상세 보기
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p>새로운 세션을 생성하세요.</p>
            )}
          </div>
        </div>
      </section>

      {selectedSessionDetails && (
        <div className="modal" style={{ display: "flex" }}>
          <div className="panel">
            <header>
              <b>세션 상세 정보</b>
              <button
                className="btn flat"
                onClick={() => setSelectedSessionDetails(null)}
              >
                닫기
              </button>
            </header>
            <div className="content">
              <div className="list">
                <div className="item">
                  <span>
                    세션 제목: <b>{selectedSessionDetails.exam_title}</b>
                  </span>
                </div>
                <div className="item">
                  <span>
                    세션 ID: <b>{selectedSessionDetails.session_id}</b>
                  </span>
                </div>
                <div className="item">
                  <span>
                    참여 코드: <b>{selectedSessionDetails.join_code}</b>
                  </span>
                </div>
                <div className="item">
                  <span>
                    감독관 ID:{" "}
                    <b>{selectedSessionDetails.proctor_credentials.user_id}</b>
                  </span>
                </div>
                <div className="item">
                  <span>
                    감독관 PW:{" "}
                    <b>{selectedSessionDetails.proctor_credentials.password}</b>
                  </span>
                </div>
                <div className="item">
                  <span>응시자 계정:</span>
                </div>
                {selectedSessionDetails.examinee_credentials.map(
                  (cred, index) => (
                    <div
                      key={index}
                      className="item"
                      style={{ marginLeft: "10px" }}
                    >
                      <span>
                        {cred.user_id} / {cred.password}
                      </span>
                    </div>
                  )
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </main>
  );
};

export default AdminPage;
