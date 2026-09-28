from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func

from app import db
from app.models.user import User
from app.models.syllabus import AcademicYear, Semester, Subject, Chapter, Topic
from app.models.question import Question, Bookmark
from app.models.quiz import QuizAttempt
from app.models.progress import StudentProgress
from app.utils.decorators import student_required
from app.services.ai_service import AIService

student_bp = Blueprint("student", __name__)
ai_service = AIService()


@student_bp.route("/dashboard")
@login_required
@student_required
def dashboard():
    attempts = current_user.quiz_attempts.filter_by(status="submitted").order_by(
        QuizAttempt.submitted_at.desc()).all()

    total_attempts = len(attempts)
    total_questions_solved = sum(a.total_questions for a in attempts)
    avg_score = round(sum(a.percentage for a in attempts) / total_attempts, 1) if total_attempts else 0
    total_correct = sum(a.correct_count for a in attempts)
    accuracy = round((total_correct / total_questions_solved) * 100, 1) if total_questions_solved else 0

    recent_attempts = attempts[:5]

    progress_rows = StudentProgress.query.filter_by(student_id=current_user.id, chapter_id=None).all()
    weak_topics = sorted([p for p in progress_rows if p.total_questions >= 1],
                          key=lambda p: p.accuracy)[:3]

    recommendations = ai_service.generate_practice_recommendations([
        {"subject": p.subject.name, "chapter": None, "accuracy": p.accuracy, "attempts": p.total_attempts}
        for p in progress_rows
    ])

    subjects = Subject.query.limit(6).all()

    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"

    return render_template(
        "student/dashboard.html",
        greeting=greeting,
        total_attempts=total_attempts,
        total_questions_solved=total_questions_solved,
        avg_score=avg_score,
        accuracy=accuracy,
        recent_attempts=recent_attempts,
        weak_topics=weak_topics,
        recommendations=recommendations,
        subjects=subjects,
    )


@student_bp.route("/subjects")
@login_required
@student_required
def subjects():
    years = AcademicYear.query.order_by(AcademicYear.order_index).all()
    return render_template("student/subjects.html", years=years)


@student_bp.route("/question-bank")
@login_required
@student_required
def question_bank():
    bookmarks = Bookmark.query.filter_by(student_id=current_user.id).order_by(
        Bookmark.created_at.desc()).all()
    all_subjects = Subject.query.all()
    return render_template("student/question_bank.html", bookmarks=bookmarks, subjects=all_subjects)


@student_bp.route("/my-attempts")
@login_required
@student_required
def my_attempts():
    attempts = current_user.quiz_attempts.filter_by(status="submitted").order_by(
        QuizAttempt.submitted_at.desc()).all()
    return render_template("student/attempts.html", attempts=attempts)


@student_bp.route("/performance")
@login_required
@student_required
def performance():
    attempts = current_user.quiz_attempts.filter_by(status="submitted").order_by(
        QuizAttempt.submitted_at.asc()).all()

    total_attempts = len(attempts)
    total_questions = sum(a.total_questions for a in attempts)
    total_correct = sum(a.correct_count for a in attempts)
    overall_accuracy = round((total_correct / total_questions) * 100, 1) if total_questions else 0
    avg_score = round(sum(a.percentage for a in attempts) / total_attempts, 1) if total_attempts else 0

    score_over_time = [{"label": a.submitted_at.strftime("%d %b"), "value": a.percentage} for a in attempts[-15:]]

    subject_perf = {}
    for a in attempts:
        name = a.quiz.subject.name if a.quiz and a.quiz.subject else "Unknown"
        subject_perf.setdefault(name, {"correct": 0, "total": 0})
        subject_perf[name]["correct"] += a.correct_count
        subject_perf[name]["total"] += a.total_questions
    subject_chart = [{"label": k, "value": round((v["correct"] / v["total"]) * 100, 1) if v["total"] else 0}
                      for k, v in subject_perf.items()]

    chapter_perf = {}
    for a in attempts:
        name = a.quiz.chapter.name if a.quiz and a.quiz.chapter else "General"
        chapter_perf.setdefault(name, {"correct": 0, "total": 0})
        chapter_perf[name]["correct"] += a.correct_count
        chapter_perf[name]["total"] += a.total_questions
    chapter_chart = [{"label": k, "value": round((v["correct"] / v["total"]) * 100, 1) if v["total"] else 0}
                      for k, v in chapter_perf.items()]

    difficulty_perf = {"Easy": {"correct": 0, "total": 0}, "Medium": {"correct": 0, "total": 0},
                        "Hard": {"correct": 0, "total": 0}}
    for a in attempts:
        d = a.quiz.difficulty if a.quiz and a.quiz.difficulty in difficulty_perf else "Medium"
        difficulty_perf[d]["correct"] += a.correct_count
        difficulty_perf[d]["total"] += a.total_questions
    difficulty_chart = [{"label": k, "value": round((v["correct"] / v["total"]) * 100, 1) if v["total"] else 0}
                         for k, v in difficulty_perf.items()]

    correct_vs_incorrect = {
        "correct": total_correct,
        "incorrect": sum(a.wrong_count for a in attempts),
        "unanswered": sum(a.unanswered_count for a in attempts),
    }

    progress_rows = StudentProgress.query.filter_by(student_id=current_user.id, chapter_id=None).all()
    weak_areas = sorted([p for p in progress_rows if p.total_questions >= 1], key=lambda p: p.accuracy)[:5]
    strong_areas = sorted([p for p in progress_rows if p.total_questions >= 1], key=lambda p: -p.accuracy)[:5]

    return render_template(
        "student/performance.html",
        total_attempts=total_attempts, total_questions=total_questions,
        overall_accuracy=overall_accuracy, avg_score=avg_score,
        score_over_time=score_over_time, subject_chart=subject_chart,
        chapter_chart=chapter_chart, difficulty_chart=difficulty_chart,
        correct_vs_incorrect=correct_vs_incorrect,
        weak_areas=weak_areas, strong_areas=strong_areas,
    )


@student_bp.route("/leaderboard")
@login_required
@student_required
def leaderboard():
    rows = db.session.query(
        User.id, User.full_name,
        func.count(QuizAttempt.id).label("attempts"),
        func.avg(QuizAttempt.percentage).label("avg_score"),
    ).join(QuizAttempt, QuizAttempt.student_id == User.id).filter(
        QuizAttempt.status == "submitted", User.role == "student"
    ).group_by(User.id).order_by(func.avg(QuizAttempt.percentage).desc()).limit(20).all()

    return render_template("student/leaderboard.html", rows=rows)


@student_bp.route("/settings")
@login_required
@student_required
def settings():
    return render_template("student/settings.html")


@student_bp.route("/bookmarks/toggle", methods=["POST"])
@login_required
@student_required
def toggle_bookmark():
    question_id = request.json.get("question_id") if request.is_json else request.form.get("question_id")
    question = Question.query.get_or_404(question_id)

    existing = Bookmark.query.filter_by(student_id=current_user.id, question_id=question.id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({"bookmarked": False, "message": "Bookmark removed."})

    db.session.add(Bookmark(student_id=current_user.id, question_id=question.id))
    db.session.commit()
    return jsonify({"bookmarked": True, "message": "Question bookmarked."})
