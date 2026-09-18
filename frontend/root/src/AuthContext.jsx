import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

const COGNITO_DOMAIN = 'https://eu-north-1c0qzx7phu.auth.eu-north-1.amazoncognito.com';
const CLIENT_ID = '1d5n0t9fnqdhj4brg2bpkuijo';
const REDIRECT_URI = 'http://localhost:3000';
const TOKEN_STORAGE_KEY = 'cognito_access_token';
const ID_TOKEN_STORAGE_KEY = 'cognito_id_token';

function base64UrlDecode(str) {
  str = str.replace(/-/g, '+').replace(/_/g, '/');
  while (str.length % 4) str += '=';
  return atob(str);
}

function decodeAccessToken(token) {
  const payload = token.split('.')[1];
  return JSON.parse(base64UrlDecode(payload));
}

function buildLoginUrl() {
  const params = new URLSearchParams({
    client_id: CLIENT_ID,
    response_type: 'code',
    scope: 'email openid phone',
    redirect_uri: REDIRECT_URI,
  });
  return `${COGNITO_DOMAIN}/login?${params.toString()}`;
}

async function exchangeCodeForToken(code) {
  const body = new URLSearchParams({
    grant_type: 'authorization_code',
    client_id: CLIENT_ID,
    code,
    redirect_uri: REDIRECT_URI,
  });

  const response = await fetch(`${COGNITO_DOMAIN}/oauth2/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString(),
  });

  if (!response.ok) {
    throw new Error(`Token exchange failed: ${response.status}`);
  }

  return response.json();
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const initStarted = React.useRef(false);

  useEffect(() => {
    if (initStarted.current) return;
    initStarted.current = true;
    initAuth();
  }, []);

  async function initAuth() {
    const existingToken = sessionStorage.getItem(TOKEN_STORAGE_KEY);
    const existingIdToken = sessionStorage.getItem(ID_TOKEN_STORAGE_KEY);
    if (existingToken) {
      try {
        const decoded = decodeAccessToken(existingToken);
        if (decoded.exp * 1000 > Date.now()) {
          const idTokenDecoded = existingIdToken ? decodeAccessToken(existingIdToken) : null;
          applyToken(existingToken, decoded, idTokenDecoded);
          setLoading(false);
          return;
        }
        sessionStorage.removeItem(TOKEN_STORAGE_KEY);
        sessionStorage.removeItem(ID_TOKEN_STORAGE_KEY);
      } catch {
        sessionStorage.removeItem(TOKEN_STORAGE_KEY);
        sessionStorage.removeItem(ID_TOKEN_STORAGE_KEY);
      }
    }

    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    if (code) {
      try {
        const tokens = await exchangeCodeForToken(code);
        const decoded = decodeAccessToken(tokens.access_token);
        const idTokenDecoded = decodeAccessToken(tokens.id_token);
        sessionStorage.setItem(TOKEN_STORAGE_KEY, tokens.access_token);
        sessionStorage.setItem(ID_TOKEN_STORAGE_KEY, tokens.id_token);
        applyToken(tokens.access_token, decoded, idTokenDecoded);
        window.history.replaceState({}, document.title, '/');
      } catch (err) {
        console.error('Login failed during code exchange:', err);
      }
      setLoading(false);
      return;
    }

    window.location.href = buildLoginUrl();
  }

  function applyToken(accessToken, decoded, idTokenDecoded) {
    setToken(accessToken);
    const role = decoded['cognito:groups'] ? decoded['cognito:groups'][0] : 'Customer';
    setUser({
      id: decoded.sub,
      email: idTokenDecoded?.email || decoded.sub,
      role,
    });
  }

  function logout() {
    sessionStorage.removeItem(TOKEN_STORAGE_KEY);
    sessionStorage.removeItem(ID_TOKEN_STORAGE_KEY);
    setUser(null);
    setToken(null);
    const params = new URLSearchParams({
      client_id: CLIENT_ID,
      logout_uri: REDIRECT_URI,
    });
    window.location.href = `${COGNITO_DOMAIN}/logout?${params.toString()}`;
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);