import React, { createContext, useContext, useState } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null); // { id, role }

  const login = async (id, password, role) => {
    try {
      const response = await fetch('/api/v1/auth/login', { // FastAPI 서버 주소
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: id, password }),
      });

      if (!response.ok) {
        // 서버가 4xx, 5xx 응답을 반환했을 때 에러를 발생시킴
        const errorData = await response.json();
        let errorMessage = '로그인에 실패했습니다.';
        if (errorData.detail) {
          if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          } else if (errorData.detail.message) { // Assuming detail is an object with a 'message' property
            errorMessage = errorData.detail.message;
          }
        }
        throw new Error(errorMessage);
      }

      const userData = await response.json(); // { token, role, expires_at }
      setUser({ id: null, role: userData.role }); // Set id to null as backend does not provide it directly in LoginResponseModel

      // JWT token is now handled by HttpOnly cookie set by backend.
      // No need to store in localStorage here.

    } catch (error) {
      // 네트워크 에러나 위에서 throw된 에러를 다시 throw하여
      // 호출한 컴포넌트(LoginPage)에서 처리할 수 있도록 함
      throw error;
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