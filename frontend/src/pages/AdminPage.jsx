import React, { useState } from 'react';
import '../css/login.css'; // mockup 스타일 재사용

const AdminPage = () => {
  // 세션 정보 상태
  const [sessionName, setSessionName] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [aiRules, setAiRules] = useState({
    gaze: true,
    windowSwitch: true,
    forbiddenItem: false,
  });
  const [examParticipants, setExamParticipants] = useState('');

  // API 응답 및 UI 상태
  const [createdSession, setCreatedSession] = useState(null); // 생성된 세션 정보 저장 {id, name, ...}
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleCheckboxChange = (e) => {
    const { name, checked } = e.target;
    setAiRules((prev) => ({ ...prev, [name]: checked }));
  };

  // 세션 생성 API 호출
  const handleCreateSession = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch('/api/v1/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          name: sessionName,
          start_time: startTime,
          end_time: endTime,
          ai_rules: aiRules 
        }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || '세션 생성에 실패했습니다.');
      }

      const sessionData = await response.json();
      setCreatedSession(sessionData);
      // 성공 메시지 또는 다음 단계 안내

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
            <input id="sessName" value={sessionName} onChange={(e) => setSessionName(e.target.value)} placeholder="2025 공개채용 필기 A세션"/>
            
            <div className="row">
              <div>
                <label htmlFor="startAt">시작 일시</label>
                <input type="datetime-local" id="startAt" value={startTime} onChange={(e) => setStartTime(e.target.value)} />
              </div>
              <div>
                <label htmlFor="endAt">종료 일시</label>
                <input type="datetime-local" id="endAt" value={endTime} onChange={(e) => setEndTime(e.target.value)} />
              </div>
            </div>
            
            <label>AI 감지 규칙</label>
            <div className="row">
              <label className={aiRules.gaze ? 'ai-rule-checked ai-rule-label' : 'ai-rule-label'}><input type="checkbox" name="gaze" checked={aiRules.gaze} onChange={handleCheckboxChange} /> 시선 이탈</label>
              <label className={aiRules.windowSwitch ? 'ai-rule-checked ai-rule-label' : 'ai-rule-label'}><input type="checkbox" name="windowSwitch" checked={aiRules.windowSwitch} onChange={handleCheckboxChange} /> 창 전환</label>
              <label className={aiRules.forbiddenItem ? 'ai-rule-checked ai-rule-label' : 'ai-rule-label'}><input type="checkbox" name="forbiddenItem" checked={aiRules.forbiddenItem} onChange={handleCheckboxChange} /> 금지 물품</label>
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

            <div className="row" style={{ marginTop: '10px' }}>
              <button className="btn" onClick={handleCreateSession} disabled={loading}>
                {loading ? '생성 중...' : '세션 생성'}
              </button>
            </div>

            

          </div>
          <div className="card">
            <h3>상태</h3>
            {error ? (
              <p style={{ color: 'red' }}>{error}</p>
            ) : createdSession ? (
              <div className="list">
                <div className="item"><span>세션 이름: <b>{createdSession.name}</b></span></div>
                <div className="item"><span>세션 ID: <b>{createdSession.id}</b></span></div>
                <div className="item"><span>시작 시간: <b>{createdSession.start_time}</b></span></div>
                <div className="item"><span>종료 시간: <b>{createdSession.end_time}</b></span></div>
                <div className="item"><span>AI 규칙: </span>
                  <span>
                    {createdSession.ai_rules.gaze && '시선 이탈, '}
                    {createdSession.ai_rules.windowSwitch && '창 전환, '}
                    {createdSession.ai_rules.forbiddenItem && '금지 물품'}
                  </span>
                </div>
              </div>
            ) : (
              <p>새로운 세션을 생성하세요.</p>
            )}
          </div>
        </div>
      </section>
    </main>
  );
};

export default AdminPage;
