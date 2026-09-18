const TOKEN_KEY = 'cognito_access_token';
const USER_KEY = 'cognito_user';

export function setToken(token) {
  if (token) sessionStorage.setItem(TOKEN_KEY, token);
}

export function getToken() {
  return sessionStorage.getItem(TOKEN_KEY);
}

export function setUser(user) {
  if (user) sessionStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function getUser() {
  const raw = sessionStorage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
}