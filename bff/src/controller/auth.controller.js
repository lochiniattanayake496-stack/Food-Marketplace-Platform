const authService = require('../service/auth.service');

async function login(req, res, next) {
  try {
    const { userId, role } = req.body;
    const result = await authService.login(userId, role);
    res.status(200).json(result);
  } catch (err) {
    next(err);
  }
}

module.exports = { login };