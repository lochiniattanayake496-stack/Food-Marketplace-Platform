import React, { useState, useEffect } from 'react';
import { getPendingProducts, updateProductStatus, getUsers, updateUserRole } from './api';

export default function App() {
  const [pendingProducts, setPendingProducts] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStewardData();
  }, []);

 const fetchStewardData = async () => {
  setLoading(true);

  // Fetch products independently
  try {
    const prodRes = await getPendingProducts();
    setPendingProducts(prodRes.data || []);
  } catch (err) {
    console.error('Error fetching pending products:', err);
  }

  // Fetch users independently
  try {
    const userRes = await getUsers();
    setUsers(userRes.data || []);
  } catch (err) {
    console.warn('User Service unavailable:', err);
  } finally {
    setLoading(false);
  }
};

const handleApprove = async (productId) => {
    try {
      // Send uppercase 'APPROVED'
      await updateProductStatus(productId, 'APPROVED');
      setPendingProducts((prev) => prev.filter((item) => item.id !== productId));
      alert('Product approved!');
    } catch (err) {
      console.error('Approval failed details:', err.response?.data || err);
      alert(`Failed to approve product: ${JSON.stringify(err.response?.data?.detail || err.message)}`);
    }
  };

  const handleReject = async (productId) => {
    const reason = window.prompt('Please enter a rejection reason:');
    if (!reason || !reason.trim()) return;

    try {
      // Send uppercase 'REJECTED'
      await updateProductStatus(productId, 'REJECTED', reason.trim());
      setPendingProducts((prev) => prev.filter((item) => item.id !== productId));
      alert('Product rejected!');
    } catch (err) {
      console.error('Rejection failed details:', err.response?.data || err);
      alert(`Failed to reject product: ${JSON.stringify(err.response?.data?.detail || err.message)}`);
    }
  };

  const handleRoleChange = async (userId, newRole) => {
    try {
      await updateUserRole(userId, newRole);
      setUsers((prev) =>
        prev.map((user) => (user.id === userId ? { ...user, role: newRole } : user))
      );
    } catch (err) {
      console.error(`Failed to update user #${userId} role:`, err);
    }
  };

  if (loading) return <div style={{ padding: '20px' }}>Loading Steward Workspace...</div>;

  return (
    <div style={{ fontFamily: 'sans-serif', padding: '20px', maxWidth: '1000px', margin: '0 auto' }}>
      <h2>Data Steward Workspace</h2>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '30px', marginTop: '20px' }}>
        {/* Pending Product Approvals Section */}
        <div style={{ border: '1px solid #ccc', borderRadius: '8px', padding: '20px', backgroundColor: '#fff' }}>
          <h3>Pending Product Approvals</h3>
          {pendingProducts.length === 0 ? (
            <p style={{ color: '#666' }}>No products pending approval.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              {pendingProducts.map((product) => (
                <div key={product.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #eee', paddingBottom: '10px' }}>
                  <div>
                    <h4 style={{ margin: '0 0 5px 0' }}>{product.name}</h4>
                    <p style={{ margin: 0, fontSize: '14px', color: '#666' }}>
                      Category: {product.category} | Price: ${product.price ? Number(product.price).toFixed(2) : '0.00'} | Supplier ID: #{product.supplierId || product.supplier_id}
                    </p>
                  </div>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button
                      onClick={() => handleApprove(product.id)}
                      style={{ padding: '6px 12px', backgroundColor: '#10b981', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                      Approve
                    </button>
                    <button
                      onClick={() => handleReject(product.id)}
                      style={{ padding: '6px 12px', backgroundColor: '#ef4444', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                      Reject
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* User Roles Management Section */}
        <div style={{ border: '1px solid #ccc', borderRadius: '8px', padding: '20px', backgroundColor: '#fff' }}>
          <h3>User Role Management</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {users.map((user) => (
              <div key={user.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #eee', paddingBottom: '10px' }}>
                <div>
                  <strong>{user.username}</strong> ({user.email})
                </div>
                <div>
                  <select
                    value={user.role}
                    onChange={(e) => handleRoleChange(user.id, e.target.value)}
                    style={{ padding: '6px', borderRadius: '4px' }}>
                    <option value="customer">customer</option>
                    <option value="supplier">supplier</option>
                    <option value="steward">steward</option>
                  </select>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}