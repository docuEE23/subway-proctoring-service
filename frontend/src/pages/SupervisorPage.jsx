import React, { useState, useEffect, useCallback } from "react";
import { Navigate, useLocation } from "react-router-dom"; // Added Navigate, useLocation
import "../css/login.css"; // mockup 스타일 재사용
import WebcamViewer from "../components/WebcamViewer";
import useWebRTC from "../hooks/useWebRTC"; // useWebRTC 훅 import
import signaling from "../services/signaling";


import { useAuth } from "../contexts/AuthContext";

const SupervisorPage = () => {
  const location = useLocation();
  const { user } = useAuth();
  const token = localStorage.getItem("token");
  const [sessions, setSessions] = useState([]); // New state
  const [selectedSessionId, setSelectedSessionId] = useState(null); // New state
  const [participants, setParticipants] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatHistory, setChatHistory] = useState({});
  const [chatInput, setChatInput] = useState("");

  const examId = selectedSessionId; // Use selectedSessionId as examId

  useEffect(() => {
    const fetchMySessions = async () => {
      try {
        const response = await fetch('/api/v1/sessions/my_sessions');
        if (!response.ok) {
          throw new Error('Failed to fetch sessions');
        }
        const data = await response.json();
        setSessions(data);
        if (data.length > 0) {
          setSelectedSessionId(data[0].session_id); // Auto-select first session
        }
      } catch (error) {
        console.error('Error fetching my sessions:', error);
        // Handle error, e.g., show a toast
      }
    };

    if (user) { // Fetch sessions only if user is logged in
      fetchMySessions();
    }
  }, [user]); // Re-fetch if user changes

  // Callback for receiving messages from useWebRTC
  const handleMessageReceived = useCallback((message) => {
    if (message.type === 'message' && message.content && message.from) {
      setChatHistory((prev) => ({
        ...prev,
        [message.from]: [...(prev[message.from] || []), { who: "them", text: `응시자 (${message.from}): ${message.content}` }],
      }));
    }
  }, [setChatHistory]);

  // --- WebRTC Hook ---
  // 감독관은 자신의 비디오를 보내지 않으므로 localStream은 사용하지 않습니다.
  const {
    remoteStreams,
    createPeerConnection,
    handleAnswer,
    handleIceCandidate,
  } = useWebRTC(examId, token, handleMessageReceived);

  

  // 컴포넌트 마운트 시 모의 데이터 로드
  useEffect(() => {
    if (!selectedSessionId) return; // Only fetch if a session is selected

    const fetchParticipants = async () => {
      try {
        const response = await fetch(`/api/v1/exams/${examId}/participants`);
        const data = await response.json();
        setParticipants(data);
      } catch (error) {
        console.error("Error fetching participants:", error);
      }
    };

    const fetchAlerts = async () => {
      try {
        const response = await fetch(`/api/v1/exams/${examId}/alerts`);
        const data = await response.json();
        setAlerts(data);
      } catch (error) {
        console.error("Error fetching alerts:", error);
      }
    };

    fetchParticipants();
    fetchAlerts();
  }, [selectedSessionId]);

  // --- WebRTC 연결 설정 Effect ---
  useEffect(() => {
    if (participants.length === 0) return;

    // 각 응시자에 대해 WebRTC 연결 시작
    participants.forEach((user) => {
      // PeerConnection 생성 (이때 localStream은 null 또는 빈 스트림이어야 함)
      const pc = createPeerConnection(user.id, new MediaStream()); // 감독관은 스트림을 보내지 않음

      // Offer 생성
      pc.createOffer()
        .then((offer) => pc.setLocalDescription(offer))
        .then(() => {
          console.log(`Sending offer to ${user.name}:`, pc.localDescription);
          signaling.send({
            type: "offer",
            to: user.id,
            sdp: pc.localDescription,
          });
        })
        .catch((err) =>
          console.error(`Error creating offer for ${user.name}:`, err)
        );
    });
  }, [participants, createPeerConnection, handleAnswer, handleIceCandidate]);

  // 사용자 선택 (확대 보기)
  const handleSelectUser = (user) => {
    setSelectedUser(user);
  };

  // 채팅 모달 열기
  const handleOpenChat = (user) => {
    setSelectedUser(user);
    if (!chatHistory[user.id]) {
      setChatHistory((prev) => ({ ...prev, [user.id]: [] }));
    }
    setIsChatOpen(true);
  };

  // 채팅 메시지 전송
  const handleSendChat = () => {
    if (!chatInput.trim() || !selectedUser) return;

    // Send message via WebSocket
    signaling.send({
      type: 'message',
      content: chatInput,
      to: selectedUser.id, // Send to the selected examinee
    });

    const newMessage = {
      who: "supervisor",
      text: chatInput,
      time: new Date().toLocaleTimeString(),
    };

    setChatHistory((prev) => ({
      ...prev,
      [selectedUser.id]: [...(prev[selectedUser.id] || []), newMessage],
    }));
    setChatInput("");
  };

  // Redirect if not authenticated
  if (!user) {
    return <Navigate to="/login" />;
  }

  return (
    <main>
      {selectedSessionId ? (
        <>
          <div className="split">
            <div>
              <div className="toolbar">
                <input placeholder="응시자 검색" />
                <select>
                  <option value="all">전체</option>
                  <option value="alert">알림 있음</option>
                </select>
                <div className="pill">{participants.length}명 표시</div>
              </div>
              <div id="grid" className="grid cols-4">
                {participants.map((p) => (
                  <div className="card" key={p.id}>
                    <div
                      className="row"
                      style={{ justifyContent: "space-between" }}
                    >
                      <b>{p.name}</b>
                      <span className={`badge ${p.alerts > 0 ? "danger" : ""}`}>
                        {p.status}
                        {p.alerts > 0 ? ` · 알림 ${p.alerts}` : ""}
                      </span>
                    </div>
                    {/* 웹캠 영상: remoteStreams에서 해당 유저의 스트림을 찾아 WebcamViewer에 전달 */}
                    <div className="video" style={{ marginTop: "8px" }}>
                      <WebcamViewer stream={remoteStreams[p.id]} />
                    </div>
                    <div className="video" style={{ marginTop: "8px" }}></div>{" "}
                    {/* 손캠 영상 (추후 구현) */}
                    <div className="row" style={{ marginTop: "8px" }}>
                      <button
                        className="btn flat"
                        onClick={() => handleSelectUser(p)}
                      >
                        확대
                      </button>
                      <button
                        className="btn flat"
                        onClick={() => handleOpenChat(p)}
                      >
                        메시지
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <div className="card">
                <h3>AI 알림 (UC-501)</h3>
                <div className="list">
                  {alerts.map((a) => (
                    <div className="item" key={a.id}>
                      <span>
                        <b>{a.userName}</b> – {a.type}
                      </span>
                      <span className="muted">{a.time}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* --- 선택 응시자 (확대 보기) --- */}
          {selectedUser && (
            <div className="card" style={{ marginTop: "14px" }}>
              <h3>선택 응시자: {selectedUser.name}</h3>
              {/* 확대 보기 영상 */}
              <div className="video rel" style={{ height: "320px" }}>
                <WebcamViewer stream={remoteStreams[selectedUser.id]} />
              </div>
              <div className="row" style={{ marginTop: "8px" }}>
                <button
                  className="btn secondary"
                  onClick={() => alert("스냅샷 저장 (API 연동 필요)")}
                >
                  스냅샷(증거)
                </button>
                <button
                  className="btn"
                  onClick={() => handleOpenChat(selectedUser)}
                >
                  1:1 메시지
                </button>
                <button className="btn flat" onClick={() => setSelectedUser(null)}>
                  닫기
                </button>
              </div>
            </div>
          )}

          {/* --- 1:1 채팅 모달 --- */}
          {isChatOpen && selectedUser && (
            <div className="modal" style={{ display: "flex" }}>
              <div className="panel">
                <header>
                  <b>메시지 – {selectedUser.name}</b>
                  <button className="btn flat" onClick={() => setIsChatOpen(false)}>
                    닫기
                  </button>
                </header>
                <div className="content">
                  <div className="chat" style={{ minHeight: "220px" }}>
                    {(chatHistory[selectedUser.id] || []).map((msg, i) => (
                      <div
                        key={i}
                        className={`bubble ${
                          msg.who === "supervisor" ? "you" : "them"
                        }`}
                      >
                        {msg.text}
                      </div>
                    ))}
                  </div>
                  <div className="row" style={{ marginTop: "10px" }}>
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
              </div>
            </div>
          )}
        </>
      ) : (
        <p>할당된 세션이 없습니다.</p>
      )}
    </main>
  );
};

export default SupervisorPage;
