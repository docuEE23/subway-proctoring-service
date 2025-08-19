import React, { useState } from "react";
import { useNavigate, Navigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import "../css/login.css";

const LoginPage = () => {
  const [id, setId] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const { user, login } = useAuth();

  if (user) {
    switch (user.role) {
      case "examinee":
        return <Navigate to="/examinee" />;
      case "supervisor":
        return <Navigate to="/supervisor" />;
      case "admin":
        return <Navigate to="/admin" />;
      default:
        return <Navigate to="/" />;
    }
  }

  const handleLogin = async (requiredRole) => {
    try {
      // AuthContext의 login 함수 호출
      await login(id, password, requiredRole);

      switch (requiredRole) {
        case "examinee":
          navigate("/examinee");
          break;
        case "supervisor":
          navigate("/supervisor");
          break;
        case "admin":
          navigate("/admin");
          break;
        default:
          // 이 경우는 발생하지 않아야 함
          break;
      }
    } catch (error) {
      alert(error.message || "로그인에 실패했습니다. 다시 시도해주세요.");
    }
  };

  return (
    <section id="view-login" className="view show">
      <div className="grid cols-2">
        <div className="card">
          <h3>사용자 로그인</h3>
          <label>아이디</label>
          <input
            id="loginId"
            type="text"
            placeholder="아이디를 입력하세요"
            value={id}
            onChange={(e) => setId(e.target.value)}
          />
          <label>비밀번호</label>
          <input
            id="loginPw"
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <div
            className="login-buttons"
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "10px",
              marginTop: "20px",
            }}
          >
            <button className="btn" onClick={() => handleLogin("examinee")}>
              응시자 로그인
            </button>
            <button
              className="btn secondary"
              onClick={() => handleLogin("supervisor")}
            >
              감독관 로그인
            </button>
            <button className="btn warn" onClick={() => handleLogin("admin")}>
              관리자 로그인
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default LoginPage;
