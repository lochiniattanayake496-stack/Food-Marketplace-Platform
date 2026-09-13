/**
 * STUB — Cognito is not yet fully wired into a login flow. This does
 * NOT perform real authentication. It exists to give the "auth"
 * domain a real route/controller/service shape, matching
 * product/cart/user, so the structure is in place.
 *
 * Note: real login for this project currently happens via Cognito's
 * Hosted UI (browser) + a token exchange — not through this endpoint.
 * This stub is a placeholder for a future direct login API if needed.
 */

async function login(userId, role) {
  if (!userId || !role) {
    const error = new Error('userId and role are required');
    error.statusCode = 400;
    throw error;
  }

  return {
    userId,
    role,
    token: `stub-token-for-${userId}`,
  };
}

module.exports = { login };