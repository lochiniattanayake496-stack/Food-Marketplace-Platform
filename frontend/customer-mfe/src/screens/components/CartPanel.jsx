import React from 'react';

export default function CartPanel({ cart, onRemoveItem }) {
  const items = cart.items || [];

  return (
    <div className="cart-panel">
      <h3 className="cart-panel__title">My Cart</h3>
      {items.length === 0 ? (
        <p className="cart-panel__empty">Your cart is empty.</p>
      ) : (
        <>
          <ul className="cart-panel__list">
            {items.map((item) => (
              <li key={item.productId} className="cart-panel__item">
                <div>
                  <div className="cart-panel__item-name">{item.productName}</div>
                  <small className="cart-panel__item-meta">
                    Qty: {item.quantity} × ${Number(item.unitPrice).toFixed(2)}
                  </small>
                </div>
                <button
                  className="cart-panel__remove"
                  onClick={() => onRemoveItem(item.productId)}
                >
                  ✕
                </button>
              </li>
            ))}
          </ul>
          <hr className="cart-panel__divider" />
          <div className="cart-panel__total">
            <span>Total</span>
            <span>${Number(cart.totalPrice || 0).toFixed(2)}</span>
          </div>
        </>
      )}
    </div>
  );
}