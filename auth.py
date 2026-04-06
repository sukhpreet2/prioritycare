"""Authentication blueprint — login and logout routes."""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET"])
def login_page() -> str:
    """Render the login page."""
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@auth_bp.route("/login", methods=["POST"])
def login_post():
    """Validate credentials and start a session."""
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        session["user_id"] = user.id
        session["user_name"] = user.display_name or user.email
        return redirect(url_for("dashboard"))

    flash("Invalid email or password. Please try again.")
    return render_template("index.html"), 401


@auth_bp.route("/logout")
def logout():
    """Clear the session and redirect to login."""
    session.clear()
    return redirect(url_for("auth.login_page"))
