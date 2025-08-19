import React, { useState, useEffect } from 'react';
import '../css/login.css'; // mockup 스타일 재사용

// --- 모의 데이터 (나중에 API로 대체) ---
const MOCK_PARTICIPANTS = Array.from({ length: 12 }).map((_, i) => ({
  id: `user_${i + 1}`,
  name: `응시자 ${String(i + 1).padStart(2, '0')}`,
  status: i % 3 === 0 ? '대기' : (i % 3 === 1 ? '시험 중' : '알림'),
  alerts: i % 4 === 0 ? 1 : 0,
}));

const MOCK_ALERTS = [
  { id: 1, userId: 'user_4', userName: '응시자 04', type: '시선 이탈', time: '14:32:10' },
  { id: 2, userId: 'user_8', userName: '응시자 08', type: '금지 물품', time: '14:32:55' },
];
// -------------------------------------

const SupervisorPage = () => {
  const [participants, setParticipants] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatHistory, setChatHistory] = useState({}); // { userId: [{...messages}] }
  const [chatInput, setChatInput] = useState('');

  // 컴포넌트 마운트 시 모의 데이터 로드 (API 호출 시뮬레이션)
  useEffect(() => {
    // TODO: API 호출로 실제 데이터 가져오기
    // fetch('/api/v1/sessions/{sessionId}/participants').then(res => res.json()).then(setParticipants);
    // fetch('/api/v1/sessions/{sessionId}/alerts').then(res => res.json()).then(setAlerts);
    setParticipants(MOCK_PARTICIPANTS);
    setAlerts(MOCK_ALERTS);
  }, []);

  // 사용자 선택 (확대 보기)
  const handleSelectUser = (user) => {
    setSelectedUser(user);
  };

  // 채팅 모달 열기
  const handleOpenChat = (user) => {
    setSelectedUser(user);
    if (!chatHistory[user.id]) {
      // 채팅 기록이 없으면 초기화 (나중에 API로 가져올 부분)
      setChatHistory(prev => ({ ...prev, [user.id]: [] }));
    }
    setIsChatOpen(true);
  };

  // 채팅 메시지 전송
  const handleSendChat = () => {
    if (!chatInput.trim() || !selectedUser) return;
    const newMessage = { who: 'supervisor', text: chatInput, time: new Date().toLocaleTimeString() };
    
    // TODO: API로 메시지 전송
    // fetch(`/api/v1/chat/${selectedUser.id}`, { method: 'POST', body: JSON.stringify({text: chatInput}) });

    setChatHistory(prev => ({
      ...prev,
      [selectedUser.id]: [...(prev[selectedUser.id] || []), newMessage]
    }));
    setChatInput('');
  };

  return (
    <main>
      {/* --- 감독관 대시보드 (그리드 뷰) --- */}
      <div className="split">
        <div>
          <div className="toolbar">
            <input placeholder="응시자 검색"/>
            <select><option value="all">전체</option><option value="alert">알림 있음</option></select>
            <div className="pill">{participants.length}명 표시</div>
          </div>
          <div id="grid" className="grid cols-4">
            {participants.map(p => (
              <div className="card" key={p.id}>
                <div className="row" style={{ justifyContent: 'space-between' }}>
                  <b>{p.name}</b>
                  <span className={`badge ${p.alerts > 0 ? 'danger' : ''}`}>{p.status}{p.alerts > 0 ? ` · 알림 ${p.alerts}`: ''}</span>
                </div>
                <div className="video" style={{ marginTop: '8px' }}></div> {/* 웹캠 영상 */}
                <div className="video" style={{ marginTop: '8px' }}></div> {/* 손캠 영상 */}
                <div className="row" style={{ marginTop: '8px' }}>
                  <button className="btn flat" onClick={() => handleSelectUser(p)}>확대</button>
                  <button className="btn flat" onClick={() => handleOpenChat(p)}>메시지</button>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div>
          <div className="card"><h3>AI 알림 (UC-501)</h3><div className="list">{alerts.map(a => <div className="item" key={a.id}><span><b>{a.userName}</b> – {a.type}</span><span className="muted">{a.time}</span></div>)}</div></div>
        </div>
      </div>

      {/* --- 선택 응시자 (확대 보기) --- */}
      {selectedUser && (
        <div className="card" style={{ marginTop: '14px' }}>
          <h3>선택 응시자: {selectedUser.name}</h3>
          <div className="video rel" style={{height: '320px'}}></div>
          <div className="row" style={{ marginTop: '8px' }}>
            <button className="btn secondary" onClick={() => alert('스냅샷 저장 (API 연동 필요)')}>스냅샷(증거)</button>
            <button className="btn" onClick={() => handleOpenChat(selectedUser)}>1:1 메시지</button>
            <button className="btn flat" onClick={() => setSelectedUser(null)}>닫기</button>
          </div>
        </div>
      )}

      {/* --- 1:1 채팅 모달 --- */}
      {isChatOpen && selectedUser && (
        <div className="modal" style={{ display: 'flex' }}>
          <div className="panel">
            <header><b>메시지 – {selectedUser.name}</b><button className="btn flat" onClick={() => setIsChatOpen(false)}>닫기</button></header>
            <div className="content">
              <div className="chat" style={{ minHeight: '220px' }}>
                {(chatHistory[selectedUser.id] || []).map((msg, i) => (
                  <div key={i} className={`bubble ${msg.who === 'supervisor' ? 'you' : 'them'}`}>{msg.text}</div>
                ))}
              </div>
              <div className="row" style={{ marginTop: '10px' }}>
                <input placeholder="메시지를 입력하세요" value={chatInput} onChange={(e) => setChatInput(e.target.value)} />
                <button className="btn" onClick={handleSendChat}>전송</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </main>
  );
};

export default SupervisorPage;
