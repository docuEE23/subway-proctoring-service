import { Navigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const ProtectedRoute = ({ children, requiredRole }) => {
  const { user } = useAuth();

  if (!user) {
    // 사용자가 로그인하지 않았으면 로그인 페이지로 리디렉션
    return <Navigate to="/login" replace />;
  }

  if (user.role !== requiredRole) {
    // 사용자의 역할이 요구되는 역할과 다르면 로그인 페이지로 리디렉션
    // 또는 권한 없음 페이지(/not-authorized)를 만들어서 보낼 수도 있습니다.
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
