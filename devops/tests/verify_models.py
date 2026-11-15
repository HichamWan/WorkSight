"""
Checks that db/models.py (SQLAlchemy) and db/init.sql (MySQL) describe the same database.

Builds one database from init.sql and one from the ORM models, then compares:
tables, columns, nullability, primary keys, foreign keys (incl. ON DELETE), unique
constraints, and ENUM values.

Usage (needs a user allowed to CREATE/DROP databases, e.g. root):
    python tests/verify_models.py "mysql+pymysql://root:rootpass@127.0.0.1:3307"
It creates and drops two scratch databases: worksight_sql and worksight_orm.
It does NOT touch your real worksight database.
"""
import os
import sys

from sqlalchemy import create_engine, inspect, text

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from db.models import Base  # noqa: E402

SERVER = sys.argv[1] if len(sys.argv) > 1 else "mysql+pymysql://root:rootpass@127.0.0.1:3306"
SQL_DB, ORM_DB = "worksight_sql", "worksight_orm"


def admin_engine():
    return create_engine(SERVER + "/", isolation_level="AUTOCOMMIT")


def recreate(db_name):
    with admin_engine().connect() as c:
        c.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
        c.execute(text(f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))


def load_sql(db_name):
    """Run db/init.sql statement by statement through SQLAlchemy (no mysql CLI needed)."""
    sql_file = os.path.join(ROOT, "db", "init.sql")
    with open(sql_file, encoding="utf-8") as f:
        raw = f.read()
    # drop full-line comments, then split on statement-ending semicolons
    body = "\n".join(l for l in raw.splitlines() if not l.strip().startswith("--"))
    statements = [st.strip() for st in body.split(";") if st.strip()]
    eng = create_engine(SERVER + f"/{db_name}")
    with eng.begin() as c:
        for st in statements:
            c.execute(text(st))
    eng.dispose()
    return len(statements)


def describe(db_name):
    eng = create_engine(SERVER + f"/{db_name}")
    insp = inspect(eng)
    out = {}
    for t in sorted(insp.get_table_names()):
        cols = {
            c["name"]: {
                "nullable": c["nullable"],
                "enum": tuple(c["type"].enums) if hasattr(c["type"], "enums") else None,
            }
            for c in insp.get_columns(t)
        }
        pk = tuple(insp.get_pk_constraint(t)["constrained_columns"])
        fks = sorted(
            (tuple(fk["constrained_columns"]), fk["referred_table"],
             tuple(fk["referred_columns"]), (fk.get("options") or {}).get("ondelete"))
            for fk in insp.get_foreign_keys(t)
        )
        uniq = sorted(tuple(u["column_names"]) for u in insp.get_unique_constraints(t))
        # MySQL reports UNIQUE KEYs as indexes; include unique indexes too.
        uniq += sorted(tuple(i["column_names"]) for i in insp.get_indexes(t) if i.get("unique"))
        out[t] = {"cols": cols, "pk": pk, "fks": fks, "uniq": sorted(set(uniq))}
    eng.dispose()
    return out


def main():
    recreate(SQL_DB)
    n = load_sql(SQL_DB)
    print(f"loaded init.sql: {n} statements")

    recreate(ORM_DB)
    eng = create_engine(SERVER + f"/{ORM_DB}")
    Base.metadata.create_all(eng)
    eng.dispose()

    sql, orm = describe(SQL_DB), describe(ORM_DB)
    problems = []

    if set(sql) != set(orm):
        problems.append(f"table sets differ: only in SQL={set(sql)-set(orm)}, only in ORM={set(orm)-set(sql)}")

    for t in sorted(set(sql) & set(orm)):
        s, o = sql[t], orm[t]
        if set(s["cols"]) != set(o["cols"]):
            problems.append(f"{t}: column names differ: SQL-only={set(s['cols'])-set(o['cols'])}, ORM-only={set(o['cols'])-set(s['cols'])}")
        for c in set(s["cols"]) & set(o["cols"]):
            if s["cols"][c]["nullable"] != o["cols"][c]["nullable"]:
                problems.append(f"{t}.{c}: nullable differs (SQL={s['cols'][c]['nullable']}, ORM={o['cols'][c]['nullable']})")
            if s["cols"][c]["enum"] != o["cols"][c]["enum"]:
                problems.append(f"{t}.{c}: ENUM values differ (SQL={s['cols'][c]['enum']}, ORM={o['cols'][c]['enum']})")
        if s["pk"] != o["pk"]:
            problems.append(f"{t}: primary key differs (SQL={s['pk']}, ORM={o['pk']})")
        if s["fks"] != o["fks"]:
            problems.append(f"{t}: foreign keys differ\n    SQL={s['fks']}\n    ORM={o['fks']}")
        if s["uniq"] != o["uniq"]:
            problems.append(f"{t}: unique constraints differ (SQL={s['uniq']}, ORM={o['uniq']})")

    checked = sum(len(v["cols"]) for v in sql.values())
    if problems:
        print(f"FAIL: {len(problems)} mismatch(es) across {len(sql)} tables, {checked} columns")
        for p in problems:
            print(" -", p)
        sys.exit(1)
    print(f"PASS: SQL and ORM agree on {len(sql)} tables, {checked} columns, FKs, uniques, ENUMs")


if __name__ == "__main__":
    main()
