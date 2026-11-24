# Munshi — Scaling & Production Architecture

This document describes how Munshi evolves from its current single-school prototype to an enterprise pilot and multi-school deployment.

> **Status Labeling**: Every capability below is explicitly marked as **[BUILT]** (currently in repository) or **[PLANNED]** (architectural roadmap).

---

## 1. Evolution Stages

```
   ┌────────────────────┐     ┌────────────────────┐     ┌────────────────────┐
   │ 1. Prototype       │ ──► │ 2. School Pilot    │ ──► │ 3. Multi-School    │
   │ Single SQLite file │     │ PostgreSQL + Queue │     │ Multi-Tenant SaaS  │
   │ [BUILT]            │     │ [PLANNED]          │     │ [PLANNED]          │
   └────────────────────┘     └────────────────────┘     └────────────────────┘
```

### Stage 1: Prototype (Current Repository) [BUILT]
- Single-school tenancy (`school_id = "S1"`).
- In-memory SQLite with idempotent boot seeding.
- Synchronous pipeline: Extraction &rarr; Span Verification &rarr; RapidFuzz &rarr; Rule Engine R1–R9.
- Frontend Single Page Application served directly by FastAPI.

### Stage 2: School Pilot (Single Institution, 2,000+ Students) [PLANNED]
- Migration to managed PostgreSQL with connection pooling (PgBouncer).
- Persistent audit logs, historical semester trends, and parent confirmation tracking.
- WhatsApp Business API sandbox integration for outbound alert dispatch.
- Redis-backed background worker queue (Celery/RQ) for marksheet OCR and PDF report card generation.

### Stage 3: Multi-School SaaS (District / Cluster Level) [PLANNED]
- Strict multi-tenant data isolation across thousands of schools.
- Dynamic timetable and syllabus configuration per state education board (CBSE, ICSE, State Boards).
- Enterprise SSO integration (Google Workspace for Education, Microsoft Entra ID).

---

## 2. Multi-Tenancy via `school_id`

### Current Implementation [BUILT]
Every table in the Munshi database schema includes a mandatory `school_id` foreign key column:
- `school`, `teacher`, `student`, `class_section`, `timetable_slot`, `syllabus_topic`, `holiday`, `message`, `attendance_record`, `diary_entry`, `homework`, `notification_draft`, `audit_log`.
- All database queries filter by `school_id == current_user.school_id`.

### Planned Multi-Tenant Hardening [PLANNED]
- **PostgreSQL Row-Level Security (RLS)**: Enforce `school_id` isolation at the database engine level via session variables (`SET app.current_school_id = 'S123'`), eliminating the risk of accidental cross-tenant data leakage in application queries.
- **Tenant Subdomains**: Route tenant schools via custom domains or subdomains (`dps-rkp.munshi.ai`, `kv-iit.munshi.ai`).

---

## 3. Stateless API Design & Horizontal Scaling

### Current Implementation [BUILT]
- **Stateless Requests**: The FastAPI application does not store server-side session state.
- **JWT Authentication**: Identity, role, and `school_id` are signed inside self-contained HMAC-SHA256 JWT tokens.
- **Single Process**: Runs in a single Uvicorn process behind a reverse proxy.

### Planned Horizontal Scaling [PLANNED]
- **Stateless Horizontal Replicas**: Multiple container instances can run behind an AWS ALB or Cloudflare Load Balancer. Any replica can handle any request.
- **Distributed In-Memory Cache**: Move the in-memory IP rate limiter (`_message_rate_limits`) and extraction cache to Redis (`redis-py` with sliding window token buckets).

---

## 4. The LLM Abstraction Layer

### Current Implementation [BUILT]
Munshi encapsulates all language model interactions behind a single typed interface (`LLMClient`):
```python
class LLMClient(ABC):
    @abstractmethod
    def extract(self, text: str, today: str, class_hint: Optional[str] = None) -> ExtractionResult: ...
```
- Concrete implementations: `GeminiClient`, `RegexFallback`, `CachedClient`.
- `CompositeExtractionClient` automatically cascades from Gemini to Fallback to Cache on timeout or rate limit, returning `llm_mode` to the caller.
- **Strict Data Boundary**: Student rosters are **never** passed into the LLM prompt. Only the raw message text, date, and class hint are sent.

### Planned LLM Enhancements [PLANNED]
- **Model Agnostic Provider Switching**: Support local on-premise models (Ollama, vLLM, Llama-3-8B-Instruct) for schools requiring strict air-gapped data sovereignty.
- **Prompt Caching**: Enable Google Gemini context caching for system instructions to reduce per-call latency.

---

## 5. Architectural Changes with PostgreSQL & Async Queues

When moving from prototype to high-volume production, the following architectural shifts occur:

| Component | Prototype (Now) [BUILT] | Production Architecture [PLANNED] |
|---|---|---|
| **Database** | SQLite file (`munshi.db`) | Managed PostgreSQL 16 with Read Replicas |
| **Transaction Isolation** | `db.begin_nested()` savepoints | Multi-row atomic commits with row-level locks |
| **Background Tasks** | None (Synchronous response) | Redis + Celery / ARQ worker queue |
| **Marksheet Processing** | Synchronous CSV dataframe validation | Async background processing for 50,000+ row files |
| **Parent Notifications** | Database template drafts only | Async Celery worker dispatching via WhatsApp API |
| **Rate Limiting** | Process in-memory dictionary | Redis sliding-window token bucket |
| **File Storage** | Local static folder | S3 / Cloudflare R2 bucket with signed URLs |
| **Monitoring** | Console stdout logs | OpenTelemetry, Prometheus metrics, Sentry error tracking |
