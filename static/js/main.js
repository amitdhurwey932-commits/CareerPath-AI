/**
 * CareerPath AI — Main JavaScript
 * Handles UI interactions, tooltips, and helper utilities.
 * No API keys or credentials are included here.
 */

document.addEventListener('DOMContentLoaded', function () {

  // ── Bootstrap tooltips ──────────────────────────────────
  const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltipEls.forEach(function (el) {
    new bootstrap.Tooltip(el, { placement: 'top' });
  });

  // ── Auto-dismiss flash alerts after 5 seconds ──────────
  const alerts = document.querySelectorAll('.alert.fade.show');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  // ── Active nav link highlight ───────────────────────────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.navbar-nav .nav-link').forEach(function (link) {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });

  // ── Smooth scroll for anchor links ──────────────────────
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ── Skill level radio button: update bar on load ────────
  updateAllSkillBars();

  // ── Form validation: prevent empty submissions ──────────
  const forms = document.querySelectorAll('form[novalidate]');
  forms.forEach(function (form) {
    form.addEventListener('submit', function (e) {
      if (!form.checkValidity()) {
        e.preventDefault();
        e.stopPropagation();
        form.classList.add('was-validated');
        const firstInvalid = form.querySelector(':invalid');
        if (firstInvalid) firstInvalid.focus();
      }
    });
  });

  // ── Password strength indicator ──────────────────────────
  const passwordInput = document.getElementById('password');
  if (passwordInput) {
    passwordInput.addEventListener('input', updatePasswordStrength);
  }

  // ── Character counter for textareas ─────────────────────
  document.querySelectorAll('textarea[maxlength]').forEach(function (ta) {
    const max = parseInt(ta.getAttribute('maxlength'));
    const counter = document.createElement('div');
    counter.className = 'form-text text-end mt-1';
    counter.textContent = `0 / ${max}`;
    ta.parentNode.insertBefore(counter, ta.nextSibling);
    ta.addEventListener('input', function () {
      counter.textContent = `${this.value.length} / ${max}`;
      counter.style.color = this.value.length > max * 0.9 ? '#dc3545' : '';
    });
  });

});

// ── Skill bar initialisation ─────────────────────────────
function updateAllSkillBars() {
  const levelMap = { 'not_learned': 0, 'basic': 33, 'intermediate': 66, 'advanced': 100 };
  const colorMap = {
    'not_learned': 'bg-secondary',
    'basic': 'bg-warning',
    'intermediate': 'bg-info',
    'advanced': 'bg-success'
  };

  document.querySelectorAll('.step-checkbox, input[type="radio"][name^="skill_"]:checked').forEach(function (cb) {
    if (!cb.checked) return;
    const container = cb.closest('.p-3');
    if (!container) return;
    const bar = container.querySelector('.progress-bar');
    if (bar && levelMap[cb.value] !== undefined) {
      bar.style.width = levelMap[cb.value] + '%';
      Object.values(colorMap).forEach(c => bar.classList.remove(c));
      bar.classList.add(colorMap[cb.value]);
    }
  });
}

// ── Password strength visual feedback ──────────────────
function updatePasswordStrength(e) {
  const pw = e.target.value;
  let strength = 0;
  if (pw.length >= 8) strength++;
  if (/[A-Z]/.test(pw)) strength++;
  if (/[0-9]/.test(pw)) strength++;
  if (/[^A-Za-z0-9]/.test(pw)) strength++;

  let indicator = e.target.parentNode.querySelector('.pw-strength');
  if (!indicator) {
    indicator = document.createElement('div');
    indicator.className = 'pw-strength mt-1';
    e.target.parentNode.parentNode.appendChild(indicator);
  }

  const labels = ['', 'Weak', 'Fair', 'Good', 'Strong'];
  const colors = ['', 'danger', 'warning', 'info', 'success'];
  if (pw.length === 0) {
    indicator.innerHTML = '';
  } else {
    indicator.innerHTML = `<div class="progress" style="height:4px;"><div class="progress-bar bg-${colors[strength]}" style="width:${strength * 25}%"></div></div><small class="text-${colors[strength]}">${labels[strength]}</small>`;
  }
}

// ── Utility: Copy text to clipboard ──────────────────────
function copyToClipboard(text) {
  if (navigator.clipboard) {
    return navigator.clipboard.writeText(text);
  }
  // Fallback
  const el = document.createElement('textarea');
  el.value = text;
  el.style.position = 'fixed';
  el.style.opacity = '0';
  document.body.appendChild(el);
  el.select();
  document.execCommand('copy');
  document.body.removeChild(el);
  return Promise.resolve();
}
