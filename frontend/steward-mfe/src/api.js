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

// Data Steward filtering by status=PENDING is allowed regardless of
// supplier_id — the backend's is_steward check permits this.
export const getPendingProducts = () =>
  apiClient.get('/products', { params: { status: 'PENDING' } });

// Uses the dedicated review endpoint (ProductStatusUpdateRequest),
// NOT the general PATCH /products/{id} — status was deliberately
// removed from the general update schema to prevent suppliers from
// self-approving their own products.
export const reviewProduct = (productId, status, rejectionReason = null) => {
  const payload = { status };
  if (rejectionReason) {
    payload.rejectionReason = rejectionReason;
  }
  return apiClient.patch(`/products/${productId}/review`, payload);
};

export default apiClient;