import React, { useState, useEffect } from 'react';
import { getProducts, getCart, addToCart, removeFromCart } from '../api';
import ProductCard from './components/ProductCard';
import CartPanel from './components/CartPanel';

export default function StoreScreen() {
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState({ id: null, items: [], totalPrice: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStoreData();
  }, []);

  async function fetchStoreData() {
    setLoading(true);
    setError(null);
    try {
      const [productsRes, cartRes] = await Promise.all([getProducts(), getCart()]);
      setProducts(productsRes.data || []);
      setCart(cartRes.data || { id: null, items: [], totalPrice: 0 });
    } catch (err) {
      console.error('Failed to load store data:', err);
      setError('Could not load the store right now. Please try again shortly.');
    } finally {
      setLoading(false);
    }
  }

  async function handleAddToCart(product) {
    if (!cart.id) return;
    try {
      const response = await addToCart(cart.id, product.id, 1);
      setCart(response.data);
    } catch (err) {
      console.error('Failed to add item to cart:', err);
      const message = err.response?.data?.error || 'Could not add this item to your cart.';
      alert(message);
    }
  }

  async function handleRemoveItem(productId) {
    if (!cart.id) return;
    try {
      const response = await removeFromCart(cart.id, productId);
      setCart(response.data);
    } catch (err) {
      console.error('Failed to remove item:', err);
    }
  }

  if (loading) return <div className="store-loading">Loading store catalog...</div>;
  if (error) return <div className="store-error">{error}</div>;

  return (
    <div className="store">
      <h2 className="store__title">Fresh Market</h2>
      <div className="store__layout">
        <div className="store__products">
          <h3 className="store__section-title">Approved Products</h3>
          {products.length === 0 ? (
            <p className="store__empty">No products available right now.</p>
          ) : (
            <div className="product-grid">
              {products.map((item) => (
                <ProductCard key={item.id} product={item} onAddToCart={handleAddToCart} />
              ))}
            </div>
          )}
        </div>
        <CartPanel cart={cart} onRemoveItem={handleRemoveItem} />
      </div>
    </div>
  );
}