/* ==========================================================
   QuizMind AI — Shared JavaScript utilities
   ========================================================== */

// ---------------- CSRF helper ----------------
function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.getAttribute('content') : '';
}

/**
 * Wrapper around fetch() that automatically attaches the CSRF token
 * for state-changing requests and parses JSON responses.
 */
async function qmFetch(url, options = {}) {
  const opts = Object.assign({}, options);
  opts.headers = Object.assign({}, opts.headers);

  if (opts.body instanceof FormData) {
    opts.headers['X-CSRFToken'] = getCsrfToken();
  } else if (opts.body) {
    opts.headers['Content-Type'] = 'application/json';
    opts.headers['X-CSRFToken'] = getCsrfToken();
  } else if (opts.method && opts.method.toUpperCase() !== 'GET') {
    opts.headers['X-CSRFToken'] = getCsrfToken();
  }

  const response = await fetch(url, opts);
  let data = null;
  try { data = await response.json(); } catch (e) { data = null; }
  return { ok: response.ok, status: response.status, data };
}

// ---------------- Toast notifications ----------------
function showToast(message, category = 'success') {
  const stack = document.getElementById('toastStack');
  if (!stack) return;

  const icons = {
    success: 'bi-check-circle-fill',
    danger: 'bi-x-circle-fill',
    info: 'bi-info-circle-fill',
    warning: 'bi-exclamation-triangle-fill',
  };
  const icon = icons[category] || icons.success;

  const toast = document.createElement('div');
  toast.className = `qm-toast toast-${category}`;
  toast.innerHTML = `<i class="bi ${icon}" style="color:${category === 'danger' ? '#E4453A' : category === 'warning' ? '#F5A524' : category === 'info' ? '#3B82F6' : '#16C784'}"></i><span>${message}</span>`;
  stack.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = 'qmFadeOut 0.25s ease forwards';
    setTimeout(() => toast.remove(), 250);
  }, 4200);
}

document.addEventListener('DOMContentLoaded', () => {
  // Render flashed Flask messages as toasts
  const flashData = document.getElementById('flashData');
  if (flashData) {
    try {
      const messages = JSON.parse(flashData.getAttribute('data-messages'));
      messages.forEach(([category, message], i) => {
        setTimeout(() => showToast(message, category === 'error' ? 'danger' : category), i * 150);
      });
    } catch (e) { /* no-op */ }
  }

  // ---------------- FAQ accordion ----------------
  document.querySelectorAll('.faq-question').forEach((q) => {
    q.addEventListener('click', () => {
      q.closest('.faq-item').classList.toggle('open');
    });
  });

  // ---------------- Global search (navbar / topbar) ----------------
  const searchForms = document.querySelectorAll('.qm-search-form');
  searchForms.forEach((form) => {
    const clearBtn = form.querySelector('.qm-search-clear');
    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        const input = form.querySelector('input[name="q"]');
        if (input) input.value = '';
        input.focus();
      });
    }
  });

  // ---------------- Bootstrap tooltips ----------------
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((el) => {
    new bootstrap.Tooltip(el);
  });
});
