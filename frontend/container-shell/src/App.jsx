import React from 'react';
import { BrowserRouter, Routes, Route, Link, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './AuthContext';

function SubAppFrame({ src, title }) {
  return (
    <div style={{ width: '100%', height: 'calc(100vh - 120px)', border: 'none' }}>
      <iframe
        src={src}
        title={title}
        style={{ width: '100%', height: '100%', border: 'none', borderRadius: '8px', background: '#fff' }}
      />
    </div>
  );
}

function ShellContent() {
  const { user, switchRole, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Map User IDs directly to their default MFE routes
  const userRouteMap = {
    '1': '/customer',
    '2': '/supplier',
    '3': '/steward',
  };

  const handleRoleSelect = (userId) => {
    // 1. Update Auth state
    switchRole(userId);

    // 2. Explicitly force router navigation to matching route
    const targetRoute = userRouteMap[userId] || '/customer';
    navigate(targetRoute);
  };

  if (loading) return <div style={{ padding: '20px' }}>Loading Application Shell...</div>;

  return (
    <div style={{ fontFamily: 'sans-serif', minHeight: '100vh', backgroundColor: '#f4f6f8' }}>
      {/* Shell Header */}
      <header style={{
        display: 'flex',
        justify: 'space-between',
        alignItems: 'center',
        padding: '1rem 2rem',
        backgroundColor: '#1e293b',
        color: '#fff'
      }}>
        <h2 style={{ margin: 0 }}>Food Marketplace Platform</h2>
        
        {/* Navigation Tabs synced to current URL */}
        <nav style={{ display: 'flex', gap: '15px' }}>
          <Link 
            to="/customer" 
            style={{
              padding: '8px 16px',
              background: location.pathname.startsWith('/customer') ? '#2563eb' : '#334155',
              color: '#fff', borderRadius: '4px', textDecoration: 'none'
            }}
          >
            Customer Store
          </Link>

          {(user?.role === 'supplier' || location.pathname.startsWith('/supplier')) && (
            <Link 
              to="/supplier" 
              style={{
                padding: '8px 16px',
                background: location.pathname.startsWith('/supplier') ? '#2563eb' : '#334155',
                color: '#fff', borderRadius: '4px', textDecoration: 'none'
              }}
            >
              Supplier Portal
            </Link>
          )}

          {(user?.role === 'steward' || location.pathname.startsWith('/steward')) && (
            <Link 
              to="/steward" 
              style={{
                padding: '8px 16px',
                background: location.pathname.startsWith('/steward') ? '#2563eb' : '#334155',
                color: '#fff', borderRadius: '4px', textDecoration: 'none'
              }}
            >
              Data Steward Workspace
            </Link>
          )}
        </nav>

        {/* Role Switcher Dropdown */}
        <div style={{ fontSize: '14px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span>Active: <strong>{user?.name || user?.username}</strong> ({user?.role})</span>
          <select 
            onChange={(e) => handleRoleSelect(e.target.value)} 
            value={String(user?.id || '1')} 
            style={{ padding: '6px', borderRadius: '4px', cursor: 'pointer' }}
          >
            <option value="1">Customer User</option>
            <option value="2">Supplier User</option>
            <option value="3">Data Steward User</option>
          </select>
        </div>
      </header>

      {/* Main Workspace Frame */}
      <main style={{ padding: '2rem' }}>
        <Routes>
          <Route path="/customer/*" element={<SubAppFrame src="http://localhost:3001" title="Customer MFE" />} />
          <Route path="/supplier/*" element={<SubAppFrame src="http://localhost:3002" title="Supplier MFE" />} />
          <Route path="/steward/*" element={<SubAppFrame src="http://localhost:3003" title="Steward MFE" />} />
          <Route path="*" element={<Navigate to="/customer" replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <ShellContent />
      </BrowserRouter>
    </AuthProvider>
  );
}