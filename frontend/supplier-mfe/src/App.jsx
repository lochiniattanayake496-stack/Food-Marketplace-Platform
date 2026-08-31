import React, { useState, useEffect } from 'react';
import { getSupplierProducts, createProduct } from './api';

export default function App() {
  const [supplierId] = useState('sup_001'); // Changed to string ID matching backend schema
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    category: '',
    stock_quantity: '',
  });

  useEffect(() => {
    fetchMyProducts();
  }, []);

  const fetchMyProducts = async () => {
  try {
    setLoading(true);
    const response = await getSupplierProducts(supplierId);
    setProducts(Array.isArray(response.data) ? response.data : []);
  } catch (err) {
    console.error('Error fetching supplier products:', err);
    setProducts([]); // Prevent UI render crash
  } finally {
    setLoading(false);
  }
};

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
  e.preventDefault();
  try {
    const payload = {
      name: formData.name,
      description: formData.description,
      category: formData.category,
      price: parseFloat(formData.price),
      supplier_id: String(supplierId), // <-- Changed supplierId to supplier_id
    };

    const res = await createProduct(payload);
    setProducts((prev) => [...prev, res.data]);
    setFormData({ name: '', description: '', price: '', category: '', stock_quantity: '' });
    alert('Product submitted for approval!');
  } catch (err) {
    console.error('Failed to submit product:', err.response?.data || err);
    alert('Failed to submit product. Check browser console.');
  }
};

  return (
    <div style={{ fontFamily: 'sans-serif', padding: '20px', maxWidth: '1000px', margin: '0 auto' }}>
      <h2>Supplier Portal</h2>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px', marginTop: '20px' }}>
        {/* Product Submission Form */}
<div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '20px', backgroundColor: '#ffffff' }}>
  <h3 style={{ color: '#0f172a', marginTop: 0 }}>Add New Product</h3>
  <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
    <div>
      <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px', color: '#334155', fontWeight: '500' }}>
        Product Name
      </label>
      <input
        type="text"
        name="name"
        value={formData.name}
        onChange={handleInputChange}
        required
        style={{ width: '100%', padding: '8px', boxSizing: 'border-box', backgroundColor: '#f8fafc', border: '1px solid #cbd5e1', borderRadius: '4px', color: '#0f172a' }}
      />
    </div>
    <div>
      <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px', color: '#334155', fontWeight: '500' }}>
        Category
      </label>
      <input
        type="text"
        name="category"
        value={formData.category}
        onChange={handleInputChange}
        required
        style={{ width: '100%', padding: '8px', boxSizing: 'border-box', backgroundColor: '#f8fafc', border: '1px solid #cbd5e1', borderRadius: '4px', color: '#0f172a' }}
      />
    </div>
    <div>
      <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px', color: '#334155', fontWeight: '500' }}>
        Price ($)
      </label>
      <input
        type="number"
        step="0.01"
        name="price"
        value={formData.price}
        onChange={handleInputChange}
        required
        style={{ width: '100%', padding: '8px', boxSizing: 'border-box', backgroundColor: '#f8fafc', border: '1px solid #cbd5e1', borderRadius: '4px', color: '#0f172a' }}
      />
    </div>
    <div>
      <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px', color: '#334155', fontWeight: '500' }}>
        Stock Quantity
      </label>
      <input
        type="number"
        name="stock_quantity"
        value={formData.stock_quantity}
        onChange={handleInputChange}
        style={{ width: '100%', padding: '8px', boxSizing: 'border-box', backgroundColor: '#f8fafc', border: '1px solid #cbd5e1', borderRadius: '4px', color: '#0f172a' }}
      />
    </div>
    <div>
      <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px', color: '#334155', fontWeight: '500' }}>
        Description
      </label>
      <textarea
        name="description"
        value={formData.description}
        onChange={handleInputChange}
        rows="3"
        style={{ width: '100%', padding: '8px', boxSizing: 'border-box', backgroundColor: '#f8fafc', border: '1px solid #cbd5e1', borderRadius: '4px', color: '#0f172a' }}
      />
    </div>
    <button
      type="submit"
      style={{ padding: '10px', backgroundColor: '#2563eb', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', marginTop: '10px', fontWeight: '600' }}>
      Submit for Approval
    </button>
  </form>
</div> 
        {/* Existing Listings View */}
        <div style={{ border: '1px solid #ccc', borderRadius: '8px', padding: '20px', backgroundColor: '#fff' }}>
          <h3>My Product Listings</h3>
          {loading ? (
            <p>Loading listings...</p>
          ) : products.length === 0 ? (
            <p style={{ color: '#666' }}>No product listings found.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {products.map((item) => (
                <div key={item.id || item.name} style={{ borderBottom: '1px solid #eee', paddingBottom: '10px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <strong>{item.name}</strong>
                    <span style={{
                      padding: '2px 8px',
                      borderRadius: '12px',
                      fontSize: '12px',
                      backgroundColor: item.status === 'approved' ? '#d1fae5' : item.status === 'rejected' ? '#fee2e2' : '#fef3c7',
                      color: item.status === 'approved' ? '#065f46' : item.status === 'rejected' ? '#991b1b' : '#92400e'
                    }}>
                      {item.status || 'pending'}
                    </span>
                  </div>
                  <p style={{ margin: '5px 0 0 0', fontSize: '13px', color: '#666' }}>
                    ${typeof item.price === 'number' ? item.price.toFixed(2) : item.price}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}