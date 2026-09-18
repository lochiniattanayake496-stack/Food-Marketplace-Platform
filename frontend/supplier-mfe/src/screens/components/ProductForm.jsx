import React, { useState } from 'react';

const initialFormState = {
  name: '',
  description: '',
  price: '',
  category: '',
  stock: '',
};

export default function ProductForm({ onSubmit }) {
  const [formData, setFormData] = useState(initialFormState);
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await onSubmit({
        name: formData.name,
        description: formData.description,
        category: formData.category,
        price: parseFloat(formData.price),
        stock: parseInt(formData.stock, 10) || 0,
      });
      setFormData(initialFormState);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="product-form">
      <div className="form-field">
        <label htmlFor="name">Product Name</label>
        <input id="name" name="name" type="text" value={formData.name} onChange={handleChange} required />
      </div>

      <div className="form-field">
        <label htmlFor="category">Category</label>
        <input id="category" name="category" type="text" value={formData.category} onChange={handleChange} required />
      </div>

      <div className="form-row">
        <div className="form-field">
          <label htmlFor="price">Price ($)</label>
          <input id="price" name="price" type="number" step="0.01" min="0.01" value={formData.price} onChange={handleChange} required />
        </div>

        <div className="form-field">
          <label htmlFor="stock">Stock Quantity</label>
          <input id="stock" name="stock" type="number" min="0" value={formData.stock} onChange={handleChange} required />
        </div>
      </div>

      <div className="form-field">
        <label htmlFor="description">Description</label>
        <textarea id="description" name="description" rows="3" value={formData.description} onChange={handleChange} />
      </div>

      <button type="submit" className="btn btn-primary" disabled={submitting}>
        {submitting ? 'Submitting...' : 'Submit for Approval'}
      </button>
    </form>
  );
}