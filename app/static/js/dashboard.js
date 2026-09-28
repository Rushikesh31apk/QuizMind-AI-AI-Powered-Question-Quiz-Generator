/* ==========================================================
   QuizMind AI — Dashboard / Analytics charts
   Uses Chart.js (loaded via CDN on pages that need it)
   ========================================================== */

document.addEventListener('DOMContentLoaded', () => {
  const PRIMARY = '#16C784';
  const PRIMARY_DARK = '#087F5B';
  const palette = ['#16C784', '#087F5B', '#5DD9A8', '#F5A524', '#3B82F6', '#E4453A', '#8B5CF6'];

  // ---------------- Generic Chart.js renderer ----------------
  document.querySelectorAll('[data-chart]').forEach((canvas) => {
    if (typeof Chart === 'undefined') return;
    const type = canvas.getAttribute('data-chart');
    const labels = JSON.parse(canvas.getAttribute('data-labels') || '[]');
    const values = JSON.parse(canvas.getAttribute('data-values') || '[]');
    const label = canvas.getAttribute('data-label') || '';
    const multi = canvas.getAttribute('data-multi-colors') === 'true';

    let datasetConfig = {
      label,
      data: values,
      backgroundColor: multi ? palette : (type === 'line' ? 'rgba(22,199,132,0.12)' : PRIMARY),
      borderColor: PRIMARY_DARK,
      borderWidth: type === 'line' ? 3 : 0,
      borderRadius: type === 'bar' ? 10 : 0,
      tension: 0.35,
      fill: type === 'line',
      pointBackgroundColor: PRIMARY_DARK,
      pointRadius: type === 'line' ? 4 : 0,
    };

    new Chart(canvas.getContext('2d'), {
      type: type === 'doughnut' ? 'doughnut' : type,
      data: { labels, datasets: [datasetConfig] },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: type === 'doughnut', position: 'bottom' },
        },
        scales: type === 'doughnut' ? {} : {
          y: { beginAtZero: true, grid: { color: '#F0F4F2' }, ticks: { color: '#667085' } },
          x: { grid: { display: false }, ticks: { color: '#667085' } },
        },
      },
    });
  });

  // ---------------- Circular score ring ----------------
  document.querySelectorAll('.score-ring-svg').forEach((svg) => {
    const pct = parseFloat(svg.getAttribute('data-percentage')) || 0;
    const circle = svg.querySelector('.score-ring-progress');
    if (!circle) return;
    const radius = circle.r.baseVal.value;
    const circumference = 2 * Math.PI * radius;
    circle.style.strokeDasharray = `${circumference} ${circumference}`;
    circle.style.strokeDashoffset = circumference;
    requestAnimationFrame(() => {
      const offset = circumference - (pct / 100) * circumference;
      circle.style.strokeDashoffset = offset;
    });
  });

  // ---------------- Mobile sidebar toggle (fallback if not using bootstrap offcanvas attr) ----------------
  const sidebarToggle = document.getElementById('sidebarToggleBtn');
  const offcanvasEl = document.getElementById('mobileSidebar');
  if (sidebarToggle && offcanvasEl && typeof bootstrap !== 'undefined') {
    sidebarToggle.addEventListener('click', () => {
      const oc = bootstrap.Offcanvas.getOrCreateInstance(offcanvasEl);
      oc.show();
    });
  }
});
