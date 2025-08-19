// src/App.jsx
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";

import LoginPage from "./pages/LoginPage";
import AdminPage from "./pages/AdminPage";
import ExamineePage from "./pages/ExamineePage";
import SupervisorPage from "./pages/SupervisorPage";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/login" />} />
          <Route path="/login" element={<LoginPage />} />

          <Route
            path="/admin"
            element={
              <ProtectedRoute requiredRole="admin">
                <AdminPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/examinee"
            element={
              <ProtectedRoute requiredRole="examinee">
                <ExamineePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/supervisor"
            element={
              <ProtectedRoute requiredRole="supervisor">
                <SupervisorPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="*"
            element={<p>404 Not Found 잘못된 경로로 진입하였습니다.</p>}
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
