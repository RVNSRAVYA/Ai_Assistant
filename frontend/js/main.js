/**
 * SmartCode AI - Global Utilities
 * Mobile nav, toast alerts, server health badge
 */

// ─── Mobile Nav Toggle ────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('menu-toggle');
  const navLinks = document.getElementById('nav-links');

  if (toggle && navLinks) {
    toggle.addEventListener('click', () => {
      navLinks.classList.toggle('open');
      toggle.textContent = navLinks.classList.contains('open') ? '✕' : '☰';
    });

    // Close nav when a link is clicked
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('open');
        toggle.textContent = '☰';
      });
    });
  }

  // Check server health
  checkServerHealth();
});

// ─── Server Health Badge ──────────────────────────────────────────────────────
async function checkServerHealth() {
  const badge = document.getElementById('server-status-badge');
  if (!badge) return;

  try {
    const res = await fetch(`${getApiBase()}/api/health`, { signal: AbortSignal.timeout(4000) });
    if (res.ok) {
      badge.textContent = '● Online';
      badge.className = 'status-badge badge-success';
    } else {
      throw new Error('Not OK');
    }
  } catch {
    badge.textContent = '● Offline';
    badge.className = 'status-badge badge-error';
  }
}

// ─── Toast Notifications ──────────────────────────────────────────────────────
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = `
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      gap: 10px;
    `;
    document.body.appendChild(container);
  }

  const colors = {
    success: '#10b981',
    error:   '#ef4444',
    warning: '#f59e0b',
    info:    '#6366f1'
  };

  const toast = document.createElement('div');
  toast.style.cssText = `
    background: #1e293b;
    color: #f8fafc;
    border: 1px solid ${colors[type] || colors.info};
    border-left: 4px solid ${colors[type] || colors.info};
    padding: 12px 18px;
    border-radius: 8px;
    font-size: 0.9rem;
    max-width: 320px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    animation: fadeInUp 0.3s ease;
  `;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.4s';
    setTimeout(() => toast.remove(), 400);
  }, 3000);
}
