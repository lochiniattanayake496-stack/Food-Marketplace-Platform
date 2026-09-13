const axios = require('axios');

const CART_SERVICE_URL = process.env.CART_SERVICE_URL || 'http://127.0.0.1:8003';

function forwardHeaders(req) {
  const headers = {};
  if (req.headers['x-user-id']) headers['X-User-Id'] = req.headers['x-user-id'];
  if (req.headers['x-user-role']) headers['X-User-Role'] = req.headers['x-user-role'];
  return headers;
}

async function getMyCart(req) {
  const response = await axios.get(`${CART_SERVICE_URL}/api/v1/carts`, {
    headers: forwardHeaders(req),
  });
  return response.data;
}

async function addItemToCart(req, cartId) {
  const response = await axios.post(
    `${CART_SERVICE_URL}/api/v1/carts/${cartId}/items`,
    req.body,
    { headers: forwardHeaders(req) }
  );
  return response.data;
}

async function updateCartItem(req, cartId, productId) {
  const response = await axios.patch(
    `${CART_SERVICE_URL}/api/v1/carts/${cartId}/items/${productId}`,
    req.body,
    { headers: forwardHeaders(req) }
  );
  return response.data;
}

async function removeCartItem(req, cartId, productId) {
  const response = await axios.delete(
    `${CART_SERVICE_URL}/api/v1/carts/${cartId}/items/${productId}`,
    { headers: forwardHeaders(req) }
  );
  return response.data;
}

module.exports = {
  getMyCart,
  addItemToCart,
  updateCartItem,
  removeCartItem,
};