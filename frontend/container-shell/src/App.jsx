import React, { useState } from 'react';
import { AuthProvider, useAuth } from './AuthContext';

function ShellContent() {
  const { user, switchRole, loading } = useAuth();
  const [activeTab, setActiveTab] = useState('customer');

  if (loading) return <div style={{ padding: '20px' }}>Loading Application Shell...</div>;

  return (
    <div style={{ fontFamily: 'sans-serif', minHeight: '100vh', backgroundColor: '#f4f6f8' }}>
      {/* Shell Header */}
      <header style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '1rem 2rem',
        backgroundColor: '#1e293b',
        color: '#fff'
      }}>
        <h2 style={{ margin: 0 }}>Food Marketplace Platform</h2>
        
        {/* Navigation Tabs */}
        <nav style={{ display: 'flex', gap: '15px' }}>
          <button 
            onClick={() => setActiveTab('customer')}
            style={{ padding: '8px 16px', background: activeTab === 'customer' ? '#3b82f6' : '#334155', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
            Customer Store
          </button>
          
          {user?.role === 'supplier' && (
            <button 
              onClick={() => setActiveTab('supplier')}
              style={{ padding: '8px 16px', background: activeTab === 'supplier' ? '#3b82f6' : '#334155', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
              Supplier Portal
            </button>
          )}

          {user?.role === 'steward' && (
            <button 
              onClick={() => setActiveTab('steward')}
              style={{ padding: '8px 16px', background: activeTab === 'steward' ? '#3b82f6' : '#334155', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
              Data Steward Workspace
            </button>
          )}
        </nav>

        {/* Dev Profile Switcher */}
        <div style={{ fontSize: '14px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span>Active: <strong>{user?.username}</strong> ({user?.role})</span>
          <select onChange={(e) => switchRole(e.target.value)} value={user?.id} style={{ padding: '4px' }}>
            <option value="1">Customer User</option>
            <option value="2">Supplier User</option>
            <option value="3">Data Steward User</option>
          </select>
        </div>
      </header>

      {/* Dynamic Workspace Container */}
      <main style={{ padding: '2rem' }}>
        {activeTab === 'customer' && <div style={{ background: '#fff', padding: '20px', borderRadius: '8px' }}>[ Customer MFE Workspace ]</div>}
        {activeTab === 'supplier' && <div style={{ background: '#fff', padding: '20px', borderRadius: '8px' }}>[ Supplier MFE Workspace ]</div>}
        {activeTab === 'steward' && <div style={{ background: '#fff', padding: '20px', borderRadius: '8px' }}>[ Data Steward MFE Workspace ]</div>}
      </main>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <ShellContent />
    </AuthProvider>
  );
}