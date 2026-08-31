import React, { createContext, useContext, useState, useEffect } from 'react';
import { getRequest } from './api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch active user profile from BFF on load
    getRequest('/users/1')
      .then((res) => setUser(res.data))
      .catch((err) => console.error('Failed to load user profile', err))
      .finally(() => setLoading(false));
  }, []);

  const switchRole = (newRoleId) => {
    // Quick helper to switch mock user accounts during development
    setLoading(true);
    getRequest(`/users/${newRoleId}`)
      .then((res) => setUser(res.data))
      .catch((err) => console.error('Error switching user', err))
      .finally(() => setLoading(false));
  };

  return (
    <AuthContext.Provider value={{ user, switchRole, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);