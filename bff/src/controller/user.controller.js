const userService = require('../service/user.service');

function handleError(err, res) {
  if (err.response) {
    const status = err.response.status;
    const detail = err.response.data?.detail || 'An error occurred';
    return res.status(status).json({ error: detail });
  }
  console.error('[User Controller] Unexpected error:', err.message);
  return res.status(500).json({ error: 'An unexpected error occurred' });
}

async function listUsers(req, res) {
  try {
    const users = await userService.listUsers(req);
    res.status(200).json(users);
  } catch (err) {
    handleError(err, res);
  }
}

async function syncUser(req, res) {
  try {
    const user = await userService.syncUser(req);
    res.status(201).json(user);
  } catch (err) {
    handleError(err, res);
  }
}

async function getUser(req, res) {
  try {
    const user = await userService.getUser(req, req.params.userId);
    res.status(200).json(user);
  } catch (err) {
    handleError(err, res);
  }
}

async function updateUser(req, res) {
  try {
    const user = await userService.updateUser(req, req.params.userId);
    res.status(200).json(user);
  } catch (err) {
    handleError(err, res);
  }
}

async function deactivateUser(req, res) {
  try {
    const result = await userService.deactivateUser(req, req.params.userId);
    res.status(200).json(result);
  } catch (err) {
    handleError(err, res);
  }
}

module.exports = {
  listUsers,
  syncUser,
  getUser,
  updateUser,
  deactivateUser,
};