import os
import json
import time
import secrets
from datetime import datetime

from flask import (
    Flask, render_template, redirect, url_for,
    request, session, abort
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user,
    login_required, current_user, logout_user
)
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash


# --------------------------------------------------
# APP CONFIGURATION
# --------------------------------------------------

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "change-this-secret-key-before-deployment"
)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///peakprep.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = 60 * 60 * 5

db = SQLAlchemy(app)
csrf = CSRFProtect(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "warning"


# --------------------------------------------------
# DATABASE MODELS
# --------------------------------------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)


class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    result_key = db.Column(
        db.String(32), unique=True, nullable=False, index=True
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False, index=True
    )
    result_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.Float, default=time.time, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (ValueError, TypeError):
        return None


# --------------------------------------------------
# QUESTION BANK
# --------------------------------------------------

from question_bank import QUESTION_SETS


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# REGISTER
# --------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not email or not password:
            error = "Please fill in all required fields."

        elif len(username) > 80:
            error = "Username must be 80 characters or fewer."

        elif len(email) > 150:
            error = "Email must be 150 characters or fewer."

        elif len(password) < 8:
            error = "Password must contain at least 8 characters."

        elif password != confirm_password:
            error = "Passwords do not match."

        elif User.query.filter_by(username=username).first():
            error = "This username is already registered."

        elif User.query.filter_by(email=email).first():
            error = "This email is already registered."

        if error:
            return render_template("register.html", error=error)

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )

        try:
            db.session.add(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            app.logger.exception("Registration failed")
            return render_template(
                "register.html",
                error="Registration failed. Please try again."
            )

        login_user(user)
        return redirect(url_for("dashboard"))

    return render_template("register.html", error=error)


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    error = None

    if request.method == "POST":
        identity = request.form.get("identity", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter(
            db.or_(
                User.username == identity,
                User.email == identity.lower()
            )
        ).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("dashboard"))

        error = "Incorrect username/email or password."

    return render_template("login.html", error=error)


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    main_tests = QUESTION_SETS.get("main", {})
    advanced_tests = QUESTION_SETS.get("advanced", {})

    recent_results = (
        TestResult.query
        .filter_by(user_id=current_user.id)
        .order_by(TestResult.created_at.desc())
        .limit(10)
        .all()
    )

    results = []

    for saved in recent_results:
        try:
            result = json.loads(saved.result_json)

            timestamp = result.get(
                "submitted_at",
                saved.created_at
            )

            try:
                result["date_label"] = datetime.fromtimestamp(
                    float(timestamp)
                ).strftime("%d %b %Y")
            except (TypeError, ValueError, OSError):
                result["date_label"] = "Date unavailable"

            results.append(result)

        except (json.JSONDecodeError, TypeError):
            app.logger.warning(
                "A saved test result could not be read."
            )

    return render_template(
        "dashboard.html",
        main_tests=main_tests,
        advanced_tests=advanced_tests,
        recent_results=results
    )


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    session.pop("attempt", None)
    session.pop("last_result_id", None)

    return redirect(url_for("home"))


# --------------------------------------------------
# START MOCK TEST
# --------------------------------------------------

@app.route("/mock-test/<exam>/<int:set_no>", methods=["GET", "POST"])
@login_required
def mock_test(exam, set_no):
    exam = exam.lower()

    if exam not in QUESTION_SETS:
        abort(404)

    if set_no not in QUESTION_SETS[exam]:
        abort(404)

    paper = QUESTION_SETS[exam][set_no]
    questions = paper["questions"]
    attempt_key = f"{exam}_{set_no}"

    attempt = session.get("attempt")

    if request.method == "GET":
        if not attempt or attempt.get("key") != attempt_key:
            attempt = {
                "key": attempt_key,
                "started": time.time(),
                "token": secrets.token_hex(16)
            }

            session["attempt"] = attempt
            session.modified = True

    if not attempt or attempt.get("key") != attempt_key:
        if request.method == "POST":
            return redirect(
                url_for("mock_test", exam=exam, set_no=set_no)
            )

        return redirect(url_for("dashboard"))

    try:
        started = float(attempt["started"])
    except (KeyError, TypeError, ValueError):
        session.pop("attempt", None)
        return redirect(url_for("dashboard"))

    duration_seconds = int(paper["duration"] * 60)
    elapsed = max(0, int(time.time() - started))
    remaining = max(0, duration_seconds - elapsed)

    # --------------------------------------------------
    # SUBMIT AND SCORE TEST
    # --------------------------------------------------

    if request.method == "POST":
        correct = 0
        wrong = 0
        unanswered = 0
        score = 0
        answers = {}

        for i, question in enumerate(questions):
            submitted = request.form.get(f"q{i}")
            selected = None

            if submitted is not None:
                try:
                    candidate = int(submitted)

                    if 0 <= candidate < len(question["options"]):
                        selected = candidate

                except (ValueError, TypeError):
                    selected = None

            answers[str(i)] = selected

            if selected is None:
                unanswered += 1

            elif selected == question["answer"]:
                correct += 1
                score += question.get("marks", 4)

            else:
                wrong += 1
                score += question.get("negative", -1)

        result_id = secrets.token_hex(12)

        result = {
            "id": result_id,
            "exam": exam.upper(),
            "set_no": set_no,
            "title": paper["title"],
            "score": score,
            "total": len(questions),
            "correct": correct,
            "wrong": wrong,
            "unanswered": unanswered,
            "answers": answers,
            "questions": questions,
            "max_score": sum(
                question.get("marks", 4)
                for question in questions
            ),
            "duration": paper["duration"],
            "submitted_at": time.time()
        }

        saved_result = TestResult(
            result_key=result_id,
            user_id=current_user.id,
            result_json=json.dumps(result, ensure_ascii=False)
        )

        try:
            db.session.add(saved_result)
            db.session.commit()
        except Exception:
            db.session.rollback()
            app.logger.exception("Could not save test result")
            return "Unable to save your result. Please try again.", 500

        session["last_result_id"] = result_id
        session.pop("attempt", None)
        session.modified = True

        return redirect(url_for("test_result"))

    return render_template(
        "mock_test.html",
        exam=exam.upper(),
        set_no=set_no,
        paper=paper,
        questions=questions,
        remaining=remaining,
        expired=(remaining <= 0)
    )


# --------------------------------------------------
# TEST RESULT
# --------------------------------------------------

@app.route("/test-result")
@login_required
def test_result():
    result_id = session.get("last_result_id")

    if not result_id:
        return redirect(url_for("dashboard"))

    saved = TestResult.query.filter_by(
        result_key=result_id,
        user_id=current_user.id
    ).first()

    if not saved:
        session.pop("last_result_id", None)
        return redirect(url_for("dashboard"))

    try:
        result = json.loads(saved.result_json)
    except (json.JSONDecodeError, TypeError):
        app.logger.exception("Saved result is invalid")
        return redirect(url_for("dashboard"))

    return render_template("result.html", result=result)


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.route("/health")
def health():
    return {"status": "ok"}


# --------------------------------------------------
# INITIALISE DATABASE
# --------------------------------------------------

with app.app_context():
    db.create_all()


# --------------------------------------------------
# RUN DEVELOPMENT SERVER
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)