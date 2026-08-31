const express = require('express');
const cors = require('cors');
const { createProxyMiddleware } = require('http-proxy-middleware');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 8000;

const PRODUCT_SERVICE_URL = process.env.PRODUCT_SERVICE_URL || 'http://127.0.0.1:8001';
const USER_SERVICE_URL = process.env.USER_SERVICE_URL || 'http://127.0.0.1:8002';
const CART_SERVICE_URL = process.env.CART_SERVICE_URL || 'http://127.0.0.1:8003';

app.use(cors());

// Preflight OPTIONS handling
app.use((req, res, next) => {
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  next();
});

// Forward context headers & handle post/patch body re-streaming
const onProxyReq = (proxyReq, req, res) => {
  if (req.headers['x-user-id']) proxyReq.setHeader('x-user-id', req.headers['x-user-id']);
  if (req.headers['x-user-role']) proxyReq.setHeader('x-user-role', req.headers['x-user-role']);

  if (req.body && Object.keys(req.body).length) {
    const bodyData = JSON.stringify(req.body);
    proxyReq.setHeader('Content-Type', 'application/json');
    proxyReq.setHeader('Content-Length', Buffer.byteLength(bodyData));
    proxyReq.write(bodyData);
  }
};

// --- PROXY ROUTES ---

// 1. Products Microservice Proxy
app.use(
  '/api/v1/products',
  createProxyMiddleware({
    target: PRODUCT_SERVICE_URL,
    changeOrigin: true,
    pathRewrite: (path, req) => req.originalUrl,
    onProxyReq,
  })
);

// 2. Users Microservice Proxy
app.use(
  '/api/v1/users',
  createProxyMiddleware({
    target: USER_SERVICE_URL,
    changeOrigin: true,
    pathRewrite: (path, req) => req.originalUrl,
    onProxyReq,
  })
);

// 3. Carts Microservice Proxy
app.use(
  '/api/v1/carts',
  createProxyMiddleware({
    target: CART_SERVICE_URL,
    changeOrigin: true,
    pathRewrite: (path, req) => req.originalUrl,
    onProxyReq,
  })
);

// Local body parsers (Must stay AFTER proxy routes)
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.get('/health', (req, res) => {
  res.json({ status: 'UP', service: 'Node.js BFF Gateway' });
});

app.listen(PORT, () => {
  console.log(`[BFF Gateway] Running on http://localhost:${PORT}`);
});