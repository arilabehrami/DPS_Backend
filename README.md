# DPS Backend

Backend API for the **Digital Personality Simulator (DPS)** built with **FastAPI + SQLAlchemy + PostgreSQL**.

This project includes:
- JWT authentication and role-based authorization
- Workspace-based multi-tenancy isolation
- OTP flows (register verification, password reset, profile password change)
- Background email jobs
- Redis cache (with memory fallback)
- Ollama LLM integration
- Swagger/OpenAPI docs

## 1. Tech Stack

- Python 3.11+ / 3.12
- FastAPI
- SQLAlchemy ORM
- PostgreSQL
- Alembic (migration config present)
- Redis (optional, fallback to in-memory cache)
- Ollama (local LLM)
- Pytest

## 2. Project Structure

- `main.py` - app bootstrap, middleware, router registration
- `routes/` - API endpoints
- `models/` - SQLAlchemy models
- `schemas/` - Pydantic schemas
- `services/` - business logic
- `security/tenant.py` - workspace isolation helpers
- `middleware/` - auth/logging middleware
- `tests/` - unit/API tests

## 3. Local Setup (Windows PowerShell)

### 3.1 Create and activate virtual env

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3.2 Install dependencies

```powershell
pip install -r requirements.txt
```

## 4. Environment Variables

Create/update `.env` in project root:

```env
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/dps_db
SECRET_KEY=change_this_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Multi-tenancy public registration target workspace
PUBLIC_REGISTER_WORKSPACE_ID=1

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:1.5b

# Redis (optional)
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SECONDS=60

# SMTP (background email jobs)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM=your_email@gmail.com
SMTP_TLS=true

# Super admin mail sender policy
SUPER_ADMIN_EMAIL=bahrieveseli1@gmail.com

# OTP config
REGISTER_OTP_EXPIRE_MINUTES=10
REGISTER_OTP_RESEND_SECONDS=60
REGISTER_OTP_MAX_ATTEMPTS=5
RESET_OTP_EXPIRE_MINUTES=10
RESET_OTP_RESEND_SECONDS=60
RESET_OTP_MAX_ATTEMPTS=5
RESET_TOKEN_EXPIRE_MINUTES=10
CHANGE_OTP_EXPIRE_MINUTES=10
CHANGE_OTP_RESEND_SECONDS=60
CHANGE_OTP_MAX_ATTEMPTS=5
```

## 5. Database

Make sure PostgreSQL is running and `dps_db` exists.

Example (psql):

```sql
CREATE DATABASE dps_db;
```

The app currently uses `Base.metadata.create_all(...)` on startup, so tables are created automatically if missing.

## 6. Run Backend

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Backend:
- API root: `http://127.0.0.1:8000/`
- Swagger: `http://127.0.0.1:8000/docs`

## 7. Ollama Commands

### 7.1 Install/start Ollama

Install Ollama from:
- https://ollama.com/download

Start Ollama service (if not auto-started):

```powershell
ollama serve
```

### 7.2 Pull and run model used by this project

```powershell
ollama pull qwen2.5:1.5b
ollama run qwen2.5:1.5b
```

If you want `phi3` instead:

```powershell
ollama pull phi3
ollama run phi3
```

Then update `.env`:

```env
OLLAMA_MODEL=phi3
```

## 8. Redis (Optional)

If Redis is not running, app falls back to memory cache.

Check cache backend in Swagger:
- `GET /cache/status`

Expected:
- `"backend": "redis"` if Redis connected
- `"backend": "memory"` otherwise

## 9. Authentication in Swagger

1. Open `/docs`
2. Click **Authorize**
3. Use OAuth password flow:
   - username: your email
   - password: your password
4. For client fields, leave empty unless required by your Swagger client UI variant.

Token endpoint configured:
- `/auth/token`

## 10. OTP Flows Implemented

### 10.1 Register OTP
- `POST /auth/register/request-otp`
- `POST /auth/register/verify-otp`

### 10.2 Forgot Password OTP
- `POST /auth/forgot-password/request-otp`
- `POST /auth/forgot-password/verify-otp`
- `POST /auth/forgot-password/reset`

### 10.3 Profile Change Password OTP
- `POST /auth/change-password/request-otp`
- `POST /auth/change-password/confirm`

## 11. Email Features

- Send endpoint: `POST /background-jobs/email/send`
- Inbox endpoint: `GET /background-jobs/email/inbox`
- Delete inbox message: `DELETE /background-jobs/email/inbox/{id}`

Policy:
- Only `SUPER_ADMIN_EMAIL` can send emails.
- SMTP sender is system mailbox; `Reply-To` is set to real sender identity.

## 12. Multi-Tenancy Notes

- Tenant key: `workspace_id`
- Resource access is validated against `current_user.workspace_id`
- Public registration does not allow arbitrary workspace assignment from client payload

## 13. Testing

Run all tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Run selected tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\test_auth_security_helpers.py
.\.venv\Scripts\python.exe -m pytest -q tests\test_logging_middleware.py
.\.venv\Scripts\python.exe -m pytest -q tests\test_authentication_middleware.py
.\.venv\Scripts\python.exe -m pytest -q tests\test_cache_service.py
```

## 14. Common Troubleshooting

### 14.1 `Auth Error: Unprocessable Entity` in Swagger
- Use `/auth/token` flow correctly
- Ensure username/password are provided

### 14.2 Redis shows memory backend
- Verify Redis is running
- Verify `REDIS_URL`

### 14.3 Email not sent
- Check SMTP app password
- Check `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`
- Check logs and `event_logs`

### 14.4 OTP not received
- Check spam folder
- Check SMTP configuration
- Respect resend cooldown window

### 14.5 Login fails after password change
- Ensure change-password confirm endpoint returned success
- Logout and login with new password

## 15. Recommended Production Hardening

- Move from `create_all` to strict Alembic migrations workflow
- Use HTTPS in deployment
- Store secrets in vault/environment, not in repo
- Add rate limits globally at gateway/reverse-proxy level
- Add full integration tests for cross-workspace isolation

---

If you want, I can also generate a matching **frontend integration README section** (React API calls + auth flow + OTP screens) ready to paste into your frontend repo.
