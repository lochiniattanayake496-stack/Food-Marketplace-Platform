import React from 'react';
import ReactDOMClient from 'react-dom/client';
import singleSpaReact from 'single-spa-react';
import App from './App.jsx';
import './styles/index.css';

const lifecycles = singleSpaReact({
  React,
  ReactDOMClient,
  rootComponent: App,
  errorBoundary(err, info, props) {
    return <div style={{ padding: '1rem', color: 'red' }}>Supplier MFE failed to load: {err.message}</div>;
  },
  domElementGetter: () => document.getElementById('mfe-container'),
});

export const { bootstrap, mount, unmount } = lifecycles;