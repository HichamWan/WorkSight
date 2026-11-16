# WorkSight Backend

WorkSight Backend is a FastAPI prototype for the WorkSight HR management system. It exposes admin and HR endpoints for accounts, companies, employees, attendance, leave requests, reports, and experimental face-image matching.

> **Prototype only:** this backend uses a local JSON file and in-memory Python lists, includes seeded demo accounts, and has incomplete persistence and sample-data-backed endpoints. Do not expose it to untrusted networks or use it for production employee data.

## Requirements

- Python compatible with the pinned packages in [`requirements.txt`](requirements.txt)
- Windows PowerShell examples are provided below; the app can also be run with Python and Uvicorn on other platforms

## Install and run

From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

The API listens at `http://127.0.0.1:8000`. Interactive Swagger documentation is available at [http://127.0.0.1:8000/api/docs](http://127.0.0.1:8000/api/docs), and the OpenAPI schema is at `/api/openapi.json`.

To run without activating the environment:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Check that the server is responding:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

Expected response:

```json
{"status":"ok"}
```

## API overview

All endpoints are under `/api`. Most HR operations require an access token in the `Authorization` header, using the `Bearer` scheme. Tokens are JWTs and expire after 60 minutes by default.

| Area | Routes |
|---|---|
| Health | `GET /api/health` |
| Admin sign-in and profile | `POST /api/admin/auth/login`, `POST /api/admin/auth/logout`, `GET /api/admin/auth/me` |
| Company management (admin) | `GET/POST /api/admin/clients`, `GET/PUT/DELETE /api/admin/clients/{client_id}` |
| HR accounts | `POST /api/hr/auth/register`, `POST /api/hr/auth/login`, `POST /api/hr/auth/logout`, `GET /api/hr/auth/me`, `POST /api/hr/auth/change-password` |
| Employees | `GET/POST /api/hr/employees`, `GET/PUT/DELETE /api/hr/employees/{employee_id}` |
| Attendance | `POST /api/hr/attendance/check-in`, `POST /api/hr/attendance/check-out`, `GET /api/hr/attendance` |
| Dashboards and work hours | `GET /api/hr/work-hours`, `GET /api/hr/dashboard/summary`, `GET /api/hr/dashboard/today`, `GET /api/hr/dashboard/analytics` |
| Alerts and activity | `GET /api/hr/alerts` and alert subroutes, `GET /api/hr/activity` |
| Face-image endpoints | `POST /api/face/register?employee_id={id}`, `POST /api/face/verify` |
| Leave requests | `GET/POST /api/hr/leaves`, `POST /api/hr/leaves/{leave_id}/status` |
| Reports | `GET /api/hr/reports/attendance`, `GET /api/hr/reports/work-hours`, `GET /api/hr/reports/export` |

Use `/api/docs` for request fields, response schemas, and authorization while exploring the endpoints.

## First-run demo data

When `database.json` does not exist, the application seeds demo admin and HR accounts, example companies, an employee, attendance, and a leave request. The seeded usernames are `admin` and `alice`; their initial demo password is `password`.

These are public demo credentials, not secure defaults. Use only disposable local data, and change or remove these accounts before any shared deployment. If a database file already exists, its records are loaded instead of seeding fresh demo data.

## Project layout

```text
backend/
├── app/
│   ├── auth/          # Password hashing, JWT helpers, and role dependencies
│   ├── routers/       # Admin and HR/face API endpoints
│   ├── config.py      # JWT signing settings
│   ├── database.py    # JSON-backed in-memory data collections and seed data
│   └── main.py        # FastAPI app, CORS middleware, router registration
├── database.json      # Local persisted data; created/updated by the app
└── requirements.txt   # Pinned Python dependencies
```

## Data and implementation notes

- The application loads its records into process-local Python lists and writes the collections to `database.json` when selected operations call the save helper. This is not a transactional database; some route changes are not currently persisted, and concurrent requests or multiple server workers are not safely coordinated.
- The face endpoints do **not** perform face detection or recognition. The current helper hashes the entire uploaded file and converts those bytes into a deterministic vector, so it only matches identical or sufficiently similar file bytes, not the same person's face across different images.
- Some dashboard, alert, and report responses contain hard-coded example values. Treat them as placeholders, not live HR calculations.
- CORS currently allows all origins, methods, and headers. Restrict it before deploying in a trusted environment.
- `SECRET_KEY` can be provided through the environment, but the code currently has a known fallback value. Set a strong, unique secret outside source control for local testing beyond a disposable demo; production use also requires replacing the prototype storage and reviewing authentication, authorization, and data handling.
