import React, { useEffect, useState } from 'react';
import { setToken, setUser } from './auth';
import SupplierDashboardScreen from './screens/SupplierDashboardScreen';
import './styles/App.css';

export default function App(props) {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    // Normal path: single-spa passes token + user via customProps (see
    // root/src/single-spa-config.js). Fallback: ?token= query param
    // for isolated standalone testing outside the shell.
    let token = props.token;
    let user = props.user;
    if (!token) {
      const params = new URLSearchParams(window.location.search);
      token = params.get('token');
    }
    if (token) setToken(token);
    if (user) setUser(user);
    setReady(true);
  }, [props.token, props.user]);

  if (!ready) return null;

  return <SupplierDashboardScreen />;
}