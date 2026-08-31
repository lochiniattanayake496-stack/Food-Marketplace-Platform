import React, { useState, useEffect } from 'react';
import { getProducts, getCart, addToCart, removeFromCart } from './api';

export default function App() {
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState({ id: null, items: [], totalPrice: 0 });
  const [loading, setLoading] = useState(true);
  const activeUserId = "cust_101";

  useEffect(() => {
    fetchStoreData();
  }, []);

  const fetchStoreData = async () => {
    setLoading(true);
    
    // 1. Fetch Products
    try {
      const prodRes = await getProducts();
      setProducts(prodRes.data || []);
    } catch (err) {
      console.error('Error fetching products:', err);
    }

    // 2. Fetch Cart
    try {
      const cartRes = await getCart(activeUserId);
      const cartData = cartRes.data || {};
      // Handle backend mapping whether it returns 'cartId' or 'id'
      setCart({
        id: cartData.cartId || cartData.id,
        items: cartData.items || [],
        totalPrice: cartData.totalPrice || 0
      });
    } catch (err) {
      console.error('Error fetching cart:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = async (product) => {
    if (!cart.id) {
      alert("Cart initialization error. Please refresh.");
      return;
    }
    try {
      const updatedCart = await addToCart(cart.id, product);
      const cartData = updatedCart.data || {};
      setCart({
        id: cartData.cartId || cartData.id,
        items: cartData.items || [],
        totalPrice: cartData.totalPrice || 0
      });
    } catch (err) {
      console.error('Failed to add item to cart:', err);
    }
  };

  const handleRemoveItem = async (productId) => {
    try {
      const updatedCart = await removeFromCart(cart.id, productId);
      const cartData = updatedCart.data || {};
      setCart({
        id: cartData.cartId || cartData.id,
        items: cartData.items || [],
        totalPrice: cartData.totalPrice || 0
      });
    } catch (err) {
      console.error('Failed to remove item:', err);
    }
  };

  if (loading) return <div style={{ padding: '20px' }}>Loading store catalog...</div>;

  return (
    <div style={{ fontFamily: 'sans-serif', padding: '20px', maxWidth: '1000px', margin: '0 auto' }}>
      <h2>Customer Marketplace Store</h2>
      
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px', marginTop: '20px' }}>
        {/* Product Catalog */}
        <div>
          <h3>Approved Products</h3>
          {products.length === 0 ? (
            <p style={{ color: '#666' }}>No approved products available right now.</p>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '15px' }}>
              {products.map((item) => (
                <div key={item.id} style={{ border: '1px solid #ccc', borderRadius: '8px', padding: '15px', background: '#fff' }}>
                  <h4 style={{ margin: '0 0 10px 0' }}>{item.name}</h4>
                  <p style={{ margin: '0 0 5px 0', color: '#666' }}>Category: {item.category}</p>
                  <p style={{ fontWeight: 'bold', fontSize: '18px', margin: '0 0 10px 0' }}>
                    ${item.price ? Number(item.price).toFixed(2) : '0.00'}
                  </p>
                  <button 
                    onClick={() => handleAddToCart(item)}
                    style={{ width: '100%', padding: '8px', backgroundColor: '#10b981', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                    Add to Cart
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Shopping Cart Summary */}
        <div style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '15px', backgroundColor: '#f9fafb', height: 'fit-content' }}>
          <h3>My Cart</h3>
          {cart.items && cart.items.length > 0 ? (
            <div>
              <ul style={{ paddingLeft: '0', listStyleType: 'none' }}>
                {cart.items.map((item) => (
                  <li key={item.productId || item.product_id} style={{ marginBottom: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div><strong>{item.productName || item.product_name}</strong></div>
                      <small style={{ color: '#555' }}>
                        Qty: {item.quantity} x ${(item.unitPrice || item.unit_price || 0).toFixed(2)}
                      </small>
                    </div>
                    <button 
                      onClick={() => handleRemoveItem(item.productId || item.product_id)}
                      style={{ padding: '4px 8px', backgroundColor: '#ef4444', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                      X
                    </button>
                  </li>
                ))}
              </ul>
              <hr />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 'bold', fontSize: '16px' }}>
                <span>Total:</span>
                <span>${(cart.totalPrice || 0).toFixed(2)}</span>
              </div>
            </div>
          ) : (
            <p style={{ color: '#888' }}>Your cart is empty.</p>
          )}
        </div>
      </div>
    </div>
  );
}