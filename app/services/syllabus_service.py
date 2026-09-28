"""
SyllabusService - handles syllabus file text extraction and importing a
validated structure (produced by AIService.analyze_syllabus) into the
relational database.
"""
from app import db
from app.models.syllabus import AcademicYear, Semester, Subject, Chapter, Topic


class SyllabusService:

    @staticmethod
    def extract_text_from_file(file_storage, filename):
        """Extract raw text from an uploaded .pdf or .txt file."""
        ext = filename.rsplit(".", 1)[-1].lower()
        if ext == "txt":
            return file_storage.read().decode("utf-8", errors="ignore")
        if ext == "pdf":
            from pypdf import PdfReader
            reader = PdfReader(file_storage)
            text = []
            for page in reader.pages:
                text.append(page.extract_text() or "")
            return "\n".join(text)
        raise ValueError("Unsupported file type")

    @staticmethod
    def import_structure(structure):
        """Insert a validated syllabus structure (list of dicts) into the database.
        Reuses existing academic years / semesters / subjects where names already match,
        so importing the same syllabus twice does not create duplicates."""
        created = {"academic_years": 0, "semesters": 0, "subjects": 0, "chapters": 0, "topics": 0}

        for item in structure:
            year = AcademicYear.query.filter_by(name=item["academic_year"]).first()
            if not year:
                year = AcademicYear(name=item["academic_year"], order_index=AcademicYear.query.count())
                db.session.add(year)
                db.session.flush()
                created["academic_years"] += 1

            semester = Semester.query.filter_by(name=item["semester"], academic_year_id=year.id).first()
            if not semester:
                semester = Semester(name=item["semester"], academic_year_id=year.id,
                                     order_index=len(year.semesters))
                db.session.add(semester)
                db.session.flush()
                created["semesters"] += 1

            subject = Subject.query.filter_by(name=item["subject"], semester_id=semester.id).first()
            if not subject:
                subject = Subject(name=item["subject"], code=item.get("subject_code", ""),
                                   semester_id=semester.id)
                db.session.add(subject)
                db.session.flush()
                created["subjects"] += 1

            for order, unit in enumerate(item.get("units", [])):
                chapter = Chapter.query.filter_by(name=unit["unit_name"], subject_id=subject.id).first()
                if not chapter:
                    chapter = Chapter(name=unit["unit_name"], subject_id=subject.id, order_index=order)
                    db.session.add(chapter)
                    db.session.flush()
                    created["chapters"] += 1

                for topic_name in unit.get("topics", []):
                    exists = Topic.query.filter_by(name=topic_name, chapter_id=chapter.id).first()
                    if not exists:
                        db.session.add(Topic(name=topic_name, chapter_id=chapter.id))
                        created["topics"] += 1

        db.session.commit()
        return created
