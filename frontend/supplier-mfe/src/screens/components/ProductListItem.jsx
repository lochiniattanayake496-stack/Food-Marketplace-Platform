import React, { useState } from 'react';

const STATUS_STYLES = {
  APPROVED: 'status-badge status-approved',
  REJECTED: 'status-badge status-rejected',
  PENDING: 'status-badge status-pending',
};

export default function ProductListItem({ product, onUpdate, onDeactivate }) {
  const [editing, setEditing] = useState(false);
  const [editData, setEditData] = useState({
    price: product.price,
    stock: product.stock,
    description: product.description || '',
  });
  const [busy, setBusy] = useState(false);

  const handleEditChange = (e) => {
    const { name, value } = e.target;
    setEditData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = async () => {
    setBusy(true);
    try {
      await onUpdate(product.id, {
        price: parseFloat(editData.price),
        stock: parseInt(editData.stock, 10),
        description: editData.description,
      });
      setEditing(false);
    } finally {
      setBusy(false);
    }
  };

  const handleDeactivate = async () => {
    if (!window.confirm(`Remove "${product.name}" from your listings?`)) return;
    setBusy(true);
    try {
      await onDeactivate(product.id);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="product-list-item">
      <div className="product-list-item-header">
        <strong>{product.name}</strong>
        <span className={STATUS_STYLES[product.status] || 'status-badge status-pending'}>
          {product.status}
        </span>
      </div>

      {product.status === 'REJECTED' && product.rejectionReason && (
        <p className="rejection-reason">Reason: {product.rejectionReason}</p>
      )}

      {!editing ? (
        <>
          <p className="product-meta">
            ${product.price.toFixed(2)} &middot; {product.stock} in stock &middot; {product.category}
          </p>
          <div className="product-actions">
            <button className="btn btn-small" onClick={() => setEditing(true)} disabled={busy}>
              Edit
            </button>
            <button className="btn btn-small btn-danger" onClick={handleDeactivate} disabled={busy}>
              Deactivate
            </button>
          </div>
        </>
      ) : (
        <div className="edit-form">
          <div className="form-row">
            <div className="form-field">
              <label>Price ($)</label>
              <input type="number" step="0.01" min="0.01" name="price" value={editData.price} onChange={handleEditChange} />
            </div>
            <div className="form-field">
              <label>Stock</label>
              <input type="number" min="0" name="stock" value={editData.stock} onChange={handleEditChange} />
            </div>
          </div>
          <div className="form-field">
            <label>Description</label>
            <textarea name="description" rows="2" value={editData.description} onChange={handleEditChange} />
          </div>
          <div className="product-actions">
            <button className="btn btn-small btn-primary" onClick={handleSave} disabled={busy}>
              Save
            </button>
            <button className="btn btn-small" onClick={() => setEditing(false)} disabled={busy}>
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}