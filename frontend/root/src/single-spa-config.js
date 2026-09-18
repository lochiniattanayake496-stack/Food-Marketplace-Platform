import { registerApplication, start } from 'single-spa';

function getToken() {
  return sessionStorage.getItem('cognito_access_token');
}

function decodeIdToken() {
  const idToken = sessionStorage.getItem('cognito_id_token');
  if (!idToken) return null;
  try {
    const payload = idToken.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    return JSON.parse(atob(payload));
  } catch {
    return null;
  }
}

// customProps is read fresh on every mount, so this always reflects the
// latest token/user from sessionStorage without needing to re-register
// or synchronize with React state in the shell.
function buildCustomProps() {
  const decoded = decodeIdToken();
  return {
    token: getToken(),
    user: decoded
      ? { id: decoded.sub, email: decoded.email, role: decoded['cognito:groups']?.[0] || 'Customer' }
      : null,
  };
}

registerApplication({
  name: 'customer-mfe',
  app: () => import('http://localhost:3001/src/main.jsx'),
  activeWhen: (location) => location.pathname.startsWith('/customer'),
  customProps: buildCustomProps,
});

registerApplication({
  name: 'supplier-mfe',
  app: () => import('http://localhost:3002/src/main.jsx'),
  activeWhen: (location) => location.pathname.startsWith('/supplier'),
  customProps: buildCustomProps,
});

registerApplication({
  name: 'steward-mfe',
  app: () => import('http://localhost:3003/src/main.jsx'),
  activeWhen: (location) => location.pathname.startsWith('/steward'),
  customProps: buildCustomProps,
});

start();