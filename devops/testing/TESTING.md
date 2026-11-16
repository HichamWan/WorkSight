# WorkSight — Integration & Testing Architecture
Owner: Orgil O. (DevOps & QA)

## The 3 phases (from the original team plan)

**Phase 1 — Contract** ✅ done
Hicham published `WorkSight_API_Contract.md` and stood up the local FastAPI
backend (`fastapi dev main.py`, docs at `/api/docs`). I rebuilt the Postman
collection directly off that contract — all 40 endpoints, real paths, real
request/response shapes instead of placeholders.

**Phase 2 — Core** ← we're here
Real MySQL container is up (`docker-compose up -d`, schema verified via
`SHOW TABLES`). Backend is live locally. Next: actually run the collection
against `http://localhost:8000/api` and see what passes/fails for real.

**Phase 3 — Connection**
Once CORS is confirmed and the team's ready to test against the shared Fly.io
mock deployment, switch environments (`WorkSight - Local` → `WorkSight - Mock
(Fly.io)`) and re-run everything via Newman for a repeatable pass, not just
click-through in the GUI.

## Postman structure

Mirrors the contract's own section numbering, 40 requests across 12 folders:

```
WorkSight API/
├── Admin Auth                            (§4)
├── Client / Company Management           (§5)
├── Client User / HR Account Management   (§6)
├── HR Auth                               (§7)
├── Employees                             (§8)
├── Attendance                            (§9)
├── Work Hours                            (§10)
├── Dashboard                             (§11)
├── Alerts                                (§12)
├── Face AI                               (§13)
├── Reports                               (§14)
└── System                                (§15 — /health)
```

Two environments now, both holding `API_BASE_URL` + `client_id` /
`employee_id` / `user_id` / `attendance_id` / `admin_token` / `hr_token`:

- **WorkSight - Local** → `http://localhost:8000/api`
- **WorkSight - Mock (Fly.io)** → `https://worksight.today/api`

Running "Login (Super Admin)" or "Login (HR/Manager/Executive)" auto-saves
the returned `access_token` into `{{admin_token}}` / `{{hr_token}}` via a
test script — every other request in that role picks it up automatically
through an `Authorization: Bearer` header.

**Flagged for Hicham:** the contract never explicitly documents the auth
header format for non-login requests. I assumed standard
`Authorization: Bearer <access_token>` — needs confirming against the real
backend.

**Flagged for Orgil N:** `/face/register` and `/face/verify` are built as
`multipart/form-data` (file upload), not base64-in-JSON like my first draft
assumed — `python-multipart` in Hicham's install step confirms that's how
FastAPI is expecting images.

## What I'm actually testing, mapped to the requirements doc

| Requirement | What gets checked |
|---|---|
| FR1–FR5 (website) | Dashboard/reports/alerts endpoints return the shape Noura's Vue app depends on |
| FR6–FR10 (software) | Register/delete employee, face verify, check-in/out all return the right status + payload |
| NFR1 (access control) | Hit an HR-only endpoint as a frontdesk-role token, expect a 403 (not yet automated — need a frontdesk test account first) |
| NFR4 (recognition speed) | `/face/verify` response time stays under the 2–3s target |
| NFR5 (auditability) | Every admin action (add/delete client, employee, manual attendance edit) produces a row in `audit_logs` |

## Still open

- **NFR3** — encrypted BLOB vs. hashed embedding for `face_embeddings.embedding`
  isn't decided yet. Need to raise this with Hicham.
- **Auth header format** — assumed `Bearer` token, not explicitly confirmed
  in the contract. Verify against the running backend.
- **NFR1 test** — need a seeded `frontdesk`-role account to actually test
  the 403 case; contract only shows HR/Manager/Executive roles being created.
- Newman + CI (GitHub Actions) for Phase 3 — not set up yet.
- Haven't actually run the collection against the live local backend yet —
  that's the very next step.

## Database checks (added Week 3)

Schema constraints and ORM/SQL agreement are tested separately from the API:

- `tests/test_schema.py`: 16 tests. Bad data must be rejected with a real MySQL
  constraint error code, valid data must be accepted, and deletes must cascade.
- `tests/verify_models.py`: builds one database from `db/init.sql` and one from
  `db/models.py`, then compares tables, columns, nullability, keys, cascades, and ENUMs.

Both were checked against MariaDB 10.11 in the sandbox, and both were
mutation-tested. Deliberately removing a CHECK constraint or changing an ENUM
makes them fail. Not yet run against the Docker MySQL 8.0 container, which
still needs a real `docker compose up` on the team machine.

API contract coverage: all 40 endpoints in `WorkSight_API_Contract.md` are present
in the Postman collection, with nothing missing and nothing extra.
