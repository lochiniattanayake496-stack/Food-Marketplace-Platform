const express = require('express');
const cors = require('cors');
const{ createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const PORT = process.env.PORT || 5000;

const PRODUCT_SERVICE_URL = process.env.PRODUCT_SERVICE_URL || 'http://localhost:8000';
const USER_SERVICE_URL = process.env.USER_SERVICE_URL || 'http://localhost:8001';
const CART_SERVICE_URL = process.env.CART_SERVICE_URL || 'http://localhost:8002';

app.use(cors());

//logging middleware
app.use((req, res, next) => {
    console.log(`[BFF Proxy] ${req.method} ${req.url}`);
    next();
});

//Proxy Rules

app.use(
    ['/api/v1/products', '/api/v1/approvals'],
    createProxyMiddleware({
        target: PRODUCT_SERVICE_URL,
        changeOrigin: true,
        onError: (err, req, res) => {
            res.status(503).json({error:'Product Service Unavailable '});
        }
    })
);

app.use(
    ['/api/v1/users'], 
    createProxyMiddleware({
        target: USER_SERVICE_URL,
        changeOrigin: true,
        onError: (err, req, res) => {
            res.status(503).json({error:'User Service Unavailable '});
        }
    })
);

app.use(
    ['/api/v1/cart'], 
    createProxyMiddleware({
        target: CART_SERVICE_URL,
        changeOrigin: true,
        onError: (err, req, res) => {
            res.status(503).json({error:'Cart Service Unavailable '});
        }   
    })
);

app.get('/health', (req, res) => {
    res.json({status: 'UP', service: 'Node.js BFF Gateway'});
});

app.listen(PORT, () => {
    console.log(`[BFF Gateway] Running on http://localhost:${PORT}`);
});