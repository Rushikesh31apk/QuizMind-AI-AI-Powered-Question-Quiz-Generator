"""
QuizService - business logic for building quizzes, scoring attempts and
maintaining per-student progress/analytics records.
"""
from datetime import datetime

from app import db
from app.models.question import Question
from app.models.quiz import Quiz, QuizQuestion, QuizAttempt, QuizAnswer
from app.models.progress import StudentProgress
from app.services.ai_service import AIService

ai_service = AIService()


class QuizService:

    @staticmethod
    def build_quiz(subject, chapter, difficulty, count, question_type, created_by, topic=None):
        """Get-or-generate `count` approved questions for the given scope, then
        wrap them into a Quiz + QuizQuestion rows and return the Quiz."""
        query = Question.query.filter_by(subject_id=subject.id, status="Approved")
        if chapter:
            query = query.filter_by(chapter_id=chapter.id)
        if difficulty:
            query = query.filter_by(difficulty=difficulty)
        if question_type:
            query = query.filter_by(question_type=question_type)
        existing = query.order_by(db.func.random()).limit(count).all()

        questions = list(existing)

        if len(questions) < count:
            needed = count - len(questions)
            topic_name = topic.name if topic else None
            generated = ai_service.generate_questions(
                subject=subject.name,
                chapter=chapter.name if chapter else subject.name,
                topic=topic_name,
                difficulty=difficulty or "Medium",
                count=needed,
                question_type=question_type or "mcq",
            )
            for g in generated:
                question = Question(
                    question_text=g["question"],
                    question_type=question_type or "mcq",
                    difficulty=g.get("difficulty", difficulty or "Medium"),
                    correct_answer=g["correct_answer"],
                    explanation=g.get("explanation", ""),
                    status="Approved",
                    source="ai",
                    subject_id=subject.id,
                    chapter_id=chapter.id if chapter else subject.chapters[0].id,
                    topic_id=topic.id if topic else None,
                    created_by=created_by,
                )
                db.session.add(question)
                db.session.flush()
                from app.models.question import QuestionOption
                for idx, opt_text in enumerate(g["options"][:4]):
                    label = ["A", "B", "C", "D"][idx]
                    db.session.add(QuestionOption(question_id=question.id, option_label=label,
                                                   option_text=opt_text))
                questions.append(question)
            db.session.commit()

        quiz = Quiz(
            title=f"{subject.name}" + (f" - {chapter.name}" if chapter else "") + f" ({difficulty})",
            subject_id=subject.id,
            chapter_id=chapter.id if chapter else None,
            difficulty=difficulty or "Mixed",
            total_questions=len(questions),
            created_by=created_by,
        )
        db.session.add(quiz)
        db.session.flush()

        for idx, q in enumerate(questions):
            db.session.add(QuizQuestion(quiz_id=quiz.id, question_id=q.id, order_index=idx))

        db.session.commit()
        return quiz

    @staticmethod
    def start_attempt(quiz, student_id):
        attempt = QuizAttempt(
            student_id=student_id,
            quiz_id=quiz.id,
            total_questions=quiz.total_questions,
            status="in_progress",
        )
        db.session.add(attempt)
        db.session.commit()
        return attempt

    @staticmethod
    def submit_attempt(attempt, answers_map, time_taken_seconds, timed_out=False):
        """answers_map: {question_id(int): selected_label(str or None)}"""
        correct = wrong = unanswered = 0

        for qq in attempt.quiz.quiz_questions:
            question = qq.question
            selected = answers_map.get(str(question.id)) or answers_map.get(question.id)
            is_correct = False
            if selected:
                is_correct = str(selected).strip().upper() == str(question.correct_answer).strip().upper()
                if is_correct:
                    correct += 1
                else:
                    wrong += 1
            else:
                unanswered += 1

            db.session.add(QuizAnswer(
                attempt_id=attempt.id,
                question_id=question.id,
                selected_answer=selected,
                is_correct=is_correct,
            ))

            QuizService._update_progress(attempt.student_id, question.subject_id, question.chapter_id, is_correct)

        total = attempt.total_questions or (correct + wrong + unanswered)
        percentage = round((correct / total) * 100, 2) if total else 0.0

        attempt.correct_count = correct
        attempt.wrong_count = wrong
        attempt.unanswered_count = unanswered
        attempt.score = correct
        attempt.percentage = percentage
        attempt.time_taken_seconds = time_taken_seconds
        attempt.status = "timed_out" if timed_out else "submitted"
        attempt.submitted_at = datetime.utcnow()

        db.session.commit()
        return attempt

    @staticmethod
    def _update_progress(student_id, subject_id, chapter_id, is_correct):
        for scope_chapter_id in (chapter_id, None):
            row = StudentProgress.query.filter_by(
                student_id=student_id, subject_id=subject_id, chapter_id=scope_chapter_id
            ).first()
            if not row:
                row = StudentProgress(student_id=student_id, subject_id=subject_id,
                                       chapter_id=scope_chapter_id, total_attempts=0,
                                       total_questions=0, total_correct=0)
                db.session.add(row)
            row.total_questions += 1
            if is_correct:
                row.total_correct += 1
            row.last_attempted_at = datetime.utcnow()
            row.recompute_accuracy()
