import React, { useEffect, useState } from 'react';
import { setToken, setUser } from './auth';
import StewardReviewScreen from './screens/StewardReviewScreen';
import './styles/App.css';

export default function App(props) {
  const [ready, setReady] = useState(false);

  useEffect(() => {
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

  return <StewardReviewScreen />;
}