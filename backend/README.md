Digital Signage Platform — Backend
1. Purpose of This Project

This repository contains the backend of an enterprise-grade, on-premises digital signage platform designed for:

Multi-tenant organizations

Always-on screens

Emergency broadcasts (< 2 seconds)

Long-term maintainability

Security audits

Operational stability

This is not a demo or tutorial project.
It is designed to be run, operated, and audited for years.

2. High-Level Architecture (Backend Scope)

The backend is responsible for:

Tenant management

Admin authentication & RBAC

Device self-registration & approval

Content lifecycle & approval

Scheduling

Emergency broadcast orchestration

Audit logging (mandatory)

Coordination with Redis (realtime only)

The backend does NOT:

Stream media files

Render content

Trust devices

3. Technology Stack (LOCKED)
Runtime

Python 3.12

FastAPI (async)

Data

PostgreSQL (primary system of record)

Redis (realtime coordination only)

Infra

Local machine (current)

Docker (Redis only, for now)

Designed for on-prem / VMware deployment

4. Environment Assumptions (CURRENT SETUP)

These are the current factual constraints and must be respected:

| Component       | Value             |
| --------------- | ----------------- |
| OS              | Windows           |
| Python          | 3.12              |
| Backend         | FastAPI           |
| PostgreSQL DB   | `cms`             |
| PostgreSQL User | `postgres`        |
| Redis           | Running in Docker |
| All services    | Same machine      |

5. Project Structure (CURRENT STATE)

backend/
├─ app/
│  └─ main.py            # Minimal FastAPI app (health check)
│
├─ .env                  # Environment variables (NOT committed)
├─ pyproject.toml        # Dependencies & project metadata
└─ README.md             # This file

⚠️ The full Clean Architecture structure will be created next, but is intentionally not yet implemented


6. Python Environment Setup (MANDATORY)
6.1 Create virtual environment

python -m venv .venv
.venv\Scripts\Activate.ps1

Verify:

python --version

Expected:

Python 3.12.x


6.2 Install dependencies
 //
pip install --upgrade pip
pip install -e .

//

7. Dependencies (pyproject.toml)

The backend uses the following explicit dependencies:

fastapi — API framework

uvicorn — ASGI server

sqlalchemy >= 2.0 — ORM (async)

asyncpg — PostgreSQL async driver

pydantic v2 — data validation

pydantic-settings — environment config

redis >= 5 — Redis async client

python-jose — JWT handling

passlib[bcrypt] — password hashing

python-multipart — file uploads (later)

All dependencies are installed via:

pip install -e .

8. Environment Variables (.env)

File location:

backend/.env

Current .env (WORKING)
###
ENV=dev

DATABASE_URL=postgresql+asyncpg://postgres:root@localhost:5432/cms

REDIS_URL=redis://localhost:6379/0

JWT_SECRET=cms1234567890!
JWT_ALGO=HS256

MEDIA_ROOT=./media
####

Important Rules

.env is never committed

Secrets must be rotated in production

Same format works in Docker & VMware


9. Database Status
PostgreSQL

Database name: cms

User: postgres

Running locally

Async connection tested successfully

Test command:

##

python - <<EOF
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine("postgresql+asyncpg://postgres@localhost:5432/cms")

async def test():
    async with engine.connect():
        print("Postgres OK")

asyncio.run(test())
EOF


##

10. Redis Status

Redis runs in Docker

Port exposed: 6379

Accessible from host

Test:

##

redis-cli -h localhost -p 6379 ping


##

Expected:

PONG

11. FastAPI Status (CURRENT)
Start backend
#
uvicorn app.main:app --reload
#

Health check
#
GET http://127.0.0.1:8000/health
#

Expected:
#
{ "status": "ok" }
#


12. Architectural Principles (NON-NEGOTIABLE)

These rules govern all future code:

Devices are untrusted

Devices are read-only

PostgreSQL is the only source of truth

Redis is ephemeral only

All admin actions are audited

Tenant isolation is explicit

No business logic in API routes

Clean Architecture (domain / use cases / infra)

If any future change violates these → it is wrong.


13. Current Progress Checkpoint
What is DONE

Python environment ready

Dependencies installed

PostgreSQL connected

Redis reachable

.env validated

FastAPI running

What is NOT started yet

Clean Architecture folders

Database models

Auth

Devices

Content

WebSockets

Redis integration

This is intentional.

14. NEXT STEP (EXACT CONTINUATION POINT)

Next step to implement:

Backend bootstrap & architecture foundation

Settings loader

Logging

Dependency injection

DB lifecycle

Redis lifecycle

Clean folder structure

When restarting a new conversation, say:

“We are at STEP: Backend bootstrap & architecture foundation
The environment is ready and validated.”

15. Final Note

This README is your single source of truth for restarting work.

If:

Chat crashes

Machine reboots

You change computer

You ask another AI

You can resume without losing architectural correctness.