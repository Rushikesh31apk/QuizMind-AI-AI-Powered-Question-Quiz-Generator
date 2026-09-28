"""
QuizMind AI - Seed Script
Populates the database with:
  - An admin account
  - A demo student account
  - A sample B.Sc. Computer Science academic structure (years/semesters/subjects/chapters/topics)
  - Sample AI-style questions
  - A couple of sample quiz attempts for the demo student (so the dashboard/analytics
    pages have something to show immediately)

DEMO CREDENTIALS (CHANGE THESE BEFORE ANY REAL/PRODUCTION USE):
  Admin:   admin@quizmind.ai   / Admin@123
  Student: student@quizmind.ai / Student@123

Run with:  python seed.py
"""
import random
from datetime import datetime, timedelta

from app import create_app, db
from app.models.user import User
from app.models.syllabus import AcademicYear, Semester, Subject, Chapter, Topic
from app.models.question import Question, QuestionOption
from app.models.quiz import Quiz, QuizQuestion, QuizAttempt, QuizAnswer
from app.models.progress import StudentProgress

app = create_app("development")

SYLLABUS = {
    "First Year B.Sc. Computer Science": {
        "Semester 1": {
            "Programming Fundamentals": {
                "code": "CS101",
                "chapters": {
                    "Unit 1: Introduction to Programming": [
                        "Algorithms and Flowcharts", "Variables and Data Types", "Operators and Expressions",
                    ],
                    "Unit 2: Control Structures": [
                        "Conditional Statements", "Loops", "Break and Continue",
                    ],
                    "Unit 3: Functions and Arrays": [
                        "Function Definition and Calling", "Recursion", "Arrays and Strings",
                    ],
                },
            },
            "Digital Electronics": {
                "code": "CS102",
                "chapters": {
                    "Unit 1: Number Systems": [
                        "Binary, Octal, Hexadecimal", "Number System Conversions", "Binary Arithmetic",
                    ],
                    "Unit 2: Logic Gates": [
                        "Basic Gates", "Boolean Algebra", "Karnaugh Maps",
                    ],
                },
            },
        },
        "Semester 2": {
            "Object Oriented Programming": {
                "code": "CS103",
                "chapters": {
                    "Unit 1: OOP Concepts": [
                        "Classes and Objects", "Encapsulation", "Inheritance", "Polymorphism",
                    ],
                    "Unit 2: Exception Handling": [
                        "Try-Catch Blocks", "Custom Exceptions",
                    ],
                },
            },
        },
    },
    "Second Year B.Sc. Computer Science": {
        "Semester 3": {
            "Data Structures": {
                "code": "CS201",
                "chapters": {
                    "Unit 1: Linear Data Structures": [
                        "Arrays", "Linked Lists", "Stacks", "Queues",
                    ],
                    "Unit 2: Trees": [
                        "Binary Trees", "Binary Search Trees", "AVL Trees", "Tree Traversals",
                    ],
                    "Unit 3: Graphs": [
                        "Graph Representation", "BFS and DFS", "Shortest Path Algorithms",
                    ],
                },
            },
            "Database Management Systems": {
                "code": "CS202",
                "chapters": {
                    "Unit 1: Introduction to DBMS": [
                        "Database Models", "ER Diagrams", "Relational Model",
                    ],
                    "Unit 2: SQL": [
                        "DDL and DML Commands", "Joins", "Subqueries", "Normalization",
                    ],
                },
            },
        },
        "Semester 4": {
            "Operating Systems": {
                "code": "CS203",
                "chapters": {
                    "Unit 1: OS Fundamentals": [
                        "Process Management", "Process Scheduling", "Threads",
                    ],
                    "Unit 2: Memory Management": [
                        "Paging", "Segmentation", "Virtual Memory",
                    ],
                    "Unit 3: Deadlocks": [
                        "Deadlock Conditions", "Deadlock Prevention", "Banker's Algorithm",
                    ],
                },
            },
        },
    },
    "Third Year B.Sc. Computer Science": {
        "Semester 5": {
            "Artificial Intelligence": {
                "code": "CS301",
                "chapters": {
                    "Unit 1: Introduction to AI": [
                        "Intelligent Agents", "Problem Solving", "Search Techniques",
                    ],
                    "Unit 2: Knowledge Representation": [
                        "Propositional Logic", "Predicate Logic", "Semantic Networks",
                    ],
                },
            },
            "Computer Networks": {
                "code": "CS302",
                "chapters": {
                    "Unit 1: Network Fundamentals": [
                        "OSI Model", "TCP/IP Model", "Network Topologies",
                    ],
                    "Unit 2: Routing": [
                        "Routing Algorithms", "IP Addressing", "Subnetting",
                    ],
                },
            },
        },
        "Semester 6": {
            "Web Technologies": {
                "code": "CS303",
                "chapters": {
                    "Unit 1: Web Fundamentals": [
                        "HTML5 and CSS3", "JavaScript Basics", "Responsive Design",
                    ],
                    "Unit 2: Server-Side Development": [
                        "Flask Framework", "REST APIs", "Database Integration",
                    ],
                },
            },
            "Software Engineering": {
                "code": "CS304",
                "chapters": {
                    "Unit 1: SDLC Models": [
                        "Waterfall Model", "Agile Methodology", "Spiral Model",
                    ],
                    "Unit 2: Software Testing": [
                        "Unit Testing", "Integration Testing", "Test Case Design",
                    ],
                },
            },
        },
    },
}


def seed():
    with app.app_context():
        print("Dropping and recreating all tables...")
        db.drop_all()
        db.create_all()

        # ---------------- Users ----------------
        print("Creating admin and demo student accounts...")
        admin = User(full_name="QuizMind Administrator", email="admin@quizmind.ai", role="admin")
        admin.set_password("Admin@123")
        db.session.add(admin)

        student = User(full_name="Rushikesh Patil", email="student@quizmind.ai", role="student",
                        college_name="Modern College of Arts, Science and Commerce")
        student.set_password("Student@123")
        db.session.add(student)
        db.session.flush()

        # ---------------- Academic structure ----------------
        print("Building academic year -> semester -> subject -> chapter -> topic tree...")
        subject_lookup = {}  # name -> Subject
        for year_order, (year_name, semesters) in enumerate(SYLLABUS.items()):
            year = AcademicYear(name=year_name, order_index=year_order)
            db.session.add(year)
            db.session.flush()

            for sem_order, (sem_name, subjects) in enumerate(semesters.items()):
                semester = Semester(name=sem_name, academic_year_id=year.id, order_index=sem_order)
                db.session.add(semester)
                db.session.flush()

                for subject_name, subject_data in subjects.items():
                    subject = Subject(name=subject_name, code=subject_data["code"], semester_id=semester.id)
                    db.session.add(subject)
                    db.session.flush()
                    subject_lookup[subject_name] = subject

                    for chap_order, (chapter_name, topics) in enumerate(subject_data["chapters"].items()):
                        chapter = Chapter(name=chapter_name, subject_id=subject.id, order_index=chap_order)
                        db.session.add(chapter)
                        db.session.flush()

                        for topic_name in topics:
                            db.session.add(Topic(name=topic_name, chapter_id=chapter.id))

        # student's academic year = Second Year (for demo dashboard relevance)
        second_year = AcademicYear.query.filter_by(name="Second Year B.Sc. Computer Science").first()
        student.academic_year_id = second_year.id if second_year else None

        db.session.commit()

        # ---------------- Sample questions ----------------
        print("Generating sample questions for a few chapters...")
        from app.services.ai_service import AIService
        ai = AIService()

        sample_chapters = Chapter.query.limit(20).all()
        with app.test_request_context():
            for chapter in sample_chapters:
                subject = chapter.subject
                for difficulty in ["Easy", "Medium", "Hard"]:
                    generated = ai._demo_generate_questions(
                        subject=subject.name, chapter=chapter.name, topic=None,
                        difficulty=difficulty, count=4, question_type="mcq",
                    )
                    for g in generated:
                        q = Question(
                            question_text=g["question"], question_type="mcq", difficulty=difficulty,
                            correct_answer=g["correct_answer"], explanation=g["explanation"],
                            status="Approved", source="ai", subject_id=subject.id, chapter_id=chapter.id,
                            created_by=admin.id,
                        )
                        db.session.add(q)
                        db.session.flush()
                        for idx, opt in enumerate(g["options"]):
                            db.session.add(QuestionOption(
                                question_id=q.id, option_label=["A", "B", "C", "D"][idx], option_text=opt))
        db.session.commit()

        # ---------------- Sample quiz attempts for demo student ----------------
        print("Creating sample quiz attempts for the demo student...")
        ds_chapter = Chapter.query.join(Subject).filter(Subject.name == "Data Structures").first()
        dbms_chapter = Chapter.query.join(Subject).filter(Subject.name == "Database Management Systems").first()
        py_chapter = Chapter.query.join(Subject).filter(Subject.name == "Programming Fundamentals").first()

        sample_configs = [
            (ds_chapter, "Medium", 55, 6),
            (dbms_chapter, "Easy", 62, 9),
            (py_chapter, "Easy", 91, 15),
        ]

        for chapter, difficulty, target_pct, days_ago in sample_configs:
            if not chapter:
                continue
            questions = Question.query.filter_by(chapter_id=chapter.id, difficulty=difficulty).limit(10).all()
            if not questions:
                continue

            quiz = Quiz(title=f"{chapter.subject.name} - {chapter.name} ({difficulty})",
                        subject_id=chapter.subject_id, chapter_id=chapter.id, difficulty=difficulty,
                        total_questions=len(questions), created_by=student.id)
            db.session.add(quiz)
            db.session.flush()
            for idx, q in enumerate(questions):
                db.session.add(QuizQuestion(quiz_id=quiz.id, question_id=q.id, order_index=idx))

            attempt = QuizAttempt(student_id=student.id, quiz_id=quiz.id, status="submitted",
                                   total_questions=len(questions),
                                   started_at=datetime.utcnow() - timedelta(days=days_ago, minutes=20),
                                   submitted_at=datetime.utcnow() - timedelta(days=days_ago))
            db.session.add(attempt)
            db.session.flush()

            num_correct = round(len(questions) * target_pct / 100)
            correct = 0
            for i, q in enumerate(questions):
                is_correct = i < num_correct
                selected = q.correct_answer if is_correct else random.choice(
                    [o for o in ["A", "B", "C", "D"] if o != q.correct_answer])
                db.session.add(QuizAnswer(attempt_id=attempt.id, question_id=q.id,
                                           selected_answer=selected, is_correct=is_correct))
                if is_correct:
                    correct += 1

                progress = StudentProgress.query.filter_by(
                    student_id=student.id, subject_id=chapter.subject_id, chapter_id=None).first()
                if not progress:
                    progress = StudentProgress(student_id=student.id, subject_id=chapter.subject_id,
                                                chapter_id=None, total_questions=0, total_correct=0)
                    db.session.add(progress)
                progress.total_questions += 1
                progress.total_correct += 1 if is_correct else 0
                progress.recompute_accuracy()

            attempt.correct_count = correct
            attempt.wrong_count = len(questions) - correct
            attempt.unanswered_count = 0
            attempt.score = correct
            attempt.percentage = round((correct / len(questions)) * 100, 2)
            attempt.time_taken_seconds = random.randint(300, 900)

        db.session.commit()

        print("\n" + "=" * 60)
        print("Seed data created successfully!")
        print("=" * 60)
        print("DEMO CREDENTIALS (change these before production use):")
        print("  Admin   -> email: admin@quizmind.ai   | password: Admin@123")
        print("  Student -> email: student@quizmind.ai | password: Student@123")
        print("=" * 60)


if __name__ == "__main__":
    seed()
