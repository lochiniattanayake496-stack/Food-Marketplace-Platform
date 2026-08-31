import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_BFF_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

export const getSupplierProducts = (supplierId) => 
  apiClient.get(`/products`, { params: { supplier_id: supplierId } });

export const createProduct = (payload) => 
  apiClient.post(`/products`, payload);

export default apiClient;