import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_BFF_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

export const getProducts = () => apiClient.get('/products?status=APPROVED');

// Query cart by customer_id parameter (Removed trailing slash before query param)
export const getCart = (customerId) => apiClient.get(`/carts?customer_id=${customerId}`);

// Add item using cart_id and expected payload field names
export const addToCart = (cartId, product) => {
  return apiClient.post(`/carts/${cartId}/items`, {
    productId: product.id,
    productName: product.name,
    unitPrice: product.price,
    quantity: product.quantity || 1,
  });
};

// Delete item from cart by cart_id and product_id
export const removeFromCart = (cartId, productId) => {
  return apiClient.delete(`/carts/${cartId}/items/${productId}`);
};

export default apiClient;