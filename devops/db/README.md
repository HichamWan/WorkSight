# WorkSight database

Owner: Orgil O. (Database / DevOps & QA)

## Files
- `init.sql`: the schema plus dev seed data. Runs once, on first container start.
- `models.py`: SQLAlchemy models. Mirrors `init.sql`. If you change one, change the other.
- `../tests/test_schema.py`: constraint tests (16). Each test rolls back, so nothing persists.
- `../tests/verify_models.py`: checks that `init.sql` and `models.py` describe the same database.

## Start the database
```
docker compose up -d
```
Copy `.env.example` to `.env` first and set your passwords.

## IMPORTANT: when you change init.sql
`init.sql` only runs when the data volume is empty. After any schema change:
```
docker compose down -v
docker compose up -d
```
`down -v` deletes the local data volume. Fine for dev, never run it on a real database.

## Run the checks
Install once:
```
pip install sqlalchemy pymysql pytest
```
Constraint tests (use the app user, from `.env`):
```
set DATABASE_URL=mysql+pymysql://worksight_app:worksight_pass@127.0.0.1:3307/worksight
pytest tests/test_schema.py -v
```
Schema comparison (needs a user that can CREATE/DROP databases, so root). It uses
two scratch databases and does not touch `worksight`:
```
python tests/verify_models.py "mysql+pymysql://root:rootpass@127.0.0.1:3307"
```

## Dev seed logins (from the API contract)
| Account | Username | Password | Role | Client |
|---|---|---|---|---|
| Super Admin | admin | password | ADMIN | none |
| HR (ABC Technology) | alice | password | HR | 1 (ABC001) |

Employee 101 (John Smith, EMP001) belongs to client 1. These are dev only, so change
them before anything real touches this database.

## Known gaps (confirm with Hicham)
- Alert types `overtime / under_time / late` are an assumption from the contract examples.
- The contract has no FRONTDESK role, but the requirements diagram has a Front desk actor.
  How the desktop app logs in still needs deciding.
- NFR3: encrypted BLOB vs hashed embedding for `face_embeddings.embedding` is not decided.
- The contract's login is mock (`mock-admin-token`). Real password checking still needs
  to be wired to these `users` rows.
