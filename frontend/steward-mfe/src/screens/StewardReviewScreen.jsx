import React, { useEffect, useState, useCallback } from 'react';
import { getPendingProducts, reviewProduct } from '../api';
import PendingProductCard from './components/PendingProductCard';

export default function StewardReviewScreen() {
  const [pendingProducts, setPendingProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchPending = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getPendingProducts();
      setPendingProducts(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      console.error('Error fetching pending products:', err);
      setError('Failed to load pending submissions.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPending();
  }, [fetchPending]);

  const handleApprove = async (productId) => {
    try {
      await reviewProduct(productId, 'APPROVED');
      setPendingProducts((prev) => prev.filter((p) => p.id !== productId));
    } catch (err) {
      console.error('Approval failed:', err.response?.data || err);
      alert(err.response?.data?.detail || 'Failed to approve product.');
    }
  };

  const handleReject = async (productId, reason) => {
    try {
      await reviewProduct(productId, 'REJECTED', reason);
      setPendingProducts((prev) => prev.filter((p) => p.id !== productId));
    } catch (err) {
      console.error('Rejection failed:', err.response?.data || err);
      alert(err.response?.data?.detail || 'Failed to reject product.');
    }
  };

  return (
    <div className="steward-workspace">
      <h2>Data Steward Workspace</h2>

      <div className="panel">
        <h3>Pending Product Approvals</h3>
        {loading ? (
          <p>Loading pending submissions...</p>
        ) : error ? (
          <p className="error-text">{error}</p>
        ) : pendingProducts.length === 0 ? (
          <p className="empty-text">No products pending approval.</p>
        ) : (
          <div className="pending-product-list">
            {pendingProducts.map((product) => (
              <PendingProductCard
                key={product.id}
                product={product}
                onApprove={handleApprove}
                onReject={handleReject}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}