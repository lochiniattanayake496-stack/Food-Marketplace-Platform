import React, { useEffect } from 'react';
import { BrowserRouter, Link, useLocation, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './AuthContext';

const KNOWN_PREFIXES = ['/customer', '/supplier', '/steward'];

function ShellContent() {
  const { user, loading, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    if (loading || !user) return;
    const onKnownRoute = KNOWN_PREFIXES.some((p) => location.pathname.startsWith(p));
    if (!onKnownRoute) {
      const defaultPath =
        user.role === 'Supplier' ? '/supplier' : user.role === 'DataSteward' ? '/steward' : '/customer';
      navigate(defaultPath, { replace: true });
    }
  }, [loading, user, location.pathname, navigate]);

  if (loading) return <div style={{ padding: '20px' }}>Loading Application Shell...</div>;

  return (
    <div style={{ fontFamily: 'sans-serif', minHeight: '100vh', backgroundColor: '#f4f6f8' }}>
      <header style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '1rem 2rem',
        backgroundColor: '#1e293b',
        color: '#fff'
      }}>
        <h2 style={{ margin: 0 }}>Food Marketplace Platform</h2>

        <nav style={{ display: 'flex', gap: '15px' }}>
          {user?.role === 'Customer' && (
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
          )}

          {user?.role === 'Supplier' && (
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

          {user?.role === 'DataSteward' && (
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

        <div style={{ fontSize: '14px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span>Signed in as: <strong>{user?.email}</strong> ({user?.role})</span>
          <button
            onClick={logout}
            style={{ padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', border: 'none', background: '#ef4444', color: '#fff' }}
          >
            Logout
          </button>
        </div>
      </header>

      <main style={{ padding: '2rem' }}>
        {/* single-spa mounts the active MFE (customer/supplier/steward)
            into this div directly — see src/single-spa-config.js.
            No <Routes>/<Route> needed here: single-spa listens to the
            same pushState navigation that <Link> triggers. */}
        <div id="mfe-container" style={{ minHeight: 'calc(100vh - 120px)' }} />
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