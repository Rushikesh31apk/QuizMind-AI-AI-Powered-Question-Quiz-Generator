"""
AIService - a provider-agnostic abstraction layer for all AI functionality
in QuizMind AI.

Supported providers (set AI_PROVIDER in .env):
    - "gemini" : Google Gemini API (needs AI_API_KEY)
    - "openai" : OpenAI API (needs AI_API_KEY)
    - "demo"   : Fully offline template-based generator (no key needed)

If a real provider is configured but the request fails for any reason
(network error, missing key, bad response, quota, etc.) the service
automatically falls back to the offline demo generator so the rest of
the application keeps working.
"""
import json
import random
import re
from flask import current_app

import requests


class AIService:

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def generate_questions(self, subject, chapter, topic, difficulty, count, question_type="mcq"):
        """Generate a list of question dicts strictly from the given syllabus scope."""
        provider = self._provider()
        prompt = self._build_question_prompt(subject, chapter, topic, difficulty, count, question_type)

        questions = []
        if provider == "gemini":
            questions = self._safe(lambda: self._call_gemini(prompt, expect_json=True))
        elif provider == "openai":
            questions = self._safe(lambda: self._call_openai(prompt, expect_json=True))

        if not questions:
            questions = self._demo_generate_questions(subject, chapter, topic, difficulty, count, question_type)

        return self._validate_questions(questions, difficulty, question_type)[:count]

    def analyze_syllabus(self, raw_text):
        """Extract a structured syllabus tree (years/semesters/subjects/chapters/topics)
        strictly from the supplied text. Returns a dict: {"structure": [...]}"""
        provider = self._provider()
        prompt = self._build_syllabus_prompt(raw_text)

        result = None
        if provider == "gemini":
            result = self._safe(lambda: self._call_gemini(prompt, expect_json=True))
        elif provider == "openai":
            result = self._safe(lambda: self._call_openai(prompt, expect_json=True))

        if not result:
            result = self._demo_analyze_syllabus(raw_text)

        return self._validate_syllabus_structure(result)

    def generate_explanation(self, question_text, correct_answer):
        provider = self._provider()
        prompt = (
            f"Explain briefly and clearly why the correct answer to this question is '{correct_answer}'.\n"
            f"Question: {question_text}\n"
            "Answer in 2-3 sentences, simple academic language, no markdown."
        )
        text = None
        if provider == "gemini":
            text = self._safe(lambda: self._call_gemini(prompt, expect_json=False))
        elif provider == "openai":
            text = self._safe(lambda: self._call_openai(prompt, expect_json=False))

        if not text:
            text = (f"The correct answer is '{correct_answer}'. Review the core definition and "
                    f"reasoning behind this topic to strengthen your understanding.")
        return text

    def generate_practice_recommendations(self, progress_rows):
        """progress_rows: list of dicts with subject, chapter, accuracy, attempts.
        Returns a list of recommendation dicts. Pure logic - no external AI call needed,
        but kept in the AI service since it represents 'intelligent' behaviour."""
        recommendations = []
        for row in sorted(progress_rows, key=lambda r: r["accuracy"]):
            if row["accuracy"] < 60:
                recommendations.append({
                    "type": "weak_area",
                    "subject": row["subject"],
                    "chapter": row.get("chapter"),
                    "message": f"You scored {row['accuracy']:.0f}% in {row['subject']}"
                               + (f" ({row['chapter']})" if row.get("chapter") else "") + ".",
                    "suggestion": f"Practice more questions in {row.get('chapter') or row['subject']} "
                                  f"at Easy/Medium difficulty to build your fundamentals.",
                })
            elif row["accuracy"] >= 85:
                recommendations.append({
                    "type": "strong_area",
                    "subject": row["subject"],
                    "chapter": row.get("chapter"),
                    "message": f"You scored {row['accuracy']:.0f}% in {row['subject']}"
                               + (f" ({row['chapter']})" if row.get("chapter") else "") + ".",
                    "suggestion": f"Try Hard-level questions in {row.get('chapter') or row['subject']} "
                                  f"to push yourself further.",
                })
        return recommendations[:6]

    # ------------------------------------------------------------------
    # Provider helpers
    # ------------------------------------------------------------------
    def _provider(self):
        return current_app.config.get("AI_PROVIDER", "demo")

    def _safe(self, fn):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 - deliberate broad catch for graceful fallback
            current_app.logger.warning(f"AI provider call failed, falling back to demo mode: {exc}")
            return None

    def _call_gemini(self, prompt, expect_json=True):
        api_key = current_app.config.get("AI_API_KEY")
        model = current_app.config.get("AI_MODEL", "gemini-1.5-flash")
        if not api_key:
            raise RuntimeError("AI_API_KEY not configured for Gemini provider")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return self._extract_json(text) if expect_json else text.strip()

    def _call_openai(self, prompt, expect_json=True):
        api_key = current_app.config.get("AI_API_KEY")
        if not api_key:
            raise RuntimeError("AI_API_KEY not configured for OpenAI provider")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.4,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        text = data["choices"][0]["message"]["content"]
        return self._extract_json(text) if expect_json else text.strip()

    @staticmethod
    def _extract_json(text):
        """Pull the first valid JSON object/array out of a raw model response."""
        text = text.strip()
        text = re.sub(r"^```(json)?", "", text.strip())
        text = re.sub(r"```$", "", text.strip())
        match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON found in AI response")
        return json.loads(match.group(1))

    # ------------------------------------------------------------------
    # Prompt builders
    # ------------------------------------------------------------------
    @staticmethod
    def _build_question_prompt(subject, chapter, topic, difficulty, count, question_type):
        scope = f"Subject: {subject}\nChapter: {chapter}"
        if topic:
            scope += f"\nTopic: {topic}"
        return f"""You are an expert academic question setter for B.Sc. Computer Science (SPPU curriculum).

Generate {count} {difficulty}-difficulty {question_type} questions strictly from the syllabus content below.
Do not introduce concepts outside the provided topic. Avoid duplicate questions.
Ensure exactly one correct answer for MCQs. Generate plausible distractors.

{scope}

Return ONLY a JSON array, no other text, in this exact format:
[
  {{
    "question": "...",
    "options": ["...", "...", "...", "..."],
    "correct_answer": "A",
    "explanation": "...",
    "difficulty": "{difficulty}"
  }}
]
"""

    @staticmethod
    def _build_syllabus_prompt(raw_text):
        return f"""You are a syllabus parsing assistant for an Indian university (SPPU) B.Sc. Computer Science
curriculum. Extract ONLY the structure that is explicitly present in the text below.
Do NOT invent academic years, semesters, subjects, units or topics that are not present in the text.

TEXT:
\"\"\"{raw_text[:8000]}\"\"\"

Return ONLY JSON in this exact format:
{{
  "structure": [
    {{
      "academic_year": "...",
      "semester": "...",
      "subject": "...",
      "subject_code": "...",
      "units": [
        {{"unit_name": "Unit 1: ...", "topics": ["...", "..."]}}
      ]
    }}
  ]
}}
"""

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    @staticmethod
    def _validate_questions(questions, difficulty, question_type):
        valid = []
        seen = set()
        if not isinstance(questions, list):
            return valid
        for q in questions:
            try:
                text = str(q["question"]).strip()
                options = list(q.get("options", []))
                correct = str(q.get("correct_answer", "A")).strip().upper()
                if not text or text.lower() in seen:
                    continue
                if question_type == "true_false":
                    options = options[:2] if len(options) >= 2 else ["True", "False"]
                else:
                    if len(options) < 2:
                        continue
                    options = options[:4]
                    while len(options) < 4:
                        options.append("None of the above")
                if correct not in ["A", "B", "C", "D"]:
                    correct = "A"
                seen.add(text.lower())
                valid.append({
                    "question": text,
                    "options": options,
                    "correct_answer": correct,
                    "explanation": str(q.get("explanation", "")).strip() or "No explanation provided.",
                    "difficulty": q.get("difficulty", difficulty),
                })
            except (KeyError, TypeError, ValueError):
                continue
        return valid

    @staticmethod
    def _validate_syllabus_structure(result):
        if not isinstance(result, dict) or "structure" not in result:
            return {"structure": []}
        cleaned = []
        for item in result.get("structure", []):
            if not isinstance(item, dict):
                continue
            units = []
            for u in item.get("units", []):
                if not isinstance(u, dict):
                    continue
                topics = [str(t).strip() for t in u.get("topics", []) if str(t).strip()]
                if u.get("unit_name"):
                    units.append({"unit_name": str(u["unit_name"]).strip(), "topics": topics})
            if item.get("subject") and item.get("academic_year") and item.get("semester"):
                cleaned.append({
                    "academic_year": str(item["academic_year"]).strip(),
                    "semester": str(item["semester"]).strip(),
                    "subject": str(item["subject"]).strip(),
                    "subject_code": str(item.get("subject_code", "")).strip(),
                    "units": units,
                })
        return {"structure": cleaned}

    # ------------------------------------------------------------------
    # Offline "demo" generators (no external API required)
    # ------------------------------------------------------------------
    def _demo_generate_questions(self, subject, chapter, topic, difficulty, count, question_type):
        """Deterministic-ish template generator so the app fully works with zero API key."""
        focus = topic or chapter or subject
        templates = [
            "Which of the following best describes {focus}?",
            "In the context of {chapter}, what is the primary purpose of {focus}?",
            "Which statement about {focus} is correct?",
            "What is a key characteristic of {focus} in {subject}?",
            "Which of the following is an example related to {focus}?",
            "Which of these is NOT typically associated with {focus}?",
            "In {subject}, {focus} is mainly used for which purpose?",
            "Identify the correct definition of {focus}.",
            "Which technique/concept is closely related to {focus}?",
            "What is an important advantage of understanding {focus} in {chapter}?",
        ]
        random.shuffle(templates)
        questions = []
        for i in range(count):
            template = templates[i % len(templates)]
            q_text = template.format(focus=focus, chapter=chapter, subject=subject)
            if question_type == "true_false":
                statement = f"{focus} is a fundamental concept covered under {chapter} in {subject}."
                questions.append({
                    "question": f"True or False: {statement}",
                    "options": ["True", "False"],
                    "correct_answer": "A",
                    "explanation": f"This statement correctly reflects how {focus} fits within {chapter}.",
                    "difficulty": difficulty,
                })
                continue

            correct_idx = random.choice(["A", "B", "C", "D"])
            options = [
                f"A correct conceptual explanation of {focus}",
                f"An unrelated concept from a different chapter",
                f"A partially correct but incomplete description of {focus}",
                f"A common misconception about {focus}",
            ]
            random.shuffle(options)
            # Ensure the "correct" one is placed at the chosen index for demo purposes
            correct_text = f"A correct conceptual explanation of {focus}"
            options.remove(correct_text)
            idx_map = {"A": 0, "B": 1, "C": 2, "D": 3}
            options.insert(idx_map[correct_idx], correct_text)

            questions.append({
                "question": f"({i+1}) {q_text}",
                "options": options,
                "correct_answer": correct_idx,
                "explanation": f"{focus} relates directly to the core ideas taught in {chapter} of {subject}. "
                                f"[Demo mode: connect a real AI provider in .env for richer, syllabus-grounded "
                                f"questions.]",
                "difficulty": difficulty,
            })
        return questions

    def _demo_analyze_syllabus(self, raw_text):
        """A lightweight rule-based extractor used when no AI provider is configured.
        Looks for common patterns like 'Year', 'Semester', 'Unit', numbered topics."""
        year_match = re.search(r"(first|second|third)\s+year", raw_text, re.IGNORECASE)
        sem_match = re.search(r"semester\s*[-:]?\s*([IVX\d]+)", raw_text, re.IGNORECASE)
        subject_match = re.search(r"subject\s*[:\-]\s*(.+)", raw_text, re.IGNORECASE)
        code_match = re.search(r"(code)\s*[:\-]\s*([A-Za-z0-9\-]+)", raw_text, re.IGNORECASE)

        academic_year = (year_match.group(0).title() if year_match else "First Year") + " B.Sc. Computer Science"
        semester = f"Semester {sem_match.group(1)}" if sem_match else "Semester 1"
        subject = subject_match.group(1).strip()[:100] if subject_match else "Imported Subject"
        subject_code = code_match.group(2).strip() if code_match else ""

        units = []
        unit_blocks = re.split(r"(?=unit\s*[-:]?\s*\d+)", raw_text, flags=re.IGNORECASE)
        for block in unit_blocks:
            block = block.strip()
            if not block or not re.match(r"unit\s*[-:]?\s*\d+", block, re.IGNORECASE):
                continue
            title_match = re.match(r"(unit\s*[-:]?\s*\d+\s*[:\-]?\s*[^\n]*)", block, re.IGNORECASE)
            unit_name = title_match.group(1).strip() if title_match else block.splitlines()[0]
            body = block[len(unit_name):]
            raw_topics = re.split(r"[\n,;•]", body)
            topics = [t.strip(" -.\t") for t in raw_topics if 3 < len(t.strip(" -.\t")) < 120]
            if unit_name:
                units.append({"unit_name": unit_name[:150], "topics": topics[:12]})

        if not units:
            # Fallback: treat non-empty lines as topics under one generic unit
            lines = [l.strip(" -.\t") for l in raw_text.splitlines() if 3 < len(l.strip()) < 120]
            if lines:
                units = [{"unit_name": "Unit 1: Extracted Topics", "topics": lines[:12]}]

        return {
            "structure": [{
                "academic_year": academic_year,
                "semester": semester,
                "subject": subject,
                "subject_code": subject_code,
                "units": units,
            }]
        }
