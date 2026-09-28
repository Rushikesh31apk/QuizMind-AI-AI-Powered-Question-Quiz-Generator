from datetime import datetime
from app import db


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), default="mcq")  # mcq | true_false | multi_select
    difficulty = db.Column(db.String(10), default="Medium")  # Easy | Medium | Hard
    correct_answer = db.Column(db.String(500), nullable=False)  # letter(s) e.g. "A" or "A,C"
    explanation = db.Column(db.Text, nullable=True)

    status = db.Column(db.String(20), default="Approved")  # Draft | Approved | Rejected
    source = db.Column(db.String(20), default="ai")  # ai | manual

    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapters.id"), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=True)

    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    options = db.relationship("QuestionOption", backref="question", lazy="joined",
                               cascade="all, delete-orphan", order_by="QuestionOption.option_label")
    subject = db.relationship("Subject")
    chapter = db.relationship("Chapter")
    topic = db.relationship("Topic")

    def options_dict(self):
        return {opt.option_label: opt.option_text for opt in self.options}

    def to_dict(self, reveal_answer=False):
        data = {
            "id": self.id,
            "question": self.question_text,
            "question_type": self.question_type,
            "difficulty": self.difficulty,
            "options": [{"label": o.option_label, "text": o.option_text} for o in self.options],
            "subject": self.subject.name if self.subject else None,
            "chapter": self.chapter.name if self.chapter else None,
            "topic": self.topic.name if self.topic else None,
        }
        if reveal_answer:
            data["correct_answer"] = self.correct_answer
            data["explanation"] = self.explanation
        return data

    def __repr__(self):
        return f"<Question {self.id}: {self.question_text[:40]}>"


class QuestionOption(db.Model):
    __tablename__ = "question_options"

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    option_label = db.Column(db.String(5), nullable=False)  # A, B, C, D
    option_text = db.Column(db.String(500), nullable=False)


class Bookmark(db.Model):
    __tablename__ = "bookmarks"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    question = db.relationship("Question")

    __table_args__ = (db.UniqueConstraint("student_id", "question_id", name="uq_bookmark"),)
