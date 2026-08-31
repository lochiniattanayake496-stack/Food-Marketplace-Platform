import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

// Permanent fallback profiles for offline/error states
const MOCK_USERS = {
  '1': { id: '1', username: 'Customer User', role: 'customer' },
  '2': { id: '2', username: 'Supplier User', role: 'supplier' },
  '3': { id: '3', username: 'Data Steward User', role: 'steward' },
};

export function AuthProvider({ children }) {
  const [user, setUser] = useState(MOCK_USERS['1']);
  const [loading, setLoading] = useState(false);

  const fetchUser = async (userId) => {
    setLoading(true);
    try {
      // 3-second timeout prevents 504 Gateway hangs
      const response = await axios.get(`http://localhost:8000/api/v1/users/${userId}`, {
        timeout: 3000
      });
      setUser(response.data);
    } catch (error) {
      console.warn(`Backend API error (${error.response?.status || 'Network Error'}). Using fallback user.`);
      // Safely fall back to default profile on 500, 504, or server failure
      setUser(MOCK_USERS[userId] || MOCK_USERS['1']);
    } finally {
      setLoading(false);
    }
  };

  const switchRole = (userId) => {
    fetchUser(userId);
  };

  useEffect(() => {
    fetchUser('1');
  }, []);

  return (
    <AuthContext.Provider value={{ user, switchRole, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);