import React, { useEffect, useState } from 'react';
import { setToken } from './auth';
import StoreScreen from './screens/StoreScreen';
import './styles/App.css';

export default function App(props) {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    // Normal path: single-spa passes the token via customProps (see
    // root/src/single-spa-config.js). Fallback: if run standalone
    // (npm run dev directly in this folder, outside the shell) for
    // isolated manual testing, allow a ?token= query param instead.
    let token = props.token;
    if (!token) {
      const params = new URLSearchParams(window.location.search);
      token = params.get('token');
    }
    if (token) setToken(token);
    setReady(true);
  }, [props.token]);

  if (!ready) return null;

  return <StoreScreen />;
}