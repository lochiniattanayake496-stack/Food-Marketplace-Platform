const express = require('express');
const router = express.Router();
const authController = require('../controller/auth.controller');

// STUB login endpoint — see auth.service.js for details.
router.post('/login', authController.login);

module.exports = router;