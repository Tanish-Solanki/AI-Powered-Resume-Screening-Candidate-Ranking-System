import React, { createContext, useState, useEffect } from 'react';
import authService from '../services/auth.service';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [userToken, setUserToken] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Hydrate state from localStorage on initial render
        const token = authService.getCurrentToken();
        if (token) {
            setUserToken(token);
        }
        setLoading(false);
    }, []);

    const login = async (email, password) => {
        const data = await authService.login(email, password);
        setUserToken(data.access_token);
        return data;
    };

    const register = async (userData) => {
        const data = await authService.register(userData);
        // Optionally auto-login following register, or just return success
        return data;
    };

    const logout = () => {
        authService.logout();
        setUserToken(null);
    };

    return (
        <AuthContext.Provider value={{ userToken, loading, login, register, logout }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};
