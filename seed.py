"""Seed script — populates Priority Care DB with sample data.

Run:  python seed.py
"""

import random
import sys
from datetime import datetime, timedelta, timezone

# Ensure the app package is importable when run from the project root
sys.path.insert(0, ".")

from app import app
from models import Patient, TriageHistory, User, db

# ── Seed configuration ────────────────────────────────────────────────────────

SEED_USER_EMAIL = "nurse@example.com"
SEED_USER_NAME = "Nurse View"
SEED_USER_PASSWORD = "password123"

NUM_PATIENTS = 55

FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
    "William", "Barbara", "David", "Elizabeth", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Aisha", "Priya", "Liam", "Sofia", "Wei",
    "Amara", "Ethan", "Mei", "Carlos", "Fatima", "Lucas", "Zara", "Noah", "Ines",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris",
    "Martin", "Thompson", "Young", "Robinson", "Patel", "Singh", "Kim", "Nguyen",
    "Chen", "Ahmed", "Lopez", "Martinez", "Gonzalez", "Hernandez",
]

SYMPTOMS_BY_TRIAGE = {
    "RED": [
        "Severe chest pain radiating to left arm",
        "Difficulty breathing, oxygen saturation critically low",
        "Uncontrolled bleeding, extreme pain",
        "Loss of consciousness, unresponsive intervals",
        "Severe allergic reaction, throat swelling",
    ],
    "YELLOW": [
        "Moderate abdominal pain, nausea",
        "Persistent headache, mild dizziness",
        "Fever 38.5°C, chills, fatigue",
        "Fracture suspected — right wrist, swelling",
        "Chest tightness with exertion, intermittent",
    ],
    "GREEN": [
        "Minor laceration on forearm, no active bleeding",
        "Mild sore throat and runny nose",
        "Routine medication refill query",
        "Low back pain, chronic, no acute change",
        "Rash on forearm, mild itching",
    ],
}

HISTORY_ACTIONS = [
    "Prediction generated",
    "Vitals updated",
    "Doctor notified",
    "Lab results reviewed",
    "Medication administered",
]


def _random_patient(label: str, days_ago: int) -> Patient:
    """Generate a single randomised patient record with the given triage label."""
    now = datetime.now(timezone.utc) - timedelta(
        days=days_ago,
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )

    # Vitals vary by triage severity
    if label == "RED":
        pain = random.randint(8, 10)
        resp = random.randint(24, 32)
        hr = random.randint(110, 140)
        spo2 = round(random.uniform(88, 94), 1)
        bp_sys = random.randint(150, 200)
        bp_dia = random.randint(90, 120)
    elif label == "YELLOW":
        pain = random.randint(5, 7)
        resp = random.randint(18, 24)
        hr = random.randint(88, 110)
        spo2 = round(random.uniform(95, 97), 1)
        bp_sys = random.randint(130, 155)
        bp_dia = random.randint(80, 95)
    else:
        pain = random.randint(0, 4)
        resp = random.randint(12, 18)
        hr = random.randint(60, 88)
        spo2 = round(random.uniform(97, 100), 1)
        bp_sys = random.randint(110, 130)
        bp_dia = random.randint(60, 80)

    confidence = round(random.uniform(0.75, 0.97), 2)

    return Patient(
        full_name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
        age=random.randint(5, 90),
        pain_level=pain,
        resp_rate=resp,
        heart_rate=hr,
        oxygen_sat=spo2,
        bp_systolic=bp_sys,
        bp_diastolic=bp_dia,
        symptoms=random.choice(SYMPTOMS_BY_TRIAGE[label]),
        triage_label=label,
        confidence=confidence,
        arrival_time=now,
        updated_at=now,
    )


def seed() -> None:
    """Drop existing seed data, re-create tables, and insert fresh records."""
    with app.app_context():
        db.create_all()

        # Seed nurse user (skip if already exists)
        if not User.query.filter_by(email=SEED_USER_EMAIL).first():
            nurse = User(email=SEED_USER_EMAIL, display_name=SEED_USER_NAME)
            nurse.set_password(SEED_USER_PASSWORD)
            db.session.add(nurse)
            db.session.commit()
            print(f"Created user: {SEED_USER_EMAIL}")
        else:
            print(f"User {SEED_USER_EMAIL} already exists — skipping.")

        # Build triage label list: ~20% RED, 40% YELLOW, 40% GREEN
        labels = (
            ["RED"] * 11 + ["YELLOW"] * 22 + ["GREEN"] * 22
        )
        random.shuffle(labels)

        inserted = 0
        for i, label in enumerate(labels):
            days_ago = random.randint(0, 13)  # spread over last 14 days
            patient = _random_patient(label, days_ago)
            db.session.add(patient)
            db.session.flush()  # get patient.id before adding history

            # Add 2–4 history entries per patient
            num_hist = random.randint(2, 4)
            for j in range(num_hist):
                action = HISTORY_ACTIONS[j % len(HISTORY_ACTIONS)]
                offset_min = j * random.randint(5, 30)
                hist = TriageHistory(
                    patient_id=patient.id,
                    timestamp=patient.arrival_time + timedelta(minutes=offset_min),
                    action=action,
                    performed_by=SEED_USER_NAME,
                    result=(
                        f"Triage: {label} (confidence {patient.confidence})"
                        if action == "Prediction generated"
                        else action
                    ),
                )
                db.session.add(hist)

            inserted += 1

        db.session.commit()
        print(f"Seeded {inserted} patients and 1 user.")


if __name__ == "__main__":
    seed()
