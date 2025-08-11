import React, { useEffect, useRef } from 'react';

const QuestionSection = ({ questions, currentQ, onNavChange }) => {
  const questionRefs = useRef([]);

  useEffect(() => {
    // currentQ가 변경될 때 해당 문제로 스크롤
    const qElement = questionRefs.current[currentQ - 1];
    if (qElement) {
      qElement.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      });
    }
  }, [currentQ]);

  return (
    <section className="col" style={{maxHeight: 'calc(100vh - 80px)', overflowY: 'auto'}}>
      {questions.map((q, index) => (
        <div 
          key={q.id} 
          className="card q-card" 
          ref={el => questionRefs.current[index] = el}
          style={{border: currentQ === (index + 1) ? '2px solid var(--acc)' : '1px solid var(--line)'}}
        >
          <div className="q-head">
            <b>문항 {index + 1}/{questions.length}</b>
          </div>
          <p className="muted">{q.text}</p>
          {q.options.map((opt, i) => (
            <div className="opt" key={i}>
              <input type="radio" name={`q${q.id}`} id={`q${q.id}o${i}`} />
              <label htmlFor={`q${q.id}o${i}`}><b>{String.fromCharCode(65 + i)}.</b> {opt}</label>
            </div>
          ))}
        </div>
      ))}
       <div className="card q-card">
        <div className="q-head"><b>유의사항</b><span className="muted">부정행위 시 감점/시험 중단</span></div>
        <ul className="muted" style={{margin:0, paddingLeft: '18px'}}>
          <li>시험 중 탭 전환/창 최소화 금지</li>
          <li>감독관 메시지 수신 확인 필수</li>
        </ul>
      </div>
    </section>
  );
};

export default QuestionSection;
