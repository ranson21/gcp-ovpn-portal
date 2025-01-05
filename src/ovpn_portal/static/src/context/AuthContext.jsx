// src/ovpn_portal/static/src/context/AuthContext.jsx
import React, { createContext, useState, useContext, useEffect } from "react";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [authState, setAuthState] = useState({
    isAuthenticated: false,
    email: null,
    token: null,
    loading: true,
  });

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await fetch("/auth/status");
        const data = await response.json();

        setAuthState({
          isAuthenticated: data.authenticated,
          email: data.email,
          token: data.token,
          loading: false,
        });
      } catch (error) {
        console.error("Auth check failed:", error);
        setAuthState((prev) => ({ ...prev, loading: false }));
      }
    };

    checkAuth();
  }, []);

  const updateAuth = (data) => {
    setAuthState({
      isAuthenticated: true,
      email: data.email,
      token: data.token,
      loading: false,
    });
  };

  return (
    <AuthContext.Provider value={{ ...authState, updateAuth }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
