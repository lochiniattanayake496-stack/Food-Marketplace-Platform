import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_BFF_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Fixed parameter to status=PENDING
export const getPendingProducts = () => apiClient.get('/products?status=PENDING');

export const updateProductStatus = (productId, status, rejection_reason = null) => {
  const payload = { status };
  if (rejection_reason) {
    // Send both field variants to pass Pydantic schema validation
    payload.rejectionReason = rejection_reason;
    payload.rejection_reason = rejection_reason;
  }
  return apiClient.patch(`/products/${productId}`, payload);
};

export const getUsers = () => apiClient.get('/users');
export const updateUserRole = (userId, role) => apiClient.patch(`/users/${userId}/role`, { role });

export default apiClient;