<div align="center">

# 🧠 QuizMind AI

### AI-Powered Question & Quiz Generator

**Learn Smarter. Practice Better. Score Higher.**

*Your AI-powered exam preparation companion.*

</div>

---

## 📌 Project Name

**QuizMind AI** — an AI-powered question and quiz generator for B.Sc. Computer Science students following the SPPU (Savitribai Phule Pune University) curriculum.

## 📖 Description

QuizMind AI lets an administrator or teacher build the syllabus (**Year → Semester → Subject → Chapter → Topic**) either by hand or by uploading / pasting syllabus text for AI analysis. AI then generates questions strictly from that syllabus. Students register, choose a subject and chapter, take timed quizzes, get instant evaluation with explanations, bookmark questions, and follow their progress through analytics and personalised recommendations.

**The syllabus is not hardcoded.** Everything is database-driven, so the current official SPPU syllabus can be entered without changing any code. The sample syllabus created by `seed.py` is demo data only.

**Highlights**

- Premium mint-green landing page and a fully responsive UI (off-canvas sidebars on mobile)
- Student and admin roles with secure authentication (hashed passwords, CSRF protection, role-based access)
- AI Syllabus Analyzer (PDF / TXT / pasted text → preview → import)
- AI Question Generator (MCQ, True/False; preview before saving) with an admin approval workflow
- Timed quiz (warnings at 10 / 5 / 1 minutes, auto-submit at zero), mark for review, bookmarks
- Result page with score ring and full review; performance charts; recommendations based on real quiz history
- Works without an API key: an offline **demo mode** keeps every feature usable

## 🛠️ Technology Stack

<p align="center">
<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/> <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask"/> <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy"/> <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL"/> <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite"/> <img src="https://img.shields.io/badge/Bootstrap_5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white" alt="Bootstrap_5"/> <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript"/> <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5"/> <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3"/> <img src="https://img.shields.io/badge/Chart.js-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white" alt="Chart.js"/> <img src="https://img.shields.io/badge/Google_Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white" alt="Google_Gemini"/> <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI"/>
</p>

| Layer | Technologies |
|---|---|
| Backend | Python 3, Flask, Flask-SQLAlchemy, Flask-Login, Flask-Migrate, Flask-WTF (CSRF), Werkzeug, python-dotenv, pypdf |
| Database | SQLite (default) or MySQL (PyMySQL) via SQLAlchemy ORM |
| Frontend | HTML5, CSS3, JavaScript (vanilla + Fetch API), Bootstrap 5, Bootstrap Icons, Google Fonts (Sora, Plus Jakarta Sans), Chart.js |
| AI | Provider abstraction: Google Gemini, OpenAI, or offline demo mode (configured via `.env`) |

> The badges load from shields.io, so they need an internet connection to display.

## 📸 Screenshots

### Public pages

**1. Landing page — hero**

Mint-green hero with the floating AI quiz mockup, CTAs and feature pills.

<p align="center"><img src="01-landing-hero.jpg" alt="Landing page — hero" width="900"></p>

**2. Landing page — full page**

Features, how it works, academic years, AI generation, quiz and analytics previews, FAQ, CTA and footer.

<p align="center"><img src="02-landing-full-page.jpg" alt="Landing page — full page" width="900"></p>

**3. Login**

Email + password login with "Remember me" and demo credentials.

<p align="center"><img src="03-login.jpg" alt="Login" width="900"></p>

**4. Student registration**

Name, email, password, academic year and optional college.

<p align="center"><img src="04-register.jpg" alt="Student registration" width="900"></p>

### Student panel

**5. Student dashboard**

Greeting, stat cards, recent attempts, continue practicing, recommendations and weak topics.

<p align="center"><img src="05-student-dashboard.jpg" alt="Student dashboard" width="900"></p>

**6. Subjects**

Browse the syllabus by year and semester; start a quiz for a subject or a single chapter.

<p align="center"><img src="06-student-subjects.jpg" alt="Subjects" width="900"></p>

**7. Quiz setup**

Cascading Year → Semester → Subject → Chapter → Topic, plus difficulty, question count and time limit.

<p align="center"><img src="07-quiz-setup.jpg" alt="Quiz setup" width="900"></p>

**8. Taking a quiz**

Live timer, question navigator (answered / current / marked for review), bookmark button.

<p align="center"><img src="08-quiz-taking.jpg" alt="Taking a quiz" width="900"></p>

**9. Submit confirmation**

"Are you sure you want to submit?" with answered / unanswered counts.

<p align="center"><img src="09-quiz-submit-confirm.jpg" alt="Submit confirmation" width="900"></p>

**10. Result page**

Animated score ring, performance label, correct / wrong / unanswered, accuracy and time taken.

<p align="center"><img src="10-quiz-result.jpg" alt="Result page" width="900"></p>

**11. Question review**

Every question with your answer, the correct answer and the explanation.

<p align="center"><img src="11-quiz-result-review.jpg" alt="Question review" width="900"></p>

**12. Question bank**

Bookmarked questions with subject, chapter and difficulty filters.

<p align="center"><img src="12-student-question-bank.jpg" alt="Question bank" width="900"></p>

**13. Performance analytics**

Score over time, subject / chapter / difficulty accuracy, correct vs incorrect, weak and strong areas.

<p align="center"><img src="13-student-performance.jpg" alt="Performance analytics" width="900"></p>

**14. My attempts**

History of every completed quiz with review and retry.

<p align="center"><img src="14-student-attempts.jpg" alt="My attempts" width="900"></p>

**15. Leaderboard**

Top students ranked by average score.

<p align="center"><img src="15-student-leaderboard.jpg" alt="Leaderboard" width="900"></p>

### Admin panel

**16. Admin dashboard**

Totals for students, subjects, questions, quizzes and attempts, plus registration, attempt and score charts.

<p align="center"><img src="16-admin-dashboard.jpg" alt="Admin dashboard" width="900"></p>

**17. AI Syllabus Analyzer**

Paste or upload a syllabus, preview the detected structure, then import it into the database.

<p align="center"><img src="17-admin-syllabus-analyzer.jpg" alt="AI Syllabus Analyzer" width="900"></p>

**18. Subject management**

Searchable table with edit and delete; same pattern for years, semesters, chapters and topics.

<p align="center"><img src="18-admin-subjects.jpg" alt="Subject management" width="900"></p>

**19. Add / edit modal**

Add and edit records in Bootstrap modals.

<p align="center"><img src="19-admin-add-subject-modal.jpg" alt="Add / edit modal" width="900"></p>

**20. AI Question Generator**

Pick subject, chapter, topic, difficulty, count and type; review the questions before saving.

<p align="center"><img src="20-admin-question-generator.jpg" alt="AI Question Generator" width="900"></p>

**21. Admin question bank**

Search, filter, approve / reject, regenerate, edit and delete questions.

<p align="center"><img src="21-admin-question-bank.jpg" alt="Admin question bank" width="900"></p>

**22. Students**

Search students, activate / deactivate or remove accounts.

<p align="center"><img src="22-admin-students.jpg" alt="Students" width="900"></p>

**23. Analytics**

Average score by subject and question difficulty distribution.

<p align="center"><img src="23-admin-analytics.jpg" alt="Analytics" width="900"></p>

### Mobile

**24. Mobile — landing page**

Responsive layout with a hamburger menu.

<p align="center"><img src="24-mobile-landing.jpg" alt="Mobile — landing page" width="320"></p>

**25. Mobile — dashboard**

Cards stack into a single column.

<p align="center"><img src="25-mobile-dashboard.jpg" alt="Mobile — dashboard" width="320"></p>

**26. Mobile — sidebar**

The sidebar becomes an off-canvas drawer.

<p align="center"><img src="26-mobile-sidebar.jpg" alt="Mobile — sidebar" width="320"></p>

## 📂 Project Directory

```
quizmind-ai/
├── app/                                    # application package
│   ├── models/                             # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── progress.py
│   │   ├── question.py
│   │   ├── quiz.py
│   │   ├── syllabus.py
│   │   └── user.py
│   ├── routes/                             # Flask blueprints
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── api.py
│   │   ├── auth.py
│   │   ├── main.py
│   │   ├── quiz.py
│   │   └── student.py
│   ├── services/                           # AI, syllabus & quiz logic
│   │   ├── __init__.py
│   │   ├── ai_service.py                   # AI provider abstraction (Gemini / OpenAI / demo)
│   │   ├── quiz_service.py                 # quiz building, scoring, progress
│   │   └── syllabus_service.py             # PDF/TXT parsing + syllabus import
│   ├── static/                             # CSS, JS, images
│   │   ├── css/                            # stylesheets
│   │   │   ├── dashboard.css
│   │   │   ├── landing.css
│   │   │   ├── quiz.css
│   │   │   └── style.css
│   │   ├── images/                         # images
│   │   └── js/                             # JavaScript
│   │       ├── admin.js
│   │       ├── dashboard.js
│   │       ├── main.js
│   │       └── quiz.js
│   ├── templates/                          # Jinja2 templates
│   │   ├── admin/                          # admin panel pages
│   │   │   ├── _layout.html
│   │   │   ├── academic_years.html
│   │   │   ├── analytics.html
│   │   │   ├── attempts.html
│   │   │   ├── chapters.html
│   │   │   ├── dashboard.html
│   │   │   ├── question_generator.html
│   │   │   ├── questions.html
│   │   │   ├── semesters.html
│   │   │   ├── settings.html
│   │   │   ├── students.html
│   │   │   ├── subjects.html
│   │   │   ├── syllabus_analyzer.html
│   │   │   └── topics.html
│   │   ├── auth/                           # login / register / profile
│   │   │   ├── forgot_password.html
│   │   │   ├── login.html
│   │   │   ├── profile.html
│   │   │   └── register.html
│   │   ├── errors/                         # 401 / 403 / 404 / 500
│   │   │   ├── 401.html
│   │   │   ├── 403.html
│   │   │   ├── 404.html
│   │   │   └── 500.html
│   │   ├── includes/                       # navbar & footer
│   │   │   ├── footer.html
│   │   │   └── navbar.html
│   │   ├── quiz/                           # quiz setup / take / result
│   │   │   ├── result.html
│   │   │   ├── setup.html
│   │   │   └── take.html
│   │   ├── student/                        # student dashboard pages
│   │   │   ├── _layout.html
│   │   │   ├── attempts.html
│   │   │   ├── dashboard.html
│   │   │   ├── leaderboard.html
│   │   │   ├── performance.html
│   │   │   ├── question_bank.html
│   │   │   ├── settings.html
│   │   │   └── subjects.html
│   │   ├── base.html
│   │   ├── index.html
│   │   └── search_results.html
│   ├── utils/                              # role-based access decorators
│   │   ├── __init__.py
│   │   └── decorators.py
│   └── __init__.py
├── docs/                                   # documentation assets
│   └── screenshots/                        # project screenshots
│           └── ... 26 screenshots (.jpg)
├── migrations/                             # Flask-Migrate (created by flask db init)
├── .env.example                            # environment template
├── README.md                               # this file
├── app.py                                  # entry point (python app.py)
├── config.py                               # configuration, reads .env
├── requirements.txt                        # Python dependencies
└── seed.py                                 # demo data + admin/student accounts
```

## ⚙️ How to Install

### 1. Requirements

- Python 3.9 or newer
- pip
- (Optional) MySQL 8+ if you don't want to use SQLite
- An internet connection in the browser, because Bootstrap, icons, fonts and Chart.js load from CDNs

### 2. Create a virtual environment

```bash
cd quizmind-ai
python -m venv venv
```

Activate it:

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the environment

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and set at least a long random `SECRET_KEY`. The defaults use SQLite and the offline demo AI, so nothing else is required to get started.

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Flask session / CSRF secret. Set a long random value. |
| `DATABASE_URL` | `sqlite:///quizmind.db` (default) or a MySQL URL |
| `AI_PROVIDER` | `demo`, `gemini` or `openai` |
| `AI_API_KEY` | Your provider key (never commit it) |
| `AI_MODEL` | For example `gemini-1.5-flash` |
| `MAX_UPLOAD_SIZE_MB` | Syllabus upload limit |
| `DEFAULT_QUIZ_TIME_MINUTES` | Default quiz time |

### 5. (Optional) Use MySQL instead of SQLite

```sql
CREATE DATABASE quizmind_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Then in `.env`:

```
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/quizmind_ai
```

### 6. Create the tables and demo data

```bash
python seed.py
```

> ⚠️ `seed.py` **drops and recreates all tables.** Run it only on a fresh or development database.

### 7. Run the app

```bash
python app.py
```

Open **http://localhost:5000**

### 8. (Optional) Database migrations

```bash
# Windows: set FLASK_APP=app.py      macOS / Linux: export FLASK_APP=app.py
flask db init
flask db migrate -m "initial"
flask db upgrade
```

## 🚀 How to Use

### Demo accounts

| Role | Email | Password |
|---|---|---|
| Admin | `admin@quizmind.ai` | `Admin@123` |
| Student | `student@quizmind.ai` | `Student@123` |

> ⚠️ These are **demo credentials**. Change them, and your `SECRET_KEY`, before any real deployment.

### As an admin

1. Log in with the admin account. You land on the admin dashboard.
2. **Build the syllabus** in one of two ways:
   - **Syllabus Analyzer:** upload a `.pdf` / `.txt` or paste syllabus text, click **Analyze Syllabus**, review the detected structure, then click **Import to Database**.
   - **Manual:** use **Academic Years → Semesters → Subjects → Chapters → Topics** and add or edit records in the modals.
3. **Generate questions:** open **AI Question Generator**, choose subject / chapter / topic, difficulty, count and type, click **Generate Questions**, review them, then **Save to Question Bank**.
4. **Manage questions:** in **Question Bank**, search and filter, then approve, reject, edit, regenerate or delete questions.
5. Monitor **Students**, **Quiz Attempts** and **Analytics**.

Syllabus Analyzer tip (demo mode): put each item on its own line, for example `Third Year`, `Semester V`, `Subject: Artificial Intelligence`, `Code: CS-501`, `Unit 1: Introduction to AI`, followed by one topic per line.

### As a student

1. **Register** (or log in with the demo student) and pick your academic year.
2. Open **Take Quiz** (or press **Practice** on the Subjects page) and choose Year → Semester → Subject → Chapter, plus difficulty, number of questions and time.
3. Click **Start Quiz**. Pick answers, use **Mark for Review**, jump between questions with the number tiles, and bookmark useful questions.
4. Click **Submit Quiz** and confirm. The quiz also submits automatically when the timer reaches zero.
5. Review your score, accuracy and every explanation, then **Retry Quiz** or **Practice Weak Topics**.
6. Track progress under **Performance**, revisit saved questions in **Question Bank**, and check the **Leaderboard**.

### Connecting a real AI provider

Demo mode (the default) works fully offline, but its questions are generic templates. For syllabus-grounded questions, edit `.env`:

```
AI_PROVIDER=gemini      # or openai
AI_API_KEY=your-key-here
```

Then restart the app. If a provider call fails, the app automatically falls back to demo mode. To add another provider, add a `_call_<name>` method in `app/services/ai_service.py`.

## 🩺 Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Activate the virtual environment and run `pip install -r requirements.txt`. |
| Page looks unstyled | Bootstrap, icons, fonts and Chart.js load from CDNs. Check your internet connection. |
| "CSRF token missing" (400) | Reload the page, enable cookies, and keep `SECRET_KEY` unchanged. |
| MySQL connection error | Check the URL and password, that the database exists, and that `PyMySQL` and `cryptography` are installed. |
| Questions look generic | You are in demo mode. Configure `AI_PROVIDER` and `AI_API_KEY`. |
| PDF gives no text | Scanned PDFs have no extractable text. Paste the syllabus text instead. |
| Port 5000 is busy | Set `PORT=5001` in `.env`, or run `PORT=5001 python app.py`. |

## 📝 Notes

- "Forgot password" is a UI only. No email service is configured.
- Multiple Select can be generated by the admin tool, but the student quiz screen currently supports single-answer questions (MCQ and True/False).
- Screenshots were captured from the seeded demo data running in demo AI mode.

---

<div align="center">

© 2026 QuizMind AI. All rights reserved.

</div>
