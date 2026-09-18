import React, { useEffect, useState, useCallback } from 'react';
import { getMyProducts, createProduct, updateProduct, deactivateProduct } from '../api';
import { getUser } from '../auth';
import ProductForm from './components/ProductForm';
import ProductListItem from './components/ProductListItem';

export default function SupplierDashboardScreen() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const user = getUser();

  const fetchMyProducts = useCallback(async () => {
    if (!user?.id) return;
    setLoading(true);
    setError(null);
    try {
      const response = await getMyProducts(user.id);
      setProducts(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      console.error('Error fetching supplier products:', err);
      setError('Failed to load your products.');
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  useEffect(() => {
    fetchMyProducts();
  }, [fetchMyProducts]);

  const handleCreate = async (payload) => {
    try {
      await createProduct(payload);
      await fetchMyProducts();
    } catch (err) {
      console.error('Failed to submit product:', err.response?.data || err);
      alert(err.response?.data?.detail || 'Failed to submit product.');
    }
  };

  const handleUpdate = async (productId, payload) => {
    try {
      await updateProduct(productId, payload);
      await fetchMyProducts();
    } catch (err) {
      console.error('Failed to update product:', err.response?.data || err);
      alert(err.response?.data?.detail || 'Failed to update product.');
    }
  };

  const handleDeactivate = async (productId) => {
    try {
      await deactivateProduct(productId);
      await fetchMyProducts();
    } catch (err) {
      console.error('Failed to deactivate product:', err.response?.data || err);
      alert(err.response?.data?.detail || 'Failed to deactivate product.');
    }
  };

  return (
    <div className="supplier-dashboard">
      <h2>Supplier Portal</h2>

      <div className="dashboard-grid">
        <div className="panel">
          <h3>Add New Product</h3>
          <ProductForm onSubmit={handleCreate} />
        </div>

        <div className="panel">
          <h3>My Product Listings</h3>
          {loading ? (
            <p>Loading listings...</p>
          ) : error ? (
            <p className="error-text">{error}</p>
          ) : products.length === 0 ? (
            <p className="empty-text">No product listings yet.</p>
          ) : (
            <div className="product-list">
              {products.map((product) => (
                <ProductListItem
                  key={product.id}
                  product={product}
                  onUpdate={handleUpdate}
                  onDeactivate={handleDeactivate}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}