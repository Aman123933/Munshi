# Munshi — Render Deployment Guide (Free Tier)

This guide documents the exact steps to deploy **Munshi** as a single web service on [Render](https://render.com) using its free tier.

---

## 1. Architecture on Render

Munshi runs as a unified single-service web application:
- **Build**: Compiles the React + Vite frontend into static assets (`frontend/dist`), copies them to `backend/static`, and installs backend Python dependencies.
- **Runtime**: FastAPI / Uvicorn running on Python 3.11+.
- **Routing**:
  - `/api/*` routes to FastAPI routers (auth, messages, records, marks, demo, health).
  - `/` and any client routes (e.g. `/records`, `/marks`) serve the built Single Page Application (`index.html`) with fallback routing.
- **Database**: SQLite (`munshi.db`). On the free tier, the ephemeral disk is cleared on restarts. Munshi automatically initializes tables and seeds the school roster, timetable, teachers, and syllabi on startup in under **0.1 seconds**.

---

## 2. One-Click Blueprint Deployment (`render.yaml`)

The repository includes a `render.yaml` blueprint. If using Render Blueprints:
1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Click **New** &rarr; **Blueprint**.
3. Connect your GitHub repository (`munshi`).
4. Render will detect `render.yaml` and configure the service automatically.
5. Provide your `GEMINI_API_KEY` under the service environment variables.

---

## 3. Manual Dashboard Deployment (Step-by-Step)

If setting up the service manually via the Render UI:

### Step 1: Connect GitHub Repository
1. On the Render Dashboard, click **New** &rarr; **Web Service**.
2. Select **Build and deploy from a Git repository**.
3. Choose your repository: `munshi` (or fork).

### Step 2: Configure Service Settings
Fill in the following fields in the Render dashboard:

| Setting | Value | Description |
|---|---|---|
| **Name** | `munshi` | Service subdomain (e.g., `munshi.onrender.com`) |
| **Region** | *Singapore* or *Frankfurt* | Choose closest to your target audience |
| **Branch** | `main` | Production branch |
| **Root Directory** | *(leave blank)* | Root of repo |
| **Runtime** | `Python` | Python 3.11+ environment |
| **Build Command** | `./build.sh` | Executes frontend build + backend pip install |
| **Start Command** | `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT` | Starts FastAPI on Render's assigned port |
| **Instance Type** | `Free` | Free tier (512 MB RAM, shared CPU) |

### Step 3: Configure Health Check Path
Under **Advanced**:
- **Health Check Path**: `/api/health`
Render uses this endpoint to determine when the application has successfully booted.

### Step 4: Environment Variables
Under the **Environment Variables** section, add the following key-value pairs:

| Key | Example / Value | Secret? | Note |
|---|---|---|---|
| `GEMINI_API_KEY` | `AIzaSy...` | **YES** | Your Google Gemini API key |
| `GEMINI_MODEL` | `gemini-1.5-flash` | No | Target extraction model |
| `JWT_SECRET` | *(click Generate)* | **YES** | Random 32+ char secret for JWT session tokens |
| `LLM_MODE` | `gemini` | No | Set to `gemini` (automatically cascades to fallback if API fails) |
| `PYTHON_VERSION` | `3.11.9` | No | Recommended Python version |

> [!WARNING]
> **Never commit your `GEMINI_API_KEY` or `JWT_SECRET` to git.** Only enter them into the Render Dashboard environment variables.

### Step 5: Deploy
Click **Create Web Service**. 
Render will clone the repo, run `./build.sh`, launch Uvicorn, and monitor `/api/health`.
Once healthy, your live URL will be active (e.g., `https://munshi.onrender.com`).

---

## 4. Free-Tier Behavior & Cold Starts

### Ephemeral Storage & Fast Startup
- On Render's free tier, the local disk is non-persistent and resets whenever the service restarts or sleeps.
- Munshi's startup lifespan executes `seed_database()` during boot. The entire seed (140 students, 14 classes, 8 teachers, timetable, and syllabus topics) completes in **~0.035 seconds**, ensuring boot times under 10 seconds.

### Inactivity Sleep & Frontend Waking Banner
- Free-tier web services spin down after **15 minutes** of inactivity.
- When an idle service receives a request, Render takes **30–50 seconds** to boot the container.
- **Munshi Frontend UX**: If the initial API request takes longer than 1.5 seconds, the frontend automatically displays a persistent top banner:
  > *Waking the server, this can take up to a minute...*
- Once the server responds, the banner automatically dismisses.

### Rate Limiting & Gemini Quota Protection
- Free-tier public demos are protected against automated quota draining:
  - `POST /api/messages` is rate-limited to **20 requests per minute per IP address**.
  - If rate limit is exceeded, HTTP 429 Too Many Requests is returned.
  - If the Gemini API experiences network timeouts or rate limits, the pipeline automatically falls back to deterministic extraction (`RegexFallback`), updates `llm_mode: fallback`, and shows the fallback badge in the UI.

---

## 5. Verifying Deployment with Smoke Tests

Run the automated smoke test script against your live deployment URL:

```bash
python scripts/smoke.py https://munshi.onrender.com
```

Expected output:
```
==========================================
 Running Munshi Smoke Tests against: https://munshi.onrender.com
==========================================

[1/5] Checking API Health (/api/health)...
  --> PASS: Health check 200 OK (status=healthy)

[2/5] Checking Frontend Static Serving (/)...
  --> PASS: Root served index.html (length=1031 bytes)

[3/5] Checking Teacher Login (/api/login)...
  --> PASS: Login successful for Rajesh Sharma (Role: teacher)

[4/5] Checking Message Pipeline Processing (/api/messages)...
  --> PASS: ReviewObject created (ID: a1b2c3d4..., Status: ready, LLM Mode: gemini)
            Extracted fields: 6, Rules evaluated: 9

[5/5] Checking Marks Pre-Flight Checker (/api/marks/demo)...
  --> PASS: Pre-flight check ran on 703 rows, found 28 discrepancy flags
            Ground-truth injected error REC0553 verified in flags

------------------------------------------
 ALL SMOKE TESTS PASSED [OK]
------------------------------------------
```

---

## 6. Rollback & Maintenance

### How to Roll Back a Deployment
1. Go to your service in the Render Dashboard.
2. Click the **Deploys** tab on the left sidebar.
3. Locate the last known good deploy.
4. Click the three dots (`...`) next to that deploy &rarr; **Rollback to this deploy**.

### Manual Re-Deploy
To trigger a fresh build without pushing a commit:
- Click **Manual Deploy** &rarr; **Deploy latest commit** (or **Clear build cache & deploy** if frontend assets need full recompilation).
