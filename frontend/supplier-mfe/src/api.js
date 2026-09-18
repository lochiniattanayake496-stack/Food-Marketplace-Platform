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

// No status filter: backend now returns ALL of this supplier's own
// products (pending/approved/rejected) when supplier_id matches the
// authenticated caller — see Product Service's show_all_statuses logic.
export const getMyProducts = (supplierId) =>
  apiClient.get('/products', { params: { supplier_id: supplierId } });

// supplier_id is never sent — backend takes ownership from the
// authenticated token. stock is required so Cart Service's stock
// validation has real data to check against.
export const createProduct = (payload) =>
  apiClient.post('/products', {
    name: payload.name,
    description: payload.description,
    category: payload.category,
    price: payload.price,
    stock: payload.stock,
  });

export const updateProduct = (productId, payload) =>
  apiClient.patch(`/products/${productId}`, payload);

export const deactivateProduct = (productId) =>
  apiClient.patch(`/products/${productId}/deactivate`);

export default apiClient;