"""Priority Care Flask application factory and root routes."""

import os
from datetime import date, datetime, timezone

from flask import Flask, redirect, render_template, request, session, url_for
from sqlalchemy import func

from analytics import analytics_bp
from auth import auth_bp
from config import config
from models import Patient, TriageHistory, db
from patients import patients_bp


def create_app(env: str = "default") -> Flask:
    """Create and configure the Flask application.

    Args:
        env: Configuration key — 'development', 'production', or 'default'.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config[env])

    # Initialise extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(analytics_bp)

    # ── Authentication guard ───────────────────────────────────────────────────

    @app.before_request
    def require_login():
        """Redirect unauthenticated users to /login for all protected routes."""
        public_endpoints = {"auth.login_page", "auth.login_post", "static"}
        if request.endpoint in public_endpoints:
            return None
        if not session.get("user_id"):
            return redirect(url_for("auth.login_page"))
        return None

    # ── Root redirect ─────────────────────────────────────────────────────────

    @app.route("/")
    def index():
        """Redirect to dashboard if logged in, otherwise to login."""
        if session.get("user_id"):
            return redirect(url_for("dashboard"))
        return redirect(url_for("auth.login_page"))

    # ── Dashboard ─────────────────────────────────────────────────────────────

    @app.route("/dashboard")
    def dashboard():
        """Render the dashboard with today's KPIs and recent patients."""
        today = date.today()

        # Total patients admitted today
        total_today = (
            db.session.query(func.count(Patient.id))
            .filter(func.date(Patient.arrival_time) == today)
            .scalar() or 0
        )

        # RED-level patients today
        red_count = (
            db.session.query(func.count(Patient.id))
            .filter(
                func.date(Patient.arrival_time) == today,
                Patient.triage_label == "RED",
            )
            .scalar() or 0
        )

        # Average wait time (arrival → first triage history entry), today
        patients_today = Patient.query.filter(
            func.date(Patient.arrival_time) == today
        ).all()

        wait_minutes = []
        for p in patients_today:
            first_hist = (
                TriageHistory.query.filter_by(patient_id=p.id)
                .order_by(TriageHistory.timestamp.asc())
                .first()
            )
            if first_hist and first_hist.timestamp and p.arrival_time:
                arr = p.arrival_time
                hist_ts = first_hist.timestamp
                if arr.tzinfo is None:
                    arr = arr.replace(tzinfo=timezone.utc)
                if hist_ts.tzinfo is None:
                    hist_ts = hist_ts.replace(tzinfo=timezone.utc)
                delta = (hist_ts - arr).total_seconds() / 60
                if delta >= 0:
                    wait_minutes.append(delta)

        avg_wait = (
            round(sum(wait_minutes) / len(wait_minutes), 1) if wait_minutes else 0
        )

        # Last 10 patients (all time)
        recent_patients = (
            Patient.query.order_by(Patient.arrival_time.desc()).limit(10).all()
        )

        return render_template(
            "dashboard.html",
            total_today=total_today,
            red_count=red_count,
            avg_wait=avg_wait,
            recent_patients=recent_patients,
            user_name=session.get("user_name", ""),
        )

    # ── Help page ─────────────────────────────────────────────────────────────

    @app.route("/help")
    def help_page():
        """Render the FAQ and ethics help page."""
        return render_template("help.html")

    # ── Create tables on first run ────────────────────────────────────────────

    with app.app_context():
        db.create_all()
        _auto_seed(app)

    return app


def _auto_seed(app: Flask) -> None:
    """Seed the database on first startup if no users exist."""
    import random
    from datetime import datetime, timedelta, timezone
    from models import Patient, TriageHistory, User
    with app.app_context():
        if User.query.first():
            return
        # Create default nurse user
        nurse = User(email="nurse@example.com", display_name="Nurse View")
        nurse.set_password("password123")
        db.session.add(nurse)
        db.session.commit()
        print("[startup] Default user created: nurse@example.com / password123")


# Allow running directly with `flask run` or `python app.py`
app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    app.run(debug=True)
