# Priority Care — Phase 4 Back End

Emergency Triage Support web application built with Flask + SQLite.

---

## Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Seed the database (creates 55 sample patients + 1 user)
python seed.py

# 4. Run the development server
flask run
```

The app runs at **http://localhost:5000**

---

## Login Credentials

| Field    | Value                  |
|----------|------------------------|
| Email    | nurse@example.com      |
| Password | password123            |

---

## Project Structure

```
prioritycare/
├── app.py              # Flask app factory + dashboard route
├── auth.py             # Login / logout blueprint
├── patients.py         # Patient CRUD + ML predict blueprint
├── analytics.py        # Analytics data API + CSV export
├── models.py           # SQLAlchemy models (Patient, TriageHistory, User)
├── config.py           # Dev / prod configuration
├── seed.py             # Database seeder
├── requirements.txt
├── Procfile            # gunicorn for Render.com
├── ml/
│   ├── predict.py      # ML model loader + rule-based fallback
│   └── triage_model.pkl  # (add your DATA-440 trained model here)
├── templates/          # Jinja2 HTML pages (from Phase 3)
└── static/             # CSS, JS, images (unchanged from Phase 3)
```

---

## ML Model

Place your trained scikit-learn model at `ml/triage_model.pkl`.

If the file is absent, the app uses a **rule-based fallback**:
- **RED** — pain ≥ 8 OR resp_rate ≥ 25 OR oxygen_sat ≤ 94
- **YELLOW** — pain ≥ 5 OR resp_rate ≥ 20
- **GREEN** — everything else

---

## Environment Variables

| Variable       | Default                    | Purpose                     |
|----------------|----------------------------|-----------------------------|
| `SECRET_KEY`   | random (dev only)          | Flask session signing key   |
| `DATABASE_URL` | `sqlite:///prioritycare.db`| Database connection string  |
| `FLASK_ENV`    | `development`              | `production` disables DEBUG |

Create a `.env` file (never commit it):

```
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

---

## Deployment (Render.com)

1. Push repository to GitHub.
2. Create a new **Web Service** on Render pointing to your repo.
3. Set environment variables: `SECRET_KEY`, `FLASK_ENV=production`.
4. Build command: `pip install -r requirements.txt && python seed.py`
5. Start command: `gunicorn app:app`

---

## Team

TriageAI Developers — Priority Care Phase 4, April 2026
