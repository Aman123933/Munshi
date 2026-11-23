# Munshi (मुंशी)

> **AI proposes. Rules verify. The teacher confirms. The model never writes to the database.**

Munshi is an intelligent classroom assistant prototype for Indian schools. A teacher sends one short message (text or voice in English, Hindi, or Hinglish), and Munshi parses and verifies it into attendance records, class diary entries, homework tasks, and parent notification drafts through a deterministic 9-rule verification engine.

---

## Architecture & Monorepo Structure

```text
munshi/
├── backend/            # FastAPI REST API (Python 3.11+)
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py     # FastAPI application & /api/health endpoint
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_health.py # Pytest smoke tests
│   └── requirements.txt
├── frontend/           # Vite + React + Tailwind CSS dashboard
│   ├── src/
│   │   ├── App.jsx     # Health check & dashboard UI
│   │   ├── main.jsx
│   │   └── index.css
│   ├── vite.config.js  # Dev proxy: /api -> http://127.0.0.1:8000
│   ├── tailwind.config.js
│   └── package.json
├── data/               # Seed datasets & benchmark data
│   ├── munshi_indian_school_marks_clean.csv
│   ├── munshi_error_ground_truth.csv
│   └── README.txt
├── eval/               # Evaluation & validation benchmark scripts
│   └── README.md
├── docs/               # Single source of truth specifications
│   └── CONTEXT.md      # Ground-truth design, pipeline, rules & schema
├── .env.example        # Environment variables template
├── .gitignore
└── README.md
```

---

## Quickstart for Teammates

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 1. Environment Setup
Copy the example environment file:
```bash
cp .env.example .env
```

### 2. Backend Setup & Run

In a terminal, navigate to the `backend/` folder:
```bash
cd backend
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
```

Run tests:
```bash
pytest
```

Start the FastAPI backend server (runs on port 8000):
```bash
uvicorn app.main:app --reload --port 8000
```
API Health Check: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

### 3. Frontend Setup & Run

In another terminal, navigate to the `frontend/` folder:
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser. The frontend dev server proxies `/api/*` requests directly to `http://127.0.0.1:8000`.

---

## Documentation
- See [`docs/CONTEXT.md`](docs/CONTEXT.md) for the project specification, 9-step pipeline, R1–R9 rules, database schema, and API contracts.
