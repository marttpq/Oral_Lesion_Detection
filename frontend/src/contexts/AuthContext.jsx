import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export function AuthProvider({ children }) {
    // Default to demo token to bypass login for frontend doctor review/testing
    const [token, setToken] = useState(() => {
        const saved = localStorage.getItem('token');
        return saved !== null ? saved : 'demo-doctor-token';
    });

    // Helper to decode JWT payload safely
    const decodeJWT = (jwtToken) => {
        try {
            const base64Url = jwtToken.split('.')[1];
            if (!base64Url) return null;
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function (c) {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join(''));
            return JSON.parse(jsonPayload);
        } catch (e) {
            return null;
        }
    };

    // Derive user synchronously to avoid delay or race condition
    let user = null;
    if (token) {
        if (token === 'demo-doctor-token') {
            user = { email: 'doctor@demo-clinic.org', role: 'Doctor (Review)', id: 'demo-doc', token };
        } else {
            const decoded = decodeJWT(token);
            if (decoded && decoded.sub) {
                user = { email: decoded.sub, id: decoded.id, picture: decoded.picture, token };
            } else {
                // Fallback for unexpected token structures
                user = { email: 'Doctor (Review)', token };
            }
        }
    }
    const loading = false; // Synchronous, so no loading delay

    useEffect(() => {
        if (token) {
            localStorage.setItem('token', token);
        } else {
            localStorage.removeItem('token');
        }
    }, [token]);

    const login = (newToken) => {
        setToken(newToken);
    };

    const logout = () => {
        setToken(null);
    };

    return (
        <AuthContext.Provider value={{ user, token, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);
