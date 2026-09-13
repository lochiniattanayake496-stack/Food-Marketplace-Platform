const express = require('express');
const router = express.Router();
const userController = require('../controller/user.controller');

router.get('/', userController.listUsers);
router.post('/', userController.syncUser);
router.get('/:userId', userController.getUser);
router.patch('/:userId', userController.updateUser);
router.patch('/:userId/deactivate', userController.deactivateUser);

module.exports = router;