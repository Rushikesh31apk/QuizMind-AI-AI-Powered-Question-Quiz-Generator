"""
QuizMind AI - Entry point.
Run with:  python app.py
"""
import os
from app import create_app, db

app = create_app(os.environ.get("FLASK_ENV", "development"))

# Make sure tables exist so `python app.py` works even before running seed.py
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", True))
