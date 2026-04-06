"""Analytics blueprint — KPI data API and CSV export."""

import csv
import io
from datetime import date, datetime, timedelta, timezone

from flask import Blueprint, Response, jsonify, render_template
from sqlalchemy import func

from models import Patient, TriageHistory, db

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")


@analytics_bp.route("/", methods=["GET"])
def analytics_page():
    """Render the analytics dashboard page."""
    return render_template("analytics.html")


@analytics_bp.route("/data", methods=["GET"])
def analytics_data():
    """Return JSON data for Chart.js charts.

    Response shape:
        {
            daily_counts: [{ date, red, yellow, green }, ...],  # last 7 days
            avg_wait:     [{ date, minutes }, ...],             # last 7 days
            triage_dist:  { red_pct, yellow_pct, green_pct }
        }
    """
    today = date.today()
    daily_counts = []
    avg_wait = []

    for offset in range(6, -1, -1):
        target_date = today - timedelta(days=offset)
        date_str = target_date.strftime("%Y-%m-%d")

        # Count by triage level for this day
        counts = {
            label: db.session.query(func.count(Patient.id))
            .filter(
                func.date(Patient.arrival_time) == target_date,
                Patient.triage_label == label,
            )
            .scalar() or 0
            for label in ("RED", "YELLOW", "GREEN")
        }
        daily_counts.append(
            {
                "date": date_str,
                "red": counts["RED"],
                "yellow": counts["YELLOW"],
                "green": counts["GREEN"],
            }
        )

        # Average wait time (arrival → first history entry) for this day
        patients_today = Patient.query.filter(
            func.date(Patient.arrival_time) == target_date
        ).all()

        wait_minutes = []
        for p in patients_today:
            first_hist = (
                TriageHistory.query.filter_by(patient_id=p.id)
                .order_by(TriageHistory.timestamp.asc())
                .first()
            )
            if first_hist and first_hist.timestamp and p.arrival_time:
                # Ensure both are offset-aware for subtraction
                arr = p.arrival_time
                hist_ts = first_hist.timestamp
                if arr.tzinfo is None:
                    arr = arr.replace(tzinfo=timezone.utc)
                if hist_ts.tzinfo is None:
                    hist_ts = hist_ts.replace(tzinfo=timezone.utc)
                delta = (hist_ts - arr).total_seconds() / 60
                if delta >= 0:
                    wait_minutes.append(delta)

        avg = round(sum(wait_minutes) / len(wait_minutes), 1) if wait_minutes else 0
        avg_wait.append({"date": date_str, "minutes": avg})

    # Overall triage distribution (all records)
    total = db.session.query(func.count(Patient.id)).scalar() or 1
    triage_dist = {
        "red_pct": round(
            (db.session.query(func.count(Patient.id))
             .filter(Patient.triage_label == "RED").scalar() or 0) / total * 100, 1
        ),
        "yellow_pct": round(
            (db.session.query(func.count(Patient.id))
             .filter(Patient.triage_label == "YELLOW").scalar() or 0) / total * 100, 1
        ),
        "green_pct": round(
            (db.session.query(func.count(Patient.id))
             .filter(Patient.triage_label == "GREEN").scalar() or 0) / total * 100, 1
        ),
    }

    return jsonify(
        {"daily_counts": daily_counts, "avg_wait": avg_wait, "triage_dist": triage_dist}
    )


@analytics_bp.route("/export", methods=["GET"])
def export_csv():
    """Stream a CSV download of all patient records."""
    patients = Patient.query.order_by(Patient.arrival_time.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow(
        [
            "Patient ID",
            "Full Name",
            "Age",
            "Pain Level",
            "Resp Rate",
            "Heart Rate",
            "Oxygen Sat",
            "BP Systolic",
            "BP Diastolic",
            "Symptoms",
            "Triage Label",
            "Confidence",
            "Arrival Time",
            "Updated At",
        ]
    )

    for p in patients:
        writer.writerow(
            [
                p.patient_id_display(),
                p.full_name,
                p.age,
                p.pain_level,
                p.resp_rate,
                p.heart_rate,
                p.oxygen_sat,
                p.bp_systolic,
                p.bp_diastolic,
                p.symptoms,
                p.triage_label,
                p.confidence,
                p.arrival_time.isoformat() if p.arrival_time else "",
                p.updated_at.isoformat() if p.updated_at else "",
            ]
        )

    csv_data = output.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=prioritycare_export.csv"
        },
    )
