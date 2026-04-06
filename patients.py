"""Patients blueprint — CRUD routes and triage prediction endpoint."""

import json
from datetime import datetime, timezone

from flask import (
    Blueprint,
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from ml.predict import predict
from models import Patient, TriageHistory, db

patients_bp = Blueprint("patients", __name__, url_prefix="/patients")


def _current_user_name() -> str:
    """Return the logged-in user's display name."""
    return session.get("user_name", "Staff")


@patients_bp.route("/", methods=["GET"])
def patient_list():
    """Render the patient list with optional search and triage filter."""
    query = Patient.query

    search_term = request.args.get("q", "").strip()
    triage_filter = request.args.get("triage", "").strip().upper()

    if search_term:
        # Case-insensitive name search
        query = query.filter(Patient.full_name.ilike(f"%{search_term}%"))

    if triage_filter in ("RED", "YELLOW", "GREEN"):
        query = query.filter(Patient.triage_label == triage_filter)

    patients = query.order_by(Patient.arrival_time.desc()).all()
    return render_template(
        "patients.html",
        patients=patients,
        search_term=search_term,
        triage_filter=triage_filter,
    )


@patients_bp.route("/new", methods=["GET"])
def new_patient_form():
    """Render the new-patient intake form."""
    return render_template("new-patient.html")


@patients_bp.route("/predict", methods=["POST"])
def predict_triage():
    """Run the ML triage prediction and return JSON result.

    Expects JSON body with patient vitals; returns label, confidence,
    suggested_action, and top_factors.
    """
    try:
        data = request.get_json(force=True) or {}
        result = predict(data)
        return jsonify(result), 200
    except Exception as exc:
        return jsonify({"error": "Prediction failed", "detail": str(exc), "code": 500}), 500


@patients_bp.route("/", methods=["POST"])
def create_patient():
    """Save a new patient and their triage result; redirect to detail page."""
    form = request.form

    try:
        patient = Patient(
            full_name=form.get("full_name", "").strip(),
            age=int(form.get("age", 0)),
            pain_level=int(form.get("pain_level", 0)),
            resp_rate=_int_or_none(form.get("resp_rate")),
            heart_rate=_int_or_none(form.get("heart_rate")),
            oxygen_sat=_float_or_none(form.get("oxygen_sat")),
            bp_systolic=_int_or_none(form.get("bp_systolic")),
            bp_diastolic=_int_or_none(form.get("bp_diastolic")),
            symptoms=form.get("symptoms", "").strip(),
            triage_label=form.get("triage_label", "GREEN").upper(),
            confidence=_float_or_none(form.get("confidence")),
            arrival_time=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.session.add(patient)
        db.session.flush()  # Get the ID before committing

        history = TriageHistory(
            patient_id=patient.id,
            timestamp=datetime.now(timezone.utc),
            action="Prediction generated",
            performed_by=_current_user_name(),
            result=f"Triage: {patient.triage_label} (confidence {patient.confidence})",
        )
        db.session.add(history)
        db.session.commit()

        return redirect(url_for("patients.patient_detail", patient_id=patient.id))

    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Could not save patient", "detail": str(exc)}), 500


@patients_bp.route("/<int:patient_id>", methods=["GET"])
def patient_detail(patient_id: int):
    """Render the patient detail page with full triage history."""
    patient = Patient.query.get_or_404(patient_id)
    history = (
        TriageHistory.query.filter_by(patient_id=patient_id)
        .order_by(TriageHistory.timestamp.desc())
        .all()
    )
    return render_template("patient-detail.html", patient=patient, history=history)


@patients_bp.route("/<int:patient_id>/edit", methods=["GET"])
def edit_patient_form(patient_id: int):
    """Render the edit form pre-filled with the patient's current data."""
    patient = Patient.query.get_or_404(patient_id)
    return render_template("edit-patient.html", patient=patient)


@patients_bp.route("/<int:patient_id>", methods=["PUT"])
def update_patient(patient_id: int):
    """Update a patient's record and append a history row; return JSON."""
    patient = Patient.query.get_or_404(patient_id)
    try:
        data = request.get_json(force=True) or {}

        # Update only provided fields
        if "full_name" in data:
            patient.full_name = str(data["full_name"]).strip()
        if "age" in data:
            patient.age = int(data["age"])
        if "pain_level" in data:
            patient.pain_level = int(data["pain_level"])
        if "resp_rate" in data:
            patient.resp_rate = _int_or_none(data["resp_rate"])
        if "heart_rate" in data:
            patient.heart_rate = _int_or_none(data["heart_rate"])
        if "oxygen_sat" in data:
            patient.oxygen_sat = _float_or_none(data["oxygen_sat"])
        if "bp_systolic" in data:
            patient.bp_systolic = _int_or_none(data["bp_systolic"])
        if "bp_diastolic" in data:
            patient.bp_diastolic = _int_or_none(data["bp_diastolic"])
        if "symptoms" in data:
            patient.symptoms = str(data["symptoms"]).strip()

        patient.updated_at = datetime.now(timezone.utc)

        history = TriageHistory(
            patient_id=patient.id,
            timestamp=datetime.now(timezone.utc),
            action="Vitals updated",
            performed_by=_current_user_name(),
            result=json.dumps({k: data[k] for k in data if k != "symptoms"}),
        )
        db.session.add(history)
        db.session.commit()

        return jsonify(patient.to_dict()), 200

    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Update failed", "detail": str(exc)}), 500


@patients_bp.route("/<int:patient_id>", methods=["DELETE"])
def delete_patient(patient_id: int):
    """Delete a patient and all associated history rows; return JSON."""
    patient = Patient.query.get_or_404(patient_id)
    try:
        # Cascade delete handles history rows via relationship
        db.session.delete(patient)
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Delete failed", "detail": str(exc)}), 500


# ── Private helpers ────────────────────────────────────────────────────────────

def _int_or_none(value) -> int | None:
    """Convert value to int, returning None if blank or unconvertible."""
    try:
        return int(value) if value not in (None, "", "null") else None
    except (ValueError, TypeError):
        return None


def _float_or_none(value) -> float | None:
    """Convert value to float, returning None if blank or unconvertible."""
    try:
        return float(value) if value not in (None, "", "null") else None
    except (ValueError, TypeError):
        return None
