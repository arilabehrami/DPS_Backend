# Backend Requirements Coverage

This backend uses FastAPI, SQLAlchemy ORM, JWT authentication, role-based authorization, middleware logging, Swagger UI, multi-tenant workspace isolation, caching, background jobs, and an OpenAI-compatible LLM module.

## Runtime

- API framework: FastAPI
- Swagger UI: `/docs`
- ORM: SQLAlchemy
- Authentication: `/auth/register`, `/auth/login`, `/auth/me`
- Authorization: `require_roles(...)`; admin users can manage users/resources, normal users have read/self-scoped access
- Middleware: `LoggingMiddleware`
- Multi-tenancy: `workspace_id` isolation in tenant-aware routes
- Caching: `services/cache.py`, Redis via `REDIS_URL` with memory fallback
- Background jobs: FastAPI `BackgroundTasks`, `routes/background_job.py`
- LLM/OpenAI: `services/llm_service.py`, OpenAI API when `OPENAI_API_KEY` exists, Ollama fallback via `OLLAMA_MODEL=phi3`
- CI/CD: `.github/workflows/backend-ci.yml`

## Useful Commands

```powershell
python seed.py
python -m uvicorn main:app --host 127.0.0.1 --port 8000
pytest -q
```
