from datetime import datetime
from app import db


class AcademicYear(db.Model):
    __tablename__ = "academic_years"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)  # e.g. "First Year B.Sc. Computer Science"
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    semesters = db.relationship("Semester", backref="academic_year", lazy="joined",
                                 cascade="all, delete-orphan", order_by="Semester.order_index")

    def __repr__(self):
        return f"<AcademicYear {self.name}>"


class Semester(db.Model):
    __tablename__ = "semesters"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # e.g. "Semester 1"
    order_index = db.Column(db.Integer, default=0)
    academic_year_id = db.Column(db.Integer, db.ForeignKey("academic_years.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    subjects = db.relationship("Subject", backref="semester", lazy="joined",
                                cascade="all, delete-orphan", order_by="Subject.name")

    __table_args__ = (db.UniqueConstraint("name", "academic_year_id", name="uq_semester_year"),)

    def __repr__(self):
        return f"<Semester {self.name}>"


class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(30), nullable=True)
    description = db.Column(db.Text, nullable=True)
    semester_id = db.Column(db.Integer, db.ForeignKey("semesters.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    chapters = db.relationship("Chapter", backref="subject", lazy="joined",
                                cascade="all, delete-orphan", order_by="Chapter.order_index")

    def __repr__(self):
        return f"<Subject {self.name}>"


class Chapter(db.Model):
    __tablename__ = "chapters"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    order_index = db.Column(db.Integer, default=0)
    description = db.Column(db.Text, nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    topics = db.relationship("Topic", backref="chapter", lazy="joined",
                              cascade="all, delete-orphan", order_by="Topic.id")

    def __repr__(self):
        return f"<Chapter {self.name}>"


class Topic(db.Model):
    __tablename__ = "topics"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapters.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Topic {self.name}>"
