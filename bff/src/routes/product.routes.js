const express = require('express');
const router = express.Router();
const productController = require('../controller/product.controller');

router.get('/', productController.listProducts);
router.get('/:productId', productController.getProductById);
router.post('/', productController.submitProduct);
router.patch('/:productId', productController.updateProduct);
router.patch('/:productId/review', productController.reviewProduct);
router.patch('/:productId/deactivate', productController.deactivateProduct);

module.exports = router;