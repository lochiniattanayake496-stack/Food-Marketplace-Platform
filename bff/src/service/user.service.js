const axios = require('axios');

const USER_SERVICE_URL = process.env.USER_SERVICE_URL || 'http://127.0.0.1:8002';

function forwardHeaders(req) {
  const headers = {};
  if (req.headers['x-user-id']) headers['X-User-Id'] = req.headers['x-user-id'];
  if (req.headers['x-user-role']) headers['X-User-Role'] = req.headers['x-user-role'];
  return headers;
}

async function listUsers(req) {
  const response = await axios.get(`${USER_SERVICE_URL}/api/v1/users`, {
    headers: forwardHeaders(req),
    params: req.query, // forwards page/limit
  });
  return response.data;
}

async function syncUser(req) {
  const response = await axios.post(`${USER_SERVICE_URL}/api/v1/users`, req.body, {
    headers: forwardHeaders(req),
  });
  return response.data;
}

async function getUser(req, userId) {
  const response = await axios.get(`${USER_SERVICE_URL}/api/v1/users/${userId}`, {
    headers: forwardHeaders(req),
  });
  return response.data;
}

async function updateUser(req, userId) {
  const response = await axios.patch(`${USER_SERVICE_URL}/api/v1/users/${userId}`, req.body, {
    headers: forwardHeaders(req),
  });
  return response.data;
}

async function deactivateUser(req, userId) {
  const response = await axios.patch(`${USER_SERVICE_URL}/api/v1/users/${userId}/deactivate`, {}, {
    headers: forwardHeaders(req),
  });
  return response.data;
}

module.exports = {
  listUsers,
  syncUser,
  getUser,
  updateUser,
  deactivateUser,
};