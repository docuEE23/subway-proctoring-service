import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ProtectedRoute = ({ children, requiredRole }) => {
  const { user } = useAuth();

  if (!user) {
    // User is not authenticated, redirect to login page
    return <Navigate to="/login" replace />;
  }

  // Check if user has the required role
  if (requiredRole && user.role !== requiredRole) {
    // User is authenticated but does not have the required role
    // Redirect to a suitable page, e.g., home or unauthorized page
    return <Navigate to="/" replace />; // Or a specific unauthorized page
  }

  return children;
};

export default ProtectedRoute;