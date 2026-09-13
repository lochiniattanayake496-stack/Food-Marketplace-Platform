const express = require('express');
const router = express.Router();
const cartController = require('../controller/cart.controller');

router.get('/', cartController.getMyCart);
router.post('/:cartId/items', cartController.addItemToCart);
router.patch('/:cartId/items/:productId', cartController.updateCartItem);
router.delete('/:cartId/items/:productId', cartController.removeCartItem);

module.exports = router;