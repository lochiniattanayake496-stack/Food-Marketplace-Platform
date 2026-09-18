const TOKEN_KEY = 'cognito_access_token';

export function setToken(token) {
  if (token) sessionStorage.setItem(TOKEN_KEY, token);
}

export function getToken() {
  return sessionStorage.getItem(TOKEN_KEY);
}