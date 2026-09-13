const productService = require('../service/product.service');

/**
 * Normalizes errors from the backend service (which returns
 * { detail: "..." } per its own global exception handler) into a
 * consistent shape for the frontend, and forwards the correct status
 * code — the BFF's "error normalization" responsibility per the
 * project guide, instead of crashing with a raw 500.
 */
function handleError(err, res) {
  if (err.response) {
    const status = err.response.status;
    const detail = err.response.data?.detail || 'An error occurred';
    return res.status(status).json({ error: detail });
  }
  console.error('[Product Controller] Unexpected error:', err.message);
  return res.status(500).json({ error: 'An unexpected error occurred' });
}

async function listProducts(req, res) {
  try {
    const products = await productService.listProducts(req);
    res.status(200).json(products);
  } catch (err) {
    handleError(err, res);
  }
}

async function getProductById(req, res) {
  try {
    const product = await productService.getProductById(req, req.params.productId);
    res.status(200).json(product);
  } catch (err) {
    handleError(err, res);
  }
}

async function submitProduct(req, res) {
  try {
    const product = await productService.submitProduct(req);
    res.status(201).json(product);
  } catch (err) {
    handleError(err, res);
  }
}

async function updateProduct(req, res) {
  try {
    const product = await productService.updateProduct(req, req.params.productId);
    res.status(200).json(product);
  } catch (err) {
    handleError(err, res);
  }
}

async function reviewProduct(req, res) {
  try {
    const product = await productService.reviewProduct(req, req.params.productId);
    res.status(200).json(product);
  } catch (err) {
    handleError(err, res);
  }
}

async function deactivateProduct(req, res) {
  try {
    const result = await productService.deactivateProduct(req, req.params.productId);
    res.status(200).json(result);
  } catch (err) {
    handleError(err, res);
  }
}

module.exports = {
  listProducts,
  getProductById,
  submitProduct,
  updateProduct,
  reviewProduct,
  deactivateProduct,
};