import axios from 'axios';

// Create Axios instance pointing to BFF URL from environment variables
const api = axios.create({
  baseURL: import.meta.env.VITE_BFF_URL || 'http://127.0.0.1:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper request functions supporting all CRUD & PATCH operations
export const getRequest = (url, params) => api.get(url, { params });
export const postRequest = (url, data) => api.post(url, data);
export const patchRequest = (url, data) => api.patch(url, data);
export const deleteRequest = (url) => api.delete(url);

export default api;
