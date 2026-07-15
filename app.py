"""
SkillBridge - A platform connecting students with real-world micro-tasks
posted by companies, so students can build proof of skill (certificates,
ratings, and experience) while companies get affordable, verified work done.

Run locally:
    pip install -r requirements.txt
    python app.py
Then open http://127.0.0.1:5000
"""

import os
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-this-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///skillbridge.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    skills = db.Column(db.String(300), default="")  # comma-separated
    bio = db.Column(db.String(500), default="")
    rating_total = db.Column(db.Integer, default=0)
    rating_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def skill_list(self):
        return [s.strip() for s in self.skills.split(",") if s.strip()]

    @property
    def average_rating(self):
        if self.rating_count == 0:
            return 0
        return round(self.rating_total / self.rating_count, 1)


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    about = db.Column(db.String(500), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    skill_required = db.Column(db.String(100), nullable=False)
    payment = db.Column(db.Integer, default=0)  # 0 = unpaid / for-experience task
    status = db.Column(db.String(20), default="open")  # open, in_progress, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship("Company", backref="tasks")


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending, accepted, rejected, submitted, rated
    submission_note = db.Column(db.Text, default="")
    rating_given = db.Column(db.Integer, default=0)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    task = db.relationship("Task", backref="applications")
    student = db.relationship("Student", backref="applications")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def login_required(role=None):
    """Decorator to require a logged-in student or company (or either)."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if "user_id" not in session or "role" not in session:
                flash("Please log in to continue.", "error")
                return redirect(url_for("login"))
            if role and session["role"] != role:
                flash("That page isn't available for your account type.", "error")
                return redirect(url_for("home"))
            return f(*args, **kwargs)
        return wrapped
    return decorator


def current_student():
    if session.get("role") == "student":
        return Student.query.get(session["user_id"])
    return None


def current_company():
    if session.get("role") == "company":
        return Company.query.get(session["user_id"])
    return None


def match_score(task_skill, student_skills):
    """Simple skill-matching: exact case-insensitive match = strong match."""
    task_skill = task_skill.strip().lower()
    return any(task_skill == s.lower() for s in student_skills)


@app.context_processor
def inject_user():
    return dict(current_student=current_student(), current_company=current_company())


# ---------------------------------------------------------------------------
# Routes: general
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    open_tasks_count = Task.query.filter_by(status="open").count()
    student_count = Student.query.count()
    company_count = Company.query.count()
    recent_tasks = Task.query.filter_by(status="open").order_by(Task.created_at.desc()).limit(3).all()
    return render_template(
        "index.html",
        open_tasks_count=open_tasks_count,
        student_count=student_count,
        company_count=company_count,
        recent_tasks=recent_tasks,
    )


@app.route("/logout")
def logout():
    session.clear()
    flash("You've been logged out.", "success")
    return redirect(url_for("home"))


# ---------------------------------------------------------------------------
# Routes: student auth
# ---------------------------------------------------------------------------

@app.route("/student/signup", methods=["GET", "POST"])
def student_signup():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        skills = request.form.get("skills", "").strip()

        if Student.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "error")
            return redirect(url_for("student_signup"))

        student = Student(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            skills=skills,
        )
        db.session.add(student)
        db.session.commit()

        session["user_id"] = student.id
        session["role"] = "student"
        flash(f"Welcome to SkillBridge, {student.name}!", "success")
        return redirect(url_for("student_dashboard"))

    return render_template("student_signup.html")


@app.route("/company/signup", methods=["GET", "POST"])
def company_signup():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        about = request.form.get("about", "").strip()

        if Company.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "error")
            return redirect(url_for("company_signup"))

        company = Company(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            about=about,
        )
        db.session.add(company)
        db.session.commit()

        session["user_id"] = company.id
        session["role"] = "company"
        flash(f"Welcome to SkillBridge, {company.name}!", "success")
        return redirect(url_for("company_dashboard"))

    return render_template("company_signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form["role"]
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        model = Student if role == "student" else Company
        user = model.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["role"] = role
            flash("Logged in successfully.", "success")
            return redirect(url_for("student_dashboard" if role == "student" else "company_dashboard"))

        flash("Incorrect email or password.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


# ---------------------------------------------------------------------------
# Routes: tasks
# ---------------------------------------------------------------------------

@app.route("/tasks")
def tasks():
    skill_filter = request.args.get("skill", "").strip()
    query = Task.query.filter_by(status="open")
    if skill_filter:
        query = query.filter(Task.skill_required.ilike(f"%{skill_filter}%"))
    task_list = query.order_by(Task.created_at.desc()).all()

    student = current_student()
    matched_ids = set()
    if student:
        matched_ids = {
            t.id for t in task_list if match_score(t.skill_required, student.skill_list)
        }

    all_skills = sorted({t.skill_required for t in Task.query.all()})
    return render_template(
        "tasks.html",
        tasks=task_list,
        matched_ids=matched_ids,
        skill_filter=skill_filter,
        all_skills=all_skills,
    )


@app.route("/tasks/<int:task_id>")
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)
    already_applied = False
    student = current_student()
    if student:
        already_applied = Application.query.filter_by(task_id=task.id, student_id=student.id).first() is not None
    return render_template("task_detail.html", task=task, already_applied=already_applied)


@app.route("/tasks/<int:task_id>/apply", methods=["POST"])
@login_required(role="student")
def apply_task(task_id):
    task = Task.query.get_or_404(task_id)
    student = current_student()

    existing = Application.query.filter_by(task_id=task.id, student_id=student.id).first()
    if existing:
        flash("You've already applied to this task.", "error")
        return redirect(url_for("task_detail", task_id=task.id))

    application = Application(task_id=task.id, student_id=student.id, status="pending")
    db.session.add(application)
    db.session.commit()
    flash("Application submitted! The company will review it soon.", "success")
    return redirect(url_for("task_detail", task_id=task.id))


@app.route("/post-task", methods=["GET", "POST"])
@login_required(role="company")
def post_task():
    if request.method == "POST":
        company = current_company()
        task = Task(
            company_id=company.id,
            title=request.form["title"].strip(),
            description=request.form["description"].strip(),
            skill_required=request.form["skill_required"].strip(),
            payment=int(request.form.get("payment") or 0),
        )
        db.session.add(task)
        db.session.commit()
        flash("Task posted successfully.", "success")
        return redirect(url_for("company_dashboard"))

    return render_template("post_task.html")


# ---------------------------------------------------------------------------
# Routes: dashboards
# ---------------------------------------------------------------------------

@app.route("/dashboard/student")
@login_required(role="student")
def student_dashboard():
    student = current_student()
    applications = Application.query.filter_by(student_id=student.id).order_by(Application.applied_at.desc()).all()

    recommended = [
        t for t in Task.query.filter_by(status="open").all()
        if match_score(t.skill_required, student.skill_list)
    ]

    return render_template("student_dashboard.html", student=student, applications=applications, recommended=recommended)


@app.route("/dashboard/company")
@login_required(role="company")
def company_dashboard():
    company = current_company()
    my_tasks = Task.query.filter_by(company_id=company.id).order_by(Task.created_at.desc()).all()
    return render_template("company_dashboard.html", company=company, tasks=my_tasks)


@app.route("/applications/<int:app_id>/decision", methods=["POST"])
@login_required(role="company")
def application_decision(app_id):
    application = Application.query.get_or_404(app_id)
    decision = request.form["decision"]  # accepted / rejected
    if application.task.company_id != session["user_id"]:
        flash("You don't have permission to do that.", "error")
        return redirect(url_for("company_dashboard"))

    application.status = decision
    db.session.commit()
    flash(f"Application {decision}.", "success")
    return redirect(url_for("company_dashboard"))


@app.route("/applications/<int:app_id>/rate", methods=["POST"])
@login_required(role="company")
def rate_application(app_id):
    application = Application.query.get_or_404(app_id)
    if application.task.company_id != session["user_id"]:
        flash("You don't have permission to do that.", "error")
        return redirect(url_for("company_dashboard"))

    rating = int(request.form["rating"])
    application.rating_given = rating
    application.status = "rated"
    application.task.status = "completed"

    student = application.student
    student.rating_total += rating
    student.rating_count += 1

    db.session.commit()
    flash("Rating submitted. The student's profile has been updated.", "success")
    return redirect(url_for("company_dashboard"))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

# Create tables at import time too, so this also works when run under
# gunicorn on Render (gunicorn imports this module instead of running
# the __main__ block below).
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
