from datetime import datetime
from app import db


class Quiz(db.Model):
    """A generated quiz configuration (a set of questions a student will attempt)."""
    __tablename__ = "quizzes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapters.id"), nullable=True)
    difficulty = db.Column(db.String(10), default="Medium")
    time_limit_minutes = db.Column(db.Integer, default=30)
    total_questions = db.Column(db.Integer, default=10)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    subject = db.relationship("Subject")
    chapter = db.relationship("Chapter")
    quiz_questions = db.relationship("QuizQuestion", backref="quiz", lazy="joined",
                                      cascade="all, delete-orphan", order_by="QuizQuestion.order_index")


class QuizQuestion(db.Model):
    """Maps a question into a quiz, in a fixed order."""
    __tablename__ = "quiz_questions"

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    order_index = db.Column(db.Integer, default=0)

    question = db.relationship("Question")


class QuizAttempt(db.Model):
    """A single student's attempt at a quiz."""
    __tablename__ = "quiz_attempts"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False)

    status = db.Column(db.String(20), default="in_progress")  # in_progress | submitted | timed_out
    score = db.Column(db.Integer, default=0)
    correct_count = db.Column(db.Integer, default=0)
    wrong_count = db.Column(db.Integer, default=0)
    unanswered_count = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    percentage = db.Column(db.Float, default=0.0)
    time_taken_seconds = db.Column(db.Integer, default=0)

    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    submitted_at = db.Column(db.DateTime, nullable=True)

    quiz = db.relationship("Quiz")
    answers = db.relationship("QuizAnswer", backref="attempt", lazy="joined",
                               cascade="all, delete-orphan")

    def performance_label(self):
        if self.percentage >= 85:
            return "Excellent"
        if self.percentage >= 60:
            return "Good"
        return "Needs Practice"


class QuizAnswer(db.Model):
    """A student's answer to one question within an attempt."""
    __tablename__ = "quiz_answers"

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("quiz_attempts.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    selected_answer = db.Column(db.String(500), nullable=True)  # e.g. "A" or None
    is_correct = db.Column(db.Boolean, default=False)
    marked_for_review = db.Column(db.Boolean, default=False)

    question = db.relationship("Question")
