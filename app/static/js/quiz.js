/* ==========================================================
   QuizMind AI — Quiz Taking Screen
   ========================================================== */

document.addEventListener('DOMContentLoaded', () => {
  const app = document.getElementById('quizApp');
  if (!app) return;

  const questions = JSON.parse(app.getAttribute('data-questions'));
  const bookmarkedIds = new Set(JSON.parse(app.getAttribute('data-bookmarked')));
  const submitUrl = app.getAttribute('data-submit-url');
  const timeLimitMinutes = parseInt(app.getAttribute('data-time-limit'), 10) || 30;

  const state = {
    current: 0,
    answers: {},        // question_id -> label
    markedForReview: new Set(),
    startedAt: Date.now(),
    remainingSeconds: timeLimitMinutes * 60,
    warned10: false,
    warned5: false,
    warned1: false,
    submitted: false,
  };

  const dotsTrack = document.getElementById('questionDots');
  const questionCardWrap = document.getElementById('questionCardWrap');
  const timerEl = document.getElementById('quizTimer');
  const progressLabel = document.getElementById('progressLabel');
  const prevBtn = document.getElementById('prevBtn');
  const nextBtn = document.getElementById('nextBtn');
  const markReviewBtn = document.getElementById('markReviewBtn');
  const submitBtn = document.getElementById('submitQuizBtn');
  const confirmSubmitModalEl = document.getElementById('confirmSubmitModal');
  const confirmSubmitModal = confirmSubmitModalEl ? new bootstrap.Modal(confirmSubmitModalEl) : null;
  const finalSubmitBtn = document.getElementById('finalSubmitBtn');
  const answeredCountEl = document.getElementById('answeredCount');
  const unansweredCountEl = document.getElementById('unansweredCount');

  function renderDots() {
    dotsTrack.innerHTML = '';
    questions.forEach((q, idx) => {
      const dot = document.createElement('div');
      let cls = 'q-dot';
      if (idx === state.current) cls += ' current';
      else if (state.markedForReview.has(q.id)) cls += ' review';
      else if (state.answers[q.id]) cls += ' answered';
      dot.className = cls;
      dot.textContent = idx + 1;
      dot.addEventListener('click', () => { state.current = idx; render(); });
      dotsTrack.appendChild(dot);
    });
  }

  function renderQuestion() {
    const q = questions[state.current];
    const isBookmarked = bookmarkedIds.has(q.id);
    const optionsHtml = q.options.map((opt) => {
      const selected = state.answers[q.id] === opt.label;
      return `
        <div class="option-choice ${selected ? 'selected' : ''}" data-label="${opt.label}">
          <div class="option-label">${opt.label}</div>
          <div>${opt.text}</div>
        </div>`;
    }).join('');

    questionCardWrap.innerHTML = `
      <div class="qm-card question-card fade-in-up">
        <div class="d-flex justify-content-between align-items-start mb-2">
          <span class="qm-pill"><i class="bi bi-patch-question"></i> Question ${state.current + 1} of ${questions.length}</span>
          <button type="button" class="btn btn-qm-ghost btn-sm-pill bookmark-toggle-btn" data-qid="${q.id}">
            <i class="bi ${isBookmarked ? 'bi-bookmark-fill text-primary-qm' : 'bi-bookmark'}"></i>
          </button>
        </div>
        <div class="question-text">${q.question}</div>
        <div class="options-list">${optionsHtml}</div>
      </div>
    `;

    questionCardWrap.querySelectorAll('.option-choice').forEach((el) => {
      el.addEventListener('click', () => {
        state.answers[q.id] = el.getAttribute('data-label');
        renderQuestion();
        renderDots();
        updateCounts();
      });
    });

    const bookmarkBtn = questionCardWrap.querySelector('.bookmark-toggle-btn');
    bookmarkBtn.addEventListener('click', async () => {
      const res = await qmFetch('/bookmarks/toggle', {
        method: 'POST',
        body: JSON.stringify({ question_id: q.id }),
      });
      if (res.data) {
        if (res.data.bookmarked) bookmarkedIds.add(q.id); else bookmarkedIds.delete(q.id);
        showToast(res.data.message, 'success');
        renderQuestion();
      }
    });

    markReviewBtn.classList.toggle('active', state.markedForReview.has(q.id));
    markReviewBtn.innerHTML = state.markedForReview.has(q.id)
      ? '<i class="bi bi-flag-fill"></i> Marked for Review'
      : '<i class="bi bi-flag"></i> Mark for Review';

    prevBtn.disabled = state.current === 0;
    nextBtn.style.display = state.current === questions.length - 1 ? 'none' : 'inline-flex';
    submitBtn.style.display = state.current === questions.length - 1 ? 'inline-flex' : 'none';
    progressLabel.textContent = `Question ${state.current + 1} of ${questions.length}`;
  }

  function updateCounts() {
    const answered = Object.keys(state.answers).length;
    answeredCountEl.textContent = answered;
    unansweredCountEl.textContent = questions.length - answered;
  }

  function render() {
    renderDots();
    renderQuestion();
  }

  prevBtn.addEventListener('click', () => { if (state.current > 0) { state.current--; render(); } });
  nextBtn.addEventListener('click', () => { if (state.current < questions.length - 1) { state.current++; render(); } });
  markReviewBtn.addEventListener('click', () => {
    const qid = questions[state.current].id;
    if (state.markedForReview.has(qid)) state.markedForReview.delete(qid);
    else state.markedForReview.add(qid);
    render();
  });

  submitBtn.addEventListener('click', () => {
    updateCounts();
    if (confirmSubmitModal) confirmSubmitModal.show();
  });

  async function doSubmit(timedOut = false) {
    if (state.submitted) return;
    state.submitted = true;
    const timeTaken = Math.round((Date.now() - state.startedAt) / 1000);
    const res = await qmFetch(submitUrl, {
      method: 'POST',
      body: JSON.stringify({
        answers: state.answers,
        time_taken_seconds: timeTaken,
        timed_out: timedOut,
      }),
    });
    if (res.data && res.data.redirect) {
      window.location.href = res.data.redirect;
    } else {
      showToast('Something went wrong while submitting. Please try again.', 'danger');
      state.submitted = false;
    }
  }

  if (finalSubmitBtn) {
    finalSubmitBtn.addEventListener('click', () => doSubmit(false));
  }

  // ---------------- Timer ----------------
  function formatTime(totalSeconds) {
    const s = Math.max(0, totalSeconds);
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;
  }

  function tickTimer() {
    if (state.submitted) return;
    state.remainingSeconds = Math.max(0, state.remainingSeconds - 1);
    timerEl.innerHTML = `<i class="bi bi-stopwatch"></i> ${formatTime(state.remainingSeconds)}`;

    if (state.remainingSeconds <= 60) {
      timerEl.classList.add('danger');
      timerEl.classList.remove('warning');
      if (!state.warned1) { state.warned1 = true; showToast('Only 1 minute remaining!', 'danger'); }
    } else if (state.remainingSeconds <= 300) {
      timerEl.classList.add('warning');
      if (!state.warned5) { state.warned5 = true; showToast('5 minutes remaining.', 'warning'); }
    } else if (state.remainingSeconds <= 600) {
      if (!state.warned10) { state.warned10 = true; showToast('10 minutes remaining.', 'warning'); }
    }

    if (state.remainingSeconds <= 0) {
      clearInterval(timerInterval);
      showToast('Time is up! Submitting your quiz automatically.', 'danger');
      doSubmit(true);
      return;
    }
  }

  const timerInterval = setInterval(tickTimer, 1000);
  timerEl.innerHTML = `<i class="bi bi-stopwatch"></i> ${formatTime(state.remainingSeconds)}`;

  // Warn before leaving the page mid-quiz
  window.addEventListener('beforeunload', (e) => {
    if (!state.submitted) {
      e.preventDefault();
      e.returnValue = '';
    }
  });

  updateCounts();
  render();
});
