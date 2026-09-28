from datetime import datetime
from app import db


class StudentProgress(db.Model):
    """Aggregated performance for a student on a subject (and optionally a chapter).
    Updated incrementally every time a quiz attempt is submitted."""
    __tablename__ = "student_progress"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapters.id"), nullable=True)

    total_attempts = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    total_correct = db.Column(db.Integer, default=0)
    accuracy = db.Column(db.Float, default=0.0)
    last_attempted_at = db.Column(db.DateTime, default=datetime.utcnow)

    subject = db.relationship("Subject")
    chapter = db.relationship("Chapter")

    __table_args__ = (
        db.UniqueConstraint("student_id", "subject_id", "chapter_id", name="uq_progress_scope"),
    )

    def recompute_accuracy(self):
        self.accuracy = (self.total_correct / self.total_questions * 100) if self.total_questions else 0.0
