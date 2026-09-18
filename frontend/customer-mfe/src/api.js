import axios from 'axios';
import { getToken } from './auth';

const API_BASE_URL = import.meta.env.VITE_BFF_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

apiClient.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// No status filter — backend already defaults to APPROVED-only for
// unfiltered requests; passing status=APPROVED explicitly would
// require Data Steward role and get rejected with 403.
export const getProducts = () => apiClient.get('/products');

export const getCart = () => apiClient.get('/carts');

// Backend only expects product_id and quantity — price/name are
// fetched server-side from Product Service, never trusted from the client.
export const addToCart = (cartId, productId, quantity = 1) => {
  return apiClient.post(`/carts/${cartId}/items`, {
    product_id: productId,
    quantity,
  });
};

export const removeFromCart = (cartId, productId) => {
  return apiClient.delete(`/carts/${cartId}/items/${productId}`);
};

export default apiClient;