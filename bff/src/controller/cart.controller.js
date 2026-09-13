const cartService = require('../service/cart.service');

function handleError(err, res) {
  if (err.response) {
    const status = err.response.status;
    const detail = err.response.data?.detail || 'An error occurred';
    return res.status(status).json({ error: detail });
  }
  console.error('[Cart Controller] Unexpected error:', err.message);
  return res.status(500).json({ error: 'An unexpected error occurred' });
}

async function getMyCart(req, res) {
  try {
    const cart = await cartService.getMyCart(req);
    res.status(200).json(cart);
  } catch (err) {
    handleError(err, res);
  }
}

async function addItemToCart(req, res) {
  try {
    const cart = await cartService.addItemToCart(req, req.params.cartId);
    res.status(200).json(cart);
  } catch (err) {
    handleError(err, res);
  }
}

async function updateCartItem(req, res) {
  try {
    const cart = await cartService.updateCartItem(req, req.params.cartId, req.params.productId);
    res.status(200).json(cart);
  } catch (err) {
    handleError(err, res);
  }
}

async function removeCartItem(req, res) {
  try {
    const cart = await cartService.removeCartItem(req, req.params.cartId, req.params.productId);
    res.status(200).json(cart);
  } catch (err) {
    handleError(err, res);
  }
}

module.exports = {
  getMyCart,
  addItemToCart,
  updateCartItem,
  removeCartItem,
};