import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './single-spa-config.js'; // registers + starts single-spa BEFORE React mounts
import './index.css';
import App from './App.jsx';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
);