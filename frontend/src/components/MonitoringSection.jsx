import React, { useState } from 'react';

const MonitoringSection = () => {
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { who: 'them', text: '감독관: 입실 후 신분증 준비해주세요.' },
    { who: 'you', text: '응시자: 네, 준비했습니다.' },
  ]);

  const handleSendChat = () => {
    if (!chatInput.trim()) return;
    // TODO: 웹소켓으로 메시지 전송
    setChatHistory(prev => [...prev, { who: 'you', text: `응시자: ${chatInput}` }]);
    setChatInput('');
  };

  return (
    <section className="col">
      <div className="card">
        <h3>내 웹캠</h3>
        <div className="video"></div>
      </div>
      <div className="card">
        <h3>보조 카메라(모바일)</h3>
        <div className="video"></div>
      </div>
      <div className="card">
        <h3>감독관 메시지</h3>
        <div className="chat">
          {chatHistory.map((msg, i) => (
            <div key={i} className={`bubble ${msg.who}`}>{msg.text}</div>
          ))}
        </div>
        <div className="row" style={{ marginTop: '8px' }}>
          <input placeholder="메시지를 입력하세요" value={chatInput} onChange={e => setChatInput(e.target.value)} />
          <button className="btn" onClick={handleSendChat}>전송</button>
        </div>
      </div>
    </section>
  );
};

export default MonitoringSection;
