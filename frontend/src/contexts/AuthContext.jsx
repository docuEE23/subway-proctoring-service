import React, { createContext, useContext, useState } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null); // { id, role }

  const login = async (id, password, role) => {
    // --- 기존 API 호출 로직 주석 처리 ---
    /*
    try {
      const response = await fetch('/api/v1/login', { // FastAPI 서버 주소
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id, password, role }),
      });

      if (!response.ok) {
        // 서버가 4xx, 5xx 응답을 반환했을 때 에러를 발생시킴
        const errorData = await response.json();
        throw new Error(errorData.detail || '로그인에 실패했습니다.');
      }

      const userData = await response.json(); // { id, role, ... }
      setUser({ id: userData.id, role: userData.role });

      // (선택사항) JWT 토큰을 사용하는 경우 로컬 스토리지에 저장
      // if (userData.access_token) {
      //   localStorage.setItem('token', userData.access_token);
      // }

    } catch (error) {
      // 네트워크 에러나 위에서 throw된 에러를 다시 throw하여
      // 호출한 컴포넌트(LoginPage)에서 처리할 수 있도록 함
      throw error;
    }
    */

    // --- 테스트용 임시 로그인 로직 ---
    console.log(`Attempting mock login for role: ${role} with id: ${id}`);
    if (password === '1234') {
      // 역할에 따라 사용자 정보 설정
      setUser({ id: id, role: role });
      console.log(`Mock login successful for user: ${id}, role: ${role}`);
    } else {
      throw new Error('비밀번호가 일치하지 않습니다. (테스트용 비밀번호는 1234 입니다)');
    }
  };

  const logout = () => {
    setUser(null);
    // (선택사항) 토큰을 사용하는 경우 로컬 스토리지에서 제거
    // localStorage.removeItem('token');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);