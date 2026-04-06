"""SQLAlchemy models for Priority Care application."""

from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):
    """User account model for nurse/staff login."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    display_name = db.Column(db.Text)

    def set_password(self, password: str) -> None:
        """Hash and store the user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a plaintext password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        """Return string representation of User."""
        return f"<User {self.email}>"


class Patient(db.Model):
    """Patient record model with triage result."""

    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.Text, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    pain_level = db.Column(db.Integer, nullable=False)
    resp_rate = db.Column(db.Integer)
    heart_rate = db.Column(db.Integer)
    oxygen_sat = db.Column(db.Float)
    bp_systolic = db.Column(db.Integer)
    bp_diastolic = db.Column(db.Integer)
    symptoms = db.Column(db.Text)
    triage_label = db.Column(db.Text)        # RED / YELLOW / GREEN
    confidence = db.Column(db.Float)         # Model confidence 0–1
    arrival_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    history = db.relationship(
        "TriageHistory",
        backref="patient",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="TriageHistory.timestamp",
    )

    def patient_id_display(self) -> str:
        """Return formatted display ID like PC-1001."""
        return f"PC-{self.id:04d}"

    def to_dict(self) -> dict:
        """Serialise patient record to a JSON-safe dict."""
        return {
            "id": self.id,
            "patient_id": self.patient_id_display(),
            "full_name": self.full_name,
            "age": self.age,
            "pain_level": self.pain_level,
            "resp_rate": self.resp_rate,
            "heart_rate": self.heart_rate,
            "oxygen_sat": self.oxygen_sat,
            "bp_systolic": self.bp_systolic,
            "bp_diastolic": self.bp_diastolic,
            "symptoms": self.symptoms,
            "triage_label": self.triage_label,
            "confidence": self.confidence,
            "arrival_time": self.arrival_time.isoformat() if self.arrival_time else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        """Return string representation of Patient."""
        return f"<Patient {self.patient_id_display()} {self.full_name}>"


class TriageHistory(db.Model):
    """Audit log of every triage prediction, edit, and notification."""

    __tablename__ = "triage_history"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    action = db.Column(db.Text)          # e.g. "Prediction generated", "Vitals updated"
    performed_by = db.Column(db.Text)    # display_name of the user
    result = db.Column(db.Text)          # JSON string or human-readable summary

    def to_dict(self) -> dict:
        """Serialise history row to dict."""
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "action": self.action,
            "performed_by": self.performed_by,
            "result": self.result,
        }

    def __repr__(self) -> str:
        """Return string representation of TriageHistory."""
        return f"<TriageHistory patient={self.patient_id} action={self.action}>"
