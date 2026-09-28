from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class User(UserMixin, db.Model):
    """A registered user - either a student or an admin/teacher."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), nullable=False, default="student")  # student | admin
    academic_year_id = db.Column(db.Integer, db.ForeignKey("academic_years.id"), nullable=True)
    college_name = db.Column(db.String(200), nullable=True)

    is_active_account = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    academic_year = db.relationship("AcademicYear", foreign_keys=[academic_year_id])
    quiz_attempts = db.relationship("QuizAttempt", backref="student", lazy="dynamic",
                                     foreign_keys="QuizAttempt.student_id")
    bookmarks = db.relationship("Bookmark", backref="student", lazy="dynamic",
                                 cascade="all, delete-orphan")
    progress_records = db.relationship("StudentProgress", backref="student", lazy="dynamic",
                                        cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
