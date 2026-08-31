const express = require('express');
const cors = require('cors');
const { createProxyMiddleware } = require('http-proxy-middleware');
const { verifyCognitoToken } = require('./middleware/auth');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

const PRODUCT_SERVICE_URL = process.env.PRODUCT_SERVICE_URL || 'http://localhost:8000';
const USER_SERVICE_URL = process.env.USER_SERVICE_URL || 'http://localhost:8001';
const CART_SERVICE_URL = process.env.CART_SERVICE_URL || 'http://localhost:8002';

app.use(cors());
app.use(verifyCognitoToken);

const onProxyReq = (proxyReq, req, res) => {
  if (req.headers['x-user-id']) {
    proxyReq.setHeader('x-user-id', req.headers['x-user-id']);
  }
  if (req.headers['x-user-role']) {
    proxyReq.setHeader('x-user-role', req.headers['x-user-role']);
  }
};

// --- PROXY ROUTE MAP ---

// 1. Product Service
app.use(
  ['/api/v1/products', '/api/v1/approvals'],
  createProxyMiddleware({
    target: PRODUCT_SERVICE_URL,
    changeOrigin: true,
    onProxyReq,
    onError: (err, req, res) => res.status(503).json({ error: 'Product Service unavailable.' })
  })
);

// 2. User Service
app.use(
  '/api/v1/users',
  createProxyMiddleware({
    target: USER_SERVICE_URL,
    changeOrigin: true,
    onProxyReq,
    onError: (err, req, res) => res.status(503).json({ error: 'User Service unavailable.' })
  })
);

// 3. Cart Service
app.use(
  '/api/v1/carts',
  createProxyMiddleware({
    target: CART_SERVICE_URL,
    changeOrigin: true,
    onProxyReq,
    onError: (err, req, res) => res.status(503).json({ error: 'Cart Service unavailable.' })
  })
);

app.get('/health', (req, res) => {
  res.json({ status: 'UP', service: 'Node.js BFF Gateway' });
});

app.listen(PORT, () => {
  console.log(`[BFF Gateway] Running on http://localhost:${PORT}`);
});