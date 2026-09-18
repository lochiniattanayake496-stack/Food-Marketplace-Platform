import React, { useState } from 'react';

export default function PendingProductCard({ product, onApprove, onReject }) {
  const [busy, setBusy] = useState(false);

  const handleApprove = async () => {
    setBusy(true);
    try {
      await onApprove(product.id);
    } finally {
      setBusy(false);
    }
  };

  const handleReject = async () => {
    const reason = window.prompt('Enter a rejection reason:');
    if (!reason || !reason.trim()) return;
    setBusy(true);
    try {
      await onReject(product.id, reason.trim());
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="pending-product-card">
      <div className="pending-product-info">
        <h4>{product.name}</h4>
        <p>
          Category: {product.category} &middot; Price: ${product.price.toFixed(2)} &middot;
          Stock: {product.stock} &middot; Supplier: {product.supplierId}
        </p>
        {product.description && <p className="description">{product.description}</p>}
      </div>
      <div className="pending-product-actions">
        <button className="btn btn-approve" onClick={handleApprove} disabled={busy}>
          Approve
        </button>
        <button className="btn btn-reject" onClick={handleReject} disabled={busy}>
          Reject
        </button>
      </div>
    </div>
  );
}