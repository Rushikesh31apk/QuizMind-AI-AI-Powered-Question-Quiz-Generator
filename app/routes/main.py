from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user

from app.models.syllabus import AcademicYear, Subject, Chapter, Topic
from app.models.question import Question

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return render_template("index.html", authenticated_admin=True)
    years = AcademicYear.query.order_by(AcademicYear.order_index).all()
    return render_template("index.html", years=years)


@main_bp.route("/search")
def search():
    query = request.args.get("q", "").strip()
    results = {"subjects": [], "chapters": [], "topics": [], "questions": []}

    if query:
        like = f"%{query}%"
        results["subjects"] = Subject.query.filter(Subject.name.ilike(like)).limit(10).all()
        results["chapters"] = Chapter.query.filter(Chapter.name.ilike(like)).limit(10).all()
        results["topics"] = Topic.query.filter(Topic.name.ilike(like)).limit(10).all()
        results["questions"] = Question.query.filter(
            Question.question_text.ilike(like), Question.status == "Approved"
        ).limit(10).all()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.args.get("ajax"):
        return jsonify({
            "subjects": [{"id": s.id, "name": s.name} for s in results["subjects"]],
            "chapters": [{"id": c.id, "name": c.name, "subject": c.subject.name} for c in results["chapters"]],
            "topics": [{"id": t.id, "name": t.name, "chapter": t.chapter.name} for t in results["topics"]],
            "questions": [{"id": q.id, "text": q.question_text[:120]} for q in results["questions"]],
        })

    return render_template("search_results.html", query=query, results=results)
