import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_BFF_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to attach Cognitio Bearer Token if available
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('cognito_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => Promise.reject(error));

export const getRequest = (url, params) => apiClient.get(url, { params });
export const postRequest = (url, data) => apiClient.post(url, data);
export const patchRequest = (url, data) => apiClient.patch(url, data);
export const deleteRequest = (url) => apiClient.delete(url);

export default apiClient;