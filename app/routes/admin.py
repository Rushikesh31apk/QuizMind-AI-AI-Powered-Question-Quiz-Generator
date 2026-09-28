from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import func

from app import db
from app.models.user import User
from app.models.syllabus import AcademicYear, Semester, Subject, Chapter, Topic
from app.models.question import Question, QuestionOption
from app.models.quiz import Quiz, QuizAttempt
from app.utils.decorators import admin_required
from app.services.ai_service import AIService
from app.services.syllabus_service import SyllabusService

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
ai_service = AIService()


# ============================================================
# DASHBOARD
# ============================================================
@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    total_students = User.query.filter_by(role="student").count()
    total_subjects = Subject.query.count()
    total_questions = Question.query.count()
    total_quizzes = Quiz.query.count()
    total_attempts = QuizAttempt.query.filter_by(status="submitted").count()

    last_30 = datetime.utcnow() - timedelta(days=30)
    registrations = db.session.query(
        func.date(User.created_at).label("d"), func.count(User.id)
    ).filter(User.role == "student", User.created_at >= last_30).group_by("d").order_by("d").all()

    attempts_over_time = db.session.query(
        func.date(QuizAttempt.submitted_at).label("d"), func.count(QuizAttempt.id)
    ).filter(QuizAttempt.status == "submitted", QuizAttempt.submitted_at >= last_30).group_by("d").order_by("d").all()

    top_subjects = db.session.query(
        Subject.name, func.count(QuizAttempt.id)
    ).join(Quiz, Quiz.subject_id == Subject.id).join(
        QuizAttempt, QuizAttempt.quiz_id == Quiz.id
    ).filter(QuizAttempt.status == "submitted").group_by(Subject.name).order_by(
        func.count(QuizAttempt.id).desc()).limit(6).all()

    avg_scores_by_subject = db.session.query(
        Subject.name, func.avg(QuizAttempt.percentage)
    ).join(Quiz, Quiz.subject_id == Subject.id).join(
        QuizAttempt, QuizAttempt.quiz_id == Quiz.id
    ).filter(QuizAttempt.status == "submitted").group_by(Subject.name).limit(6).all()

    recent_students = User.query.filter_by(role="student").order_by(User.created_at.desc()).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        total_students=total_students, total_subjects=total_subjects,
        total_questions=total_questions, total_quizzes=total_quizzes, total_attempts=total_attempts,
        registrations=[{"label": str(d), "value": c} for d, c in registrations],
        attempts_over_time=[{"label": str(d), "value": c} for d, c in attempts_over_time],
        top_subjects=[{"label": n, "value": c} for n, c in top_subjects],
        avg_scores_by_subject=[{"label": n, "value": round(v or 0, 1)} for n, v in avg_scores_by_subject],
        recent_students=recent_students,
    )


# ============================================================
# ACADEMIC YEARS
# ============================================================
@admin_bp.route("/academic-years")
@login_required
@admin_required
def academic_years():
    years = AcademicYear.query.order_by(AcademicYear.order_index).all()
    return render_template("admin/academic_years.html", years=years)


@admin_bp.route("/academic-years/create", methods=["POST"])
@login_required
@admin_required
def create_academic_year():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Please enter a name for the academic year.", "danger")
    elif AcademicYear.query.filter_by(name=name).first():
        flash("This academic year already exists.", "danger")
    else:
        db.session.add(AcademicYear(name=name, order_index=AcademicYear.query.count()))
        db.session.commit()
        flash("Academic year added successfully.", "success")
    return redirect(url_for("admin.academic_years"))


@admin_bp.route("/academic-years/<int:year_id>/update", methods=["POST"])
@login_required
@admin_required
def update_academic_year(year_id):
    year = AcademicYear.query.get_or_404(year_id)
    year.name = request.form.get("name", year.name).strip()
    db.session.commit()
    flash("Academic year updated.", "success")
    return redirect(url_for("admin.academic_years"))


@admin_bp.route("/academic-years/<int:year_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_academic_year(year_id):
    year = AcademicYear.query.get_or_404(year_id)
    db.session.delete(year)
    db.session.commit()
    flash("Academic year deleted.", "info")
    return redirect(url_for("admin.academic_years"))


# ============================================================
# SEMESTERS
# ============================================================
@admin_bp.route("/semesters")
@login_required
@admin_required
def semesters():
    years = AcademicYear.query.order_by(AcademicYear.order_index).all()
    all_semesters = Semester.query.join(AcademicYear).order_by(AcademicYear.order_index, Semester.order_index).all()
    return render_template("admin/semesters.html", years=years, semesters=all_semesters)


@admin_bp.route("/semesters/create", methods=["POST"])
@login_required
@admin_required
def create_semester():
    name = request.form.get("name", "").strip()
    academic_year_id = request.form.get("academic_year_id")
    if not name or not academic_year_id:
        flash("Name and academic year are required.", "danger")
    elif Semester.query.filter_by(name=name, academic_year_id=academic_year_id).first():
        flash("This semester already exists for that academic year.", "danger")
    else:
        sem = Semester(name=name, academic_year_id=int(academic_year_id),
                        order_index=Semester.query.filter_by(academic_year_id=academic_year_id).count())
        db.session.add(sem)
        db.session.commit()
        flash("Semester added successfully.", "success")
    return redirect(url_for("admin.semesters"))


@admin_bp.route("/semesters/<int:semester_id>/update", methods=["POST"])
@login_required
@admin_required
def update_semester(semester_id):
    sem = Semester.query.get_or_404(semester_id)
    sem.name = request.form.get("name", sem.name).strip()
    if request.form.get("academic_year_id"):
        sem.academic_year_id = int(request.form.get("academic_year_id"))
    db.session.commit()
    flash("Semester updated.", "success")
    return redirect(url_for("admin.semesters"))


@admin_bp.route("/semesters/<int:semester_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_semester(semester_id):
    sem = Semester.query.get_or_404(semester_id)
    db.session.delete(sem)
    db.session.commit()
    flash("Semester deleted.", "info")
    return redirect(url_for("admin.semesters"))


# ============================================================
# SUBJECTS
# ============================================================
@admin_bp.route("/subjects")
@login_required
@admin_required
def subjects():
    all_semesters = Semester.query.join(AcademicYear).order_by(AcademicYear.order_index, Semester.order_index).all()
    all_subjects = Subject.query.join(Semester).join(AcademicYear).order_by(
        AcademicYear.order_index, Semester.order_index, Subject.name).all()
    return render_template("admin/subjects.html", semesters=all_semesters, subjects=all_subjects)


@admin_bp.route("/subjects/create", methods=["POST"])
@login_required
@admin_required
def create_subject():
    name = request.form.get("name", "").strip()
    code = request.form.get("code", "").strip()
    semester_id = request.form.get("semester_id")
    description = request.form.get("description", "").strip()
    if not name or not semester_id:
        flash("Name and semester are required.", "danger")
    else:
        db.session.add(Subject(name=name, code=code, semester_id=int(semester_id), description=description))
        db.session.commit()
        flash("Subject added successfully.", "success")
    return redirect(url_for("admin.subjects"))


@admin_bp.route("/subjects/<int:subject_id>/update", methods=["POST"])
@login_required
@admin_required
def update_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    subject.name = request.form.get("name", subject.name).strip()
    subject.code = request.form.get("code", subject.code)
    subject.description = request.form.get("description", subject.description)
    if request.form.get("semester_id"):
        subject.semester_id = int(request.form.get("semester_id"))
    db.session.commit()
    flash("Subject updated.", "success")
    return redirect(url_for("admin.subjects"))


@admin_bp.route("/subjects/<int:subject_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash("Subject deleted.", "info")
    return redirect(url_for("admin.subjects"))


# ============================================================
# CHAPTERS
# ============================================================
@admin_bp.route("/chapters")
@login_required
@admin_required
def chapters():
    all_subjects = Subject.query.order_by(Subject.name).all()
    all_chapters = Chapter.query.join(Subject).order_by(Subject.name, Chapter.order_index).all()
    return render_template("admin/chapters.html", subjects=all_subjects, chapters=all_chapters)


@admin_bp.route("/chapters/create", methods=["POST"])
@login_required
@admin_required
def create_chapter():
    name = request.form.get("name", "").strip()
    subject_id = request.form.get("subject_id")
    description = request.form.get("description", "").strip()
    if not name or not subject_id:
        flash("Name and subject are required.", "danger")
    else:
        chapter = Chapter(name=name, subject_id=int(subject_id), description=description,
                           order_index=Chapter.query.filter_by(subject_id=subject_id).count())
        db.session.add(chapter)
        db.session.commit()
        flash("Chapter added successfully.", "success")
    return redirect(url_for("admin.chapters"))


@admin_bp.route("/chapters/<int:chapter_id>/update", methods=["POST"])
@login_required
@admin_required
def update_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    chapter.name = request.form.get("name", chapter.name).strip()
    chapter.description = request.form.get("description", chapter.description)
    if request.form.get("subject_id"):
        chapter.subject_id = int(request.form.get("subject_id"))
    db.session.commit()
    flash("Chapter updated.", "success")
    return redirect(url_for("admin.chapters"))


@admin_bp.route("/chapters/<int:chapter_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    flash("Chapter deleted.", "info")
    return redirect(url_for("admin.chapters"))


# ============================================================
# TOPICS
# ============================================================
@admin_bp.route("/topics")
@login_required
@admin_required
def topics():
    all_chapters = Chapter.query.join(Subject).order_by(Subject.name, Chapter.order_index).all()
    all_topics = Topic.query.join(Chapter).order_by(Chapter.name, Topic.id).all()
    return render_template("admin/topics.html", chapters=all_chapters, topics=all_topics)


@admin_bp.route("/topics/create", methods=["POST"])
@login_required
@admin_required
def create_topic():
    name = request.form.get("name", "").strip()
    chapter_id = request.form.get("chapter_id")
    if not name or not chapter_id:
        flash("Name and chapter are required.", "danger")
    else:
        db.session.add(Topic(name=name, chapter_id=int(chapter_id)))
        db.session.commit()
        flash("Topic added successfully.", "success")
    return redirect(url_for("admin.topics"))


@admin_bp.route("/topics/<int:topic_id>/update", methods=["POST"])
@login_required
@admin_required
def update_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    topic.name = request.form.get("name", topic.name).strip()
    if request.form.get("chapter_id"):
        topic.chapter_id = int(request.form.get("chapter_id"))
    db.session.commit()
    flash("Topic updated.", "success")
    return redirect(url_for("admin.topics"))


@admin_bp.route("/topics/<int:topic_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    db.session.delete(topic)
    db.session.commit()
    flash("Topic deleted.", "info")
    return redirect(url_for("admin.topics"))


# ============================================================
# AI SYLLABUS ANALYZER  (JSON / AJAX — needs preview-before-import)
# ============================================================
@admin_bp.route("/syllabus-analyzer", methods=["GET"])
@login_required
@admin_required
def syllabus_analyzer():
    return render_template("admin/syllabus_analyzer.html")


@admin_bp.route("/syllabus-analyzer/analyze", methods=["POST"])
@login_required
@admin_required
def analyze_syllabus():
    raw_text = request.form.get("syllabus_text", "").strip()
    upload = request.files.get("syllabus_file")

    if upload and upload.filename:
        filename = secure_filename(upload.filename)
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in current_app.config["ALLOWED_SYLLABUS_EXTENSIONS"]:
            return jsonify({"success": False, "message": "Only .pdf and .txt files are allowed."}), 400
        try:
            raw_text = SyllabusService.extract_text_from_file(upload.stream, filename)
        except Exception as exc:  # noqa: BLE001
            return jsonify({"success": False, "message": f"Could not read file: {exc}"}), 400

    if not raw_text or len(raw_text.strip()) < 20:
        return jsonify({"success": False, "message": "Please paste syllabus text or upload a valid file."}), 400

    result = ai_service.analyze_syllabus(raw_text)
    if not result["structure"]:
        return jsonify({"success": False, "message": "Could not detect any syllabus structure in the "
                                                       "supplied content. Please check the format and try again."}), 422

    return jsonify({"success": True, "structure": result["structure"]})


@admin_bp.route("/syllabus-analyzer/import", methods=["POST"])
@login_required
@admin_required
def import_syllabus():
    payload = request.get_json(force=True, silent=True) or {}
    structure = payload.get("structure", [])
    if not structure:
        return jsonify({"success": False, "message": "Nothing to import."}), 400

    created = SyllabusService.import_structure(structure)
    return jsonify({"success": True, "created": created,
                     "message": "Syllabus imported successfully."})


# ============================================================
# AI QUESTION GENERATOR (JSON / AJAX — needs preview-before-save)
# ============================================================
@admin_bp.route("/question-generator")
@login_required
@admin_required
def question_generator():
    all_subjects = Subject.query.order_by(Subject.name).all()
    return render_template("admin/question_generator.html", subjects=all_subjects)


@admin_bp.route("/question-generator/generate", methods=["POST"])
@login_required
@admin_required
def generate_questions_preview():
    payload = request.get_json(force=True, silent=True) or {}
    subject = Subject.query.get(payload.get("subject_id"))
    chapter = Chapter.query.get(payload.get("chapter_id")) if payload.get("chapter_id") else None
    topic = Topic.query.get(payload.get("topic_id")) if payload.get("topic_id") else None
    difficulty = payload.get("difficulty", "Medium")
    count = min(max(int(payload.get("count", 5)), 1), 25)
    question_type = payload.get("question_type", "mcq")

    if not subject:
        return jsonify({"success": False, "message": "Please select a subject."}), 400

    questions = ai_service.generate_questions(
        subject=subject.name,
        chapter=chapter.name if chapter else subject.name,
        topic=topic.name if topic else None,
        difficulty=difficulty,
        count=count,
        question_type=question_type,
    )
    demo_mode = current_app.config.get("AI_PROVIDER", "demo") == "demo"
    return jsonify({"success": True, "questions": questions, "demo_mode": demo_mode})


@admin_bp.route("/question-generator/save", methods=["POST"])
@login_required
@admin_required
def save_generated_questions():
    payload = request.get_json(force=True, silent=True) or {}
    subject_id = payload.get("subject_id")
    chapter_id = payload.get("chapter_id")
    topic_id = payload.get("topic_id")
    question_type = payload.get("question_type", "mcq")
    questions = payload.get("questions", [])

    subject = Subject.query.get_or_404(subject_id)
    chapter = Chapter.query.get(chapter_id) if chapter_id else (subject.chapters[0] if subject.chapters else None)
    if not chapter:
        return jsonify({"success": False, "message": "This subject has no chapters yet. Add a chapter first."}), 400

    saved = 0
    for q in questions:
        question = Question(
            question_text=q["question"],
            question_type=question_type,
            difficulty=q.get("difficulty", "Medium"),
            correct_answer=q["correct_answer"],
            explanation=q.get("explanation", ""),
            status="Approved",
            source="ai",
            subject_id=subject.id,
            chapter_id=chapter.id,
            topic_id=int(topic_id) if topic_id else None,
            created_by=current_user.id,
        )
        db.session.add(question)
        db.session.flush()
        for idx, opt_text in enumerate(q.get("options", [])[:4]):
            label = ["A", "B", "C", "D"][idx]
            db.session.add(QuestionOption(question_id=question.id, option_label=label, option_text=opt_text))
        saved += 1

    db.session.commit()
    return jsonify({"success": True, "message": f"{saved} question(s) saved to the question bank."})


# ============================================================
# QUESTION BANK (ADMIN)
# ============================================================
@admin_bp.route("/questions")
@login_required
@admin_required
def questions():
    query = Question.query
    subject_id = request.args.get("subject_id")
    chapter_id = request.args.get("chapter_id")
    difficulty = request.args.get("difficulty")
    status = request.args.get("status")
    search = request.args.get("q", "").strip()

    if subject_id:
        query = query.filter(Question.subject_id == subject_id)
    if chapter_id:
        query = query.filter(Question.chapter_id == chapter_id)
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    if status:
        query = query.filter(Question.status == status)
    if search:
        query = query.filter(Question.question_text.ilike(f"%{search}%"))

    all_questions = query.order_by(Question.created_at.desc()).limit(200).all()
    all_subjects = Subject.query.order_by(Subject.name).all()
    all_chapters = Chapter.query.order_by(Chapter.name).all()

    return render_template("admin/questions.html", questions=all_questions, subjects=all_subjects,
                            chapters=all_chapters, filters=request.args)


@admin_bp.route("/questions/<int:question_id>/update", methods=["POST"])
@login_required
@admin_required
def update_question(question_id):
    question = Question.query.get_or_404(question_id)
    payload = request.get_json(force=True, silent=True) or {}

    question.question_text = payload.get("question_text", question.question_text)
    question.difficulty = payload.get("difficulty", question.difficulty)
    question.correct_answer = payload.get("correct_answer", question.correct_answer)
    question.explanation = payload.get("explanation", question.explanation)

    options = payload.get("options")
    if options:
        for opt in list(question.options):
            db.session.delete(opt)
        db.session.flush()
        for idx, opt_text in enumerate(options[:4]):
            label = ["A", "B", "C", "D"][idx]
            db.session.add(QuestionOption(question_id=question.id, option_label=label, option_text=opt_text))

    db.session.commit()
    return jsonify({"success": True, "message": "Question updated successfully."})


@admin_bp.route("/questions/<int:question_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return jsonify({"success": True, "message": "Question deleted."})


@admin_bp.route("/questions/<int:question_id>/status", methods=["POST"])
@login_required
@admin_required
def set_question_status(question_id):
    question = Question.query.get_or_404(question_id)
    payload = request.get_json(silent=True) or {}
    new_status = request.form.get("status") or payload.get("status")
    if new_status not in ("Draft", "Approved", "Rejected"):
        return jsonify({"success": False, "message": "Invalid status."}), 400
    question.status = new_status
    db.session.commit()
    return jsonify({"success": True, "message": f"Question marked as {new_status}."})


@admin_bp.route("/questions/<int:question_id>/regenerate", methods=["POST"])
@login_required
@admin_required
def regenerate_question(question_id):
    question = Question.query.get_or_404(question_id)
    generated = ai_service.generate_questions(
        subject=question.subject.name,
        chapter=question.chapter.name,
        topic=question.topic.name if question.topic else None,
        difficulty=question.difficulty,
        count=1,
        question_type=question.question_type,
    )
    if not generated:
        return jsonify({"success": False, "message": "Could not regenerate question."}), 500

    g = generated[0]
    question.question_text = g["question"]
    question.correct_answer = g["correct_answer"]
    question.explanation = g.get("explanation", "")
    for opt in list(question.options):
        db.session.delete(opt)
    db.session.flush()
    for idx, opt_text in enumerate(g["options"][:4]):
        label = ["A", "B", "C", "D"][idx]
        db.session.add(QuestionOption(question_id=question.id, option_label=label, option_text=opt_text))
    db.session.commit()
    return jsonify({"success": True, "message": "Question regenerated.", "question": question.to_dict(True)})


# ============================================================
# STUDENTS
# ============================================================
@admin_bp.route("/students")
@login_required
@admin_required
def students():
    search = request.args.get("q", "").strip()
    query = User.query.filter_by(role="student")
    if search:
        query = query.filter(User.full_name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%"))
    all_students = query.order_by(User.created_at.desc()).all()
    return render_template("admin/students.html", students=all_students, search=search)


@admin_bp.route("/students/<int:student_id>/toggle-active", methods=["POST"])
@login_required
@admin_required
def toggle_student_active(student_id):
    student = User.query.get_or_404(student_id)
    student.is_active_account = not student.is_active_account
    db.session.commit()
    state = "activated" if student.is_active_account else "deactivated"
    flash(f"Student account {state}.", "success")
    return redirect(url_for("admin.students"))


@admin_bp.route("/students/<int:student_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_student(student_id):
    student = User.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash("Student account removed.", "info")
    return redirect(url_for("admin.students"))


# ============================================================
# QUIZ ATTEMPTS (ADMIN VIEW)
# ============================================================
@admin_bp.route("/attempts")
@login_required
@admin_required
def attempts():
    all_attempts = QuizAttempt.query.filter_by(status="submitted").order_by(
        QuizAttempt.submitted_at.desc()).limit(200).all()
    return render_template("admin/attempts.html", attempts=all_attempts)


# ============================================================
# ANALYTICS
# ============================================================
@admin_bp.route("/analytics")
@login_required
@admin_required
def analytics():
    total_students = User.query.filter_by(role="student").count()
    total_attempts = QuizAttempt.query.filter_by(status="submitted").count()
    avg_score = db.session.query(func.avg(QuizAttempt.percentage)).filter(
        QuizAttempt.status == "submitted").scalar() or 0

    subject_avg = db.session.query(
        Subject.name, func.avg(QuizAttempt.percentage), func.count(QuizAttempt.id)
    ).join(Quiz, Quiz.subject_id == Subject.id).join(
        QuizAttempt, QuizAttempt.quiz_id == Quiz.id
    ).filter(QuizAttempt.status == "submitted").group_by(Subject.name).all()

    difficulty_dist = db.session.query(
        Question.difficulty, func.count(Question.id)
    ).group_by(Question.difficulty).all()

    return render_template(
        "admin/analytics.html",
        total_students=total_students, total_attempts=total_attempts, avg_score=round(avg_score, 1),
        subject_avg=[{"label": n, "value": round(v or 0, 1), "count": c} for n, v, c in subject_avg],
        difficulty_dist=[{"label": d or "Unspecified", "value": c} for d, c in difficulty_dist],
    )


# ============================================================
# SETTINGS
# ============================================================
@admin_bp.route("/settings")
@login_required
@admin_required
def settings():
    return render_template("admin/settings.html")
