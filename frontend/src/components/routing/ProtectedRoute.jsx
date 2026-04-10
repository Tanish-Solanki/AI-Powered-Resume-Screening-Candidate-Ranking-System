import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const ProtectedRoute = () => {
    const { userToken, loading } = useAuth();
    
    if (loading) {
        return <div className="flex h-screen items-center justify-center">Loading authentication...</div>;
    }

    // Direct user to generic unauthenticated route if missing token mapping
    if (!userToken) {
        return <Navigate to="/login" replace />;
    }

    return <Outlet />;
};

export default ProtectedRoute;
