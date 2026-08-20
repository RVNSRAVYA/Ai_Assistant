/**
 * SmartCode AI - API Configuration
 * Auto-detects backend URL for localhost, live-server, and mobile (network) access.
 */

function getApiBase() {
  // file:// = opened directly, always use localhost
  if (window.location.protocol === 'file:') {
    return 'http://localhost:8000';
  }
  // Live Server ports → backend is on port 8000
  const devPorts = ['5500', '5501', '3000', '4000', '8080'];
  if (devPorts.includes(window.location.port)) {
    return `${window.location.protocol}//${window.location.hostname}:8000`;
  }
  // FastAPI is serving this page directly (same origin)
  return window.location.origin;
}

// Backwards-compatible alias
function getApiUrl(endpoint) {
  return `${getApiBase()}${endpoint}`;
}

function getPageUrl(page) {
  if (window.location.protocol === 'file:') {
    return `${page}.html`;
  }

  const routes = {
    home: '/',
    assistant: '/assistant',
    editor: '/editor',
    about: '/about'
  };
  return routes[page] || '/';
}
