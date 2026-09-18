import React from 'react';

export default function ProductCard({ product, onAddToCart }) {
  return (
    <div className="product-card">
      <div className="product-card__category">{product.category}</div>
      <h3 className="product-card__name">{product.name}</h3>
      <p className="product-card__price">
        ${product.price ? Number(product.price).toFixed(2) : '0.00'}
      </p>
      <button
        className="product-card__button"
        onClick={() => onAddToCart(product)}
      >
        Add to Cart
      </button>
    </div>
  );
}