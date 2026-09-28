from flask import Blueprint, jsonify, request
from flask_login import login_required

from app.models.syllabus import AcademicYear, Semester, Subject, Chapter, Topic

api_bp = Blueprint("api", __name__)


@api_bp.route("/semesters")
@login_required
def get_semesters():
    year_id = request.args.get("academic_year_id")
    if not year_id:
        return jsonify([])
    rows = Semester.query.filter_by(academic_year_id=year_id).order_by(Semester.order_index).all()
    return jsonify([{"id": s.id, "name": s.name} for s in rows])


@api_bp.route("/subjects")
@login_required
def get_subjects():
    semester_id = request.args.get("semester_id")
    if not semester_id:
        return jsonify([])
    rows = Subject.query.filter_by(semester_id=semester_id).order_by(Subject.name).all()
    return jsonify([{"id": s.id, "name": s.name, "code": s.code} for s in rows])


@api_bp.route("/chapters")
@login_required
def get_chapters():
    subject_id = request.args.get("subject_id")
    if not subject_id:
        return jsonify([])
    rows = Chapter.query.filter_by(subject_id=subject_id).order_by(Chapter.order_index).all()
    return jsonify([{"id": c.id, "name": c.name} for c in rows])


@api_bp.route("/topics")
@login_required
def get_topics():
    chapter_id = request.args.get("chapter_id")
    if not chapter_id:
        return jsonify([])
    rows = Topic.query.filter_by(chapter_id=chapter_id).order_by(Topic.id).all()
    return jsonify([{"id": t.id, "name": t.name} for t in rows])


@api_bp.route("/subject-path")
@login_required
def subject_path():
    """Return the year/semester ids for a subject (used to pre-fill the quiz form)."""
    subject = Subject.query.get(request.args.get("subject_id", type=int))
    if not subject:
        return jsonify({})
    return jsonify({"semester_id": subject.semester_id,
                    "year_id": subject.semester.academic_year_id})
