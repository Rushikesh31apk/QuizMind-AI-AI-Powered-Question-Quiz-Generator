import re
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models.user import User
from app.models.syllabus import AcademicYear

auth_bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("student.dashboard"))

    years = AcademicYear.query.order_by(AcademicYear.order_index).all()

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        academic_year_id = request.form.get("academic_year_id") or None
        college_name = request.form.get("college_name", "").strip()

        errors = []
        if not full_name or len(full_name) < 2:
            errors.append("Please enter your full name.")
        if not EMAIL_RE.match(email):
            errors.append("Please enter a valid email address.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if User.query.filter_by(email=email).first():
            errors.append("An account with this email already exists.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("auth/register.html", years=years, form=request.form)

        user = User(
            full_name=full_name,
            email=email,
            role="student",
            academic_year_id=int(academic_year_id) if academic_year_id else None,
            college_name=college_name or None,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f"Welcome to QuizMind AI, {user.full_name.split()[0]}! Your account has been created.", "success")
        return redirect(url_for("student.dashboard"))

    return render_template("auth/register.html", years=years, form={})


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard") if current_user.is_admin else url_for("student.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if not user.is_active_account:
                flash("This account has been deactivated. Contact the administrator.", "danger")
                return render_template("auth/login.html")
            login_user(user, remember=remember)
            flash(f"Welcome back, {user.full_name.split()[0]}!", "success")
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            return redirect(url_for("admin.dashboard") if user.is_admin else url_for("student.dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        # Demo-mode notice: no real email service is configured in this project.
        flash("If an account exists with that email, password reset instructions "
              "would be sent. (Email delivery is not configured in this demo.)", "info")
        return redirect(url_for("auth.login"))
    return render_template("auth/forgot_password.html")


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    years = AcademicYear.query.order_by(AcademicYear.order_index).all()

    if request.method == "POST":
        current_user.full_name = request.form.get("full_name", current_user.full_name).strip()
        current_user.college_name = request.form.get("college_name", current_user.college_name)
        academic_year_id = request.form.get("academic_year_id")
        if academic_year_id:
            current_user.academic_year_id = int(academic_year_id)

        new_password = request.form.get("new_password", "")
        if new_password:
            if len(new_password) < 6:
                flash("New password must be at least 6 characters.", "danger")
                return redirect(url_for("auth.profile"))
            current_user.set_password(new_password)

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("auth.profile"))

    return render_template("auth/profile.html", years=years)
