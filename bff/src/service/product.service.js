const axios = require('axios');

const PRODUCT_SERVICE_URL = process.env.PRODUCT_SERVICE_URL || 'http://127.0.0.1:8001';

function forwardHeaders(req) {
  const headers = {};
  if (req.headers['x-user-id']) headers['X-User-Id'] = req.headers['x-user-id'];
  if (req.headers['x-user-role']) headers['X-User-Role'] = req.headers['x-user-role'];
  return headers;
}

async function listProducts(req) {
  const response = await axios.get(`${PRODUCT_SERVICE_URL}/api/v1/products`, {
    headers: forwardHeaders(req),
    params: req.query,
  });
  return response.data;
}

async function getProductById(req, productId) {
  const response = await axios.get(`${PRODUCT_SERVICE_URL}/api/v1/products/${productId}`, {
    headers: forwardHeaders(req),
  });
  return response.data;
}

async function submitProduct(req) {
  const response = await axios.post(`${PRODUCT_SERVICE_URL}/api/v1/products`, req.body, {
    headers: forwardHeaders(req),
  });
  return response.data;
}

async function updateProduct(req, productId) {
  const response = await axios.patch(`${PRODUCT_SERVICE_URL}/api/v1/products/${productId}`, req.body, {
    headers: forwardHeaders(req),
  });
  return response.data;
}

async function reviewProduct(req, productId) {
  const response = await axios.patch(`${PRODUCT_SERVICE_URL}/api/v1/products/${productId}/review`, req.body, {
    headers: forwardHeaders(req),
  });
  return response.data;
}

async function deactivateProduct(req, productId) {
  const response = await axios.patch(`${PRODUCT_SERVICE_URL}/api/v1/products/${productId}/deactivate`, {}, {
    headers: forwardHeaders(req),
  });
  return response.data;
}

module.exports = {
  listProducts,
  getProductById,
  submitProduct,
  updateProduct,
  reviewProduct,
  deactivateProduct,
};