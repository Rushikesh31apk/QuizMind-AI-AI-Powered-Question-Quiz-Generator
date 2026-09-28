/* ==========================================================
   QuizMind AI — Admin Panel JavaScript
   ========================================================== */

document.addEventListener('DOMContentLoaded', () => {

  // ---------------- Confirm-before-submit for delete forms ----------------
  document.querySelectorAll('form.confirm-delete').forEach((form) => {
    form.addEventListener('submit', (e) => {
      const msg = form.getAttribute('data-confirm') || 'Are you sure you want to delete this item?';
      if (!confirm(msg)) e.preventDefault();
    });
  });

  // ---------------- Edit-modal populate (generic) ----------------
  document.querySelectorAll('[data-edit-trigger]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const modalSelector = btn.getAttribute('data-edit-trigger');
      const modalEl = document.querySelector(modalSelector);
      if (!modalEl) return;
      const fields = JSON.parse(btn.getAttribute('data-edit-fields') || '{}');
      const actionUrl = btn.getAttribute('data-edit-action');
      const form = modalEl.querySelector('form');
      if (actionUrl && form) form.setAttribute('action', actionUrl);
      Object.entries(fields).forEach(([name, value]) => {
        const field = modalEl.querySelector(`[name="${name}"]`);
        if (field) field.value = value;
      });
      const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
      modal.show();
    });
  });

  // ================================================================
  // SYLLABUS ANALYZER
  // ================================================================
  const analyzeForm = document.getElementById('syllabusAnalyzeForm');
  if (analyzeForm) {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const previewWrap = document.getElementById('syllabusPreview');
    const importBtn = document.getElementById('importSyllabusBtn');
    let currentStructure = null;

    analyzeForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      analyzeBtn.disabled = true;
      analyzeBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Analyzing...';

      const formData = new FormData(analyzeForm);
      const res = await fetch(analyzeForm.getAttribute('action'), {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrfToken() },
        body: formData,
      });
      const data = await res.json();

      analyzeBtn.disabled = false;
      analyzeBtn.innerHTML = '<i class="bi bi-stars"></i> Analyze Syllabus';

      if (!data.success) {
        showToast(data.message || 'Could not analyze syllabus.', 'danger');
        previewWrap.innerHTML = '';
        return;
      }

      currentStructure = data.structure;
      renderPreview(currentStructure);
      showToast('Syllabus analyzed successfully. Review the detected structure below.', 'success');
    });

    function renderPreview(structure) {
      if (!structure.length) {
        previewWrap.innerHTML = '<p class="text-soft">No structure detected.</p>';
        importBtn.classList.add('d-none');
        return;
      }
      let html = '';
      structure.forEach((item, i) => {
        html += `
          <div class="qm-card p-3 mb-3">
            <div class="d-flex flex-wrap gap-2 mb-2">
              <span class="qm-pill"><i class="bi bi-mortarboard"></i> ${item.academic_year}</span>
              <span class="qm-pill"><i class="bi bi-calendar3"></i> ${item.semester}</span>
              <span class="qm-pill"><i class="bi bi-journal-bookmark"></i> ${item.subject} ${item.subject_code ? '(' + item.subject_code + ')' : ''}</span>
            </div>
            ${item.units.map((u) => `
              <div class="border rounded-3 p-2 mb-2" style="border-color:var(--qm-border)">
                <strong>${u.unit_name}</strong>
                <ul class="mb-0 mt-1 small text-soft">
                  ${u.topics.map((t) => `<li>${t}</li>`).join('')}
                </ul>
              </div>
            `).join('')}
          </div>`;
      });
      previewWrap.innerHTML = html;
      importBtn.classList.remove('d-none');
    }

    if (importBtn) {
      importBtn.addEventListener('click', async () => {
        if (!currentStructure) return;
        importBtn.disabled = true;
        importBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Importing...';
        const res = await qmFetch(importBtn.getAttribute('data-import-url'), {
          method: 'POST',
          body: JSON.stringify({ structure: currentStructure }),
        });
        importBtn.disabled = false;
        importBtn.innerHTML = '<i class="bi bi-cloud-arrow-up"></i> Import to Database';
        if (res.data && res.data.success) {
          showToast(res.data.message, 'success');
          previewWrap.innerHTML = '';
          importBtn.classList.add('d-none');
          document.getElementById('syllabusTextArea').value = '';
        } else {
          showToast((res.data && res.data.message) || 'Import failed.', 'danger');
        }
      });
    }

    const cancelBtn = document.getElementById('cancelPreviewBtn');
    if (cancelBtn) {
      cancelBtn.addEventListener('click', () => {
        currentStructure = null;
        previewWrap.innerHTML = '';
        importBtn.classList.add('d-none');
      });
    }
  }

  // ================================================================
  // AI QUESTION GENERATOR
  // ================================================================
  const genForm = document.getElementById('questionGenForm');
  if (genForm) {
    const genBtn = document.getElementById('generateBtn');
    const resultsWrap = document.getElementById('generatedQuestionsWrap');
    const saveBtn = document.getElementById('saveQuestionsBtn');
    let generatedQuestions = [];

    const subjectSelect = document.getElementById('genSubject');
    const chapterSelect = document.getElementById('genChapter');
    const topicSelect = document.getElementById('genTopic');

    async function loadChapters() {
      chapterSelect.innerHTML = '<option value="">Whole Subject</option>';
      topicSelect.innerHTML = '<option value="">Any Topic</option>';
      if (!subjectSelect.value) return;
      const res = await fetch(`/api/chapters?subject_id=${subjectSelect.value}`);
      const chapters = await res.json();
      chapters.forEach((c) => {
        chapterSelect.innerHTML += `<option value="${c.id}">${c.name}</option>`;
      });
    }
    async function loadTopics() {
      topicSelect.innerHTML = '<option value="">Any Topic</option>';
      if (!chapterSelect.value) return;
      const res = await fetch(`/api/topics?chapter_id=${chapterSelect.value}`);
      const topicsData = await res.json();
      topicsData.forEach((t) => {
        topicSelect.innerHTML += `<option value="${t.id}">${t.name}</option>`;
      });
    }
    if (subjectSelect) subjectSelect.addEventListener('change', loadChapters);
    if (chapterSelect) chapterSelect.addEventListener('change', loadTopics);

    genForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!subjectSelect.value) { showToast('Please select a subject.', 'danger'); return; }

      genBtn.disabled = true;
      genBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generating...';

      const payload = {
        subject_id: subjectSelect.value,
        chapter_id: chapterSelect.value || null,
        topic_id: topicSelect.value || null,
        difficulty: document.getElementById('genDifficulty').value,
        count: document.getElementById('genCount').value,
        question_type: document.getElementById('genType').value,
      };

      const res = await qmFetch(genForm.getAttribute('action'), {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      genBtn.disabled = false;
      genBtn.innerHTML = '<i class="bi bi-stars"></i> Generate Questions';

      if (!res.data || !res.data.success) {
        showToast((res.data && res.data.message) || 'Could not generate questions.', 'danger');
        return;
      }

      generatedQuestions = res.data.questions;
      renderGenerated(generatedQuestions, res.data.demo_mode);
      showToast(`${generatedQuestions.length} question(s) generated. Review before saving.`, 'success');
    });

    function renderGenerated(questions, demoMode) {
      if (!questions.length) {
        resultsWrap.innerHTML = '<p class="text-soft">No questions were generated.</p>';
        saveBtn.classList.add('d-none');
        return;
      }
      let banner = demoMode
        ? `<div class="qm-pill mb-3"><i class="bi bi-info-circle"></i> Demo mode: connect a real AI provider in .env for richer questions.</div>`
        : '';
      resultsWrap.innerHTML = banner + questions.map((q, i) => `
        <div class="qm-card p-3 mb-3">
          <div class="d-flex justify-content-between">
            <strong>Q${i + 1}. ${q.question}</strong>
            <span class="qm-badge qm-badge-${q.difficulty.toLowerCase()}">${q.difficulty}</span>
          </div>
          <ul class="mt-2 mb-2 small">
            ${q.options.map((opt, idx) => `<li class="${['A','B','C','D'][idx] === q.correct_answer ? 'text-primary-qm fw-bold' : ''}">${['A','B','C','D'][idx]}. ${opt}</li>`).join('')}
          </ul>
          <p class="small text-soft mb-0"><i class="bi bi-lightbulb"></i> ${q.explanation}</p>
        </div>
      `).join('');
      saveBtn.classList.remove('d-none');
    }

    if (saveBtn) {
      saveBtn.addEventListener('click', async () => {
        if (!generatedQuestions.length) return;
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Saving...';
        const res = await qmFetch(saveBtn.getAttribute('data-save-url'), {
          method: 'POST',
          body: JSON.stringify({
            subject_id: subjectSelect.value,
            chapter_id: chapterSelect.value || null,
            topic_id: topicSelect.value || null,
            question_type: document.getElementById('genType').value,
            questions: generatedQuestions,
          }),
        });
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<i class="bi bi-check-circle"></i> Save to Question Bank';
        if (res.data && res.data.success) {
          showToast(res.data.message, 'success');
          resultsWrap.innerHTML = '';
          saveBtn.classList.add('d-none');
          generatedQuestions = [];
        } else {
          showToast((res.data && res.data.message) || 'Could not save questions.', 'danger');
        }
      });
    }
  }

  // ================================================================
  // QUESTION BANK — row actions (approve / reject / delete / regenerate)
  // ================================================================
  document.querySelectorAll('.q-status-btn').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const qid = btn.getAttribute('data-qid');
      const status = btn.getAttribute('data-status');
      const res = await qmFetch(`/admin/questions/${qid}/status`, {
        method: 'POST',
        body: JSON.stringify({ status }),
      });
      if (res.data && res.data.success) {
        showToast(res.data.message, 'success');
        const badge = document.querySelector(`#status-badge-${qid}`);
        if (badge) {
          badge.className = `qm-badge qm-badge-${status.toLowerCase()}`;
          badge.textContent = status;
        }
      } else {
        showToast('Could not update status.', 'danger');
      }
    });
  });

  document.querySelectorAll('.q-delete-btn').forEach((btn) => {
    btn.addEventListener('click', async () => {
      if (!confirm('Delete this question permanently?')) return;
      const qid = btn.getAttribute('data-qid');
      const res = await qmFetch(`/admin/questions/${qid}/delete`, { method: 'POST' });
      if (res.data && res.data.success) {
        showToast(res.data.message, 'success');
        const row = document.getElementById(`question-row-${qid}`);
        if (row) row.remove();
      }
    });
  });

  document.querySelectorAll('.q-regenerate-btn').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const qid = btn.getAttribute('data-qid');
      btn.disabled = true;
      const original = btn.innerHTML;
      btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
      const res = await qmFetch(`/admin/questions/${qid}/regenerate`, { method: 'POST' });
      btn.disabled = false;
      btn.innerHTML = original;
      if (res.data && res.data.success) {
        showToast(res.data.message, 'success');
        setTimeout(() => window.location.reload(), 700);
      } else {
        showToast((res.data && res.data.message) || 'Regeneration failed.', 'danger');
      }
    });
  });

  // ---------------- Live table search ----------------
  const tableSearch = document.getElementById('tableSearch');
  if (tableSearch) {
    tableSearch.addEventListener('input', () => {
      const term = tableSearch.value.toLowerCase();
      document.querySelectorAll('#crudTable tbody tr').forEach((tr) => {
        tr.style.display = tr.textContent.toLowerCase().includes(term) ? '' : 'none';
      });
    });
  }

  // ---------------- Edit question modal ----------------
  document.querySelectorAll('.q-edit-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const d = btn.dataset;
      document.getElementById('eqId').value = d.qid;
      document.getElementById('eqText').value = d.question;
      const opts = JSON.parse(d.options || '[]');
      ['A', 'B', 'C', 'D'].forEach((l, i) => { document.getElementById('eqOpt' + l).value = opts[i] || ''; });
      document.getElementById('eqCorrect').value = d.correct;
      document.getElementById('eqDiff').value = d.difficulty;
      document.getElementById('eqExp').value = d.explanation;
    });
  });
  const eqSave = document.getElementById('eqSave');
  if (eqSave) {
    eqSave.addEventListener('click', async () => {
      const qid = document.getElementById('eqId').value;
      const res = await qmFetch(`/admin/questions/${qid}/update`, {
        method: 'POST',
        body: JSON.stringify({
          question_text: document.getElementById('eqText').value,
          options: ['A', 'B', 'C', 'D'].map((l) => document.getElementById('eqOpt' + l).value),
          correct_answer: document.getElementById('eqCorrect').value,
          difficulty: document.getElementById('eqDiff').value,
          explanation: document.getElementById('eqExp').value,
        }),
      });
      if (res.data && res.data.success) {
        showToast(res.data.message, 'success');
        setTimeout(() => window.location.reload(), 600);
      } else {
        showToast('Could not update question.', 'danger');
      }
    });
  }
});
