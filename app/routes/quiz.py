from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user

from app import db
from app.models.syllabus import Subject, Chapter, Topic
from app.models.quiz import Quiz, QuizAttempt
from app.models.question import Bookmark
from app.utils.decorators import student_required
from app.services.quiz_service import QuizService

quiz_bp = Blueprint("quiz", __name__, url_prefix="/quiz")


@quiz_bp.route("/start", methods=["GET", "POST"])
@login_required
@student_required
def start():
    if request.method == "POST":
        subject = Subject.query.get_or_404(int(request.form.get("subject_id")))
        chapter_id = request.form.get("chapter_id") or None
        topic_id = request.form.get("topic_id") or None
        chapter = Chapter.query.get(int(chapter_id)) if chapter_id else None
        topic = Topic.query.get(int(topic_id)) if topic_id else None
        difficulty = request.form.get("difficulty", "Medium")
        count = min(max(int(request.form.get("num_questions", 10)), 1), 50)
        question_type = request.form.get("question_type", "mcq")
        time_limit = int(request.form.get("time_limit", current_app.config["DEFAULT_QUIZ_TIME_MINUTES"]))

        if not chapter and not subject.chapters:
            flash("This subject has no chapters yet. Ask your administrator to add some.", "danger")
            return redirect(url_for("quiz.start"))

        quiz = QuizService.build_quiz(
            subject=subject, chapter=chapter, difficulty=difficulty,
            count=count, question_type=question_type, created_by=current_user.id, topic=topic,
        )
        quiz.time_limit_minutes = time_limit
        db.session.commit()

        attempt = QuizService.start_attempt(quiz, current_user.id)
        return redirect(url_for("quiz.take", attempt_id=attempt.id))

    from app.models.syllabus import AcademicYear
    years = AcademicYear.query.order_by(AcademicYear.order_index).all()
    return render_template("quiz/setup.html", years=years)


@quiz_bp.route("/attempt/<int:attempt_id>")
@login_required
@student_required
def take(attempt_id):
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    if attempt.student_id != current_user.id:
        flash("You are not authorized to view this quiz attempt.", "danger")
        return redirect(url_for("student.dashboard"))
    if attempt.status != "in_progress":
        return redirect(url_for("quiz.result", attempt_id=attempt.id))

    quiz = attempt.quiz
    questions = [qq.question for qq in quiz.quiz_questions]
    bookmarked_ids = {b.question_id for b in Bookmark.query.filter_by(student_id=current_user.id).all()}

    questions_json = [{
        "id": q.id,
        "question": q.question_text,
        "options": [{"label": o.option_label, "text": o.option_text} for o in q.options],
        "type": q.question_type,
    } for q in questions]

    return render_template(
        "quiz/take.html", attempt=attempt, quiz=quiz, questions=questions,
        questions_json=questions_json, bookmarked_ids=bookmarked_ids,
    )


@quiz_bp.route("/attempt/<int:attempt_id>/submit", methods=["POST"])
@login_required
@student_required
def submit(attempt_id):
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    if attempt.student_id != current_user.id:
        return jsonify({"error": "Not authorized"}), 403
    if attempt.status != "in_progress":
        return jsonify({"redirect": url_for("quiz.result", attempt_id=attempt.id)})

    payload = request.get_json(force=True, silent=True) or {}
    answers = payload.get("answers", {})
    time_taken = int(payload.get("time_taken_seconds", 0))
    timed_out = bool(payload.get("timed_out", False))

    QuizService.submit_attempt(attempt, answers, time_taken, timed_out=timed_out)

    return jsonify({"redirect": url_for("quiz.result", attempt_id=attempt.id)})


@quiz_bp.route("/result/<int:attempt_id>")
@login_required
@student_required
def result(attempt_id):
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    if attempt.student_id != current_user.id:
        flash("You are not authorized to view this result.", "danger")
        return redirect(url_for("student.dashboard"))
    if attempt.status == "in_progress":
        return redirect(url_for("quiz.take", attempt_id=attempt.id))

    bookmarked_ids = {b.question_id for b in Bookmark.query.filter_by(student_id=current_user.id).all()}

    return render_template("quiz/result.html", attempt=attempt, bookmarked_ids=bookmarked_ids)


@quiz_bp.route("/retry/<int:quiz_id>")
@login_required
@student_required
def retry(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    attempt = QuizService.start_attempt(quiz, current_user.id)
    return redirect(url_for("quiz.take", attempt_id=attempt.id))


@quiz_bp.route("/practice-saved")
@login_required
@student_required
def practice_saved():
    """Build a quiz from the student's bookmarked questions."""
    from app.models.quiz import QuizQuestion
    bookmarks = Bookmark.query.filter_by(student_id=current_user.id).all()
    if not bookmarks:
        flash("Bookmark some questions first to practice them.", "info")
        return redirect(url_for("student.question_bank"))
    first = bookmarks[0].question
    quiz = Quiz(title="Saved Questions Practice", subject_id=first.subject_id, chapter_id=None,
                difficulty="Mixed", total_questions=len(bookmarks),
                time_limit_minutes=max(10, len(bookmarks) * 2), created_by=current_user.id)
    db.session.add(quiz)
    db.session.flush()
    for idx, b in enumerate(bookmarks):
        db.session.add(QuizQuestion(quiz_id=quiz.id, question_id=b.question_id, order_index=idx))
    db.session.commit()
    attempt = QuizService.start_attempt(quiz, current_user.id)
    return redirect(url_for("quiz.take", attempt_id=attempt.id))
