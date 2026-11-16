"""
Schema constraint tests for WorkSight.

Run against any MySQL/MariaDB that has db/init.sql loaded:
    set DATABASE_URL=mysql+pymysql://worksight_app:worksight_pass@127.0.0.1:3307/worksight
    pytest tests/test_schema.py -v

Every test runs inside a transaction that is rolled back, so nothing persists.
The seed data (admin, client 1 ABC001, HR user alice, employee 101) must be present.
"""
import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError

# MySQL/MariaDB error codes that mean "the schema rejected this row".
CONSTRAINT_CODES = {
    1048,  # column cannot be null
    1062,  # duplicate key (unique constraint)
    1264,  # out of range value
    1265,  # data truncated / value not in ENUM
    1364,  # field has no default value
    1452,  # foreign key: parent row missing
    1466,  # foreign key: cannot delete parent
    3819,  # check constraint (MariaDB)
    4025,  # check constraint (MySQL 8 / MariaDB CONSTRAINT)
}

URL = os.environ.get("DATABASE_URL", "mysql+pymysql://worksight_app:worksight_pass@127.0.0.1:3307/worksight")
engine = create_engine(URL)



@pytest.fixture
def conn():
    c = engine.connect()
    tx = c.begin()
    yield c
    tx.rollback()
    c.close()


def insert(conn, sql, **params):
    conn.execute(text(sql), params)


def assert_rejected_by_schema(conn, sql):
    """Passes only if the DB rejects the row with a known constraint error code."""
    try:
        conn.execute(text(sql), {})
    except DBAPIError as ex:
        code = ex.orig.args[0]
        assert code in CONSTRAINT_CODES, f"rejected, but with unexpected error {code}: {ex.orig}"
        return
    raise AssertionError("schema ACCEPTED bad data (no constraint error)")


# ---- rules that must REJECT bad data ----
@pytest.mark.parametrize("name,sql", [
    ("ADMIN with a client_id",
     "INSERT INTO users (client_id,username,email,password_hash,role) VALUES (1,'t_admin','t@x','h','ADMIN')"),
    ("HR with no client_id",
     "INSERT INTO users (client_id,username,email,password_hash,role) VALUES (NULL,'t_hr','t@x','h','HR')"),
    ("role outside contract (FRONTDESK)",
     "INSERT INTO users (client_id,username,email,password_hash,role) VALUES (1,'t_fd','t@x','h','FRONTDESK')"),
    ("duplicate employee_code in same client",
     "INSERT INTO employees (client_id,employee_code,first_name,last_name) VALUES (1,'EMP001','Dup','Person')"),
    ("employee pointing at missing client",
     "INSERT INTO employees (client_id,employee_code,first_name,last_name) VALUES (999,'X1','No','Client')"),
    ("attendance status outside on_time/late/absent",
     "INSERT INTO attendance_records (employee_id,record_date,status) VALUES (101,'2026-09-17','weird')"),
    ("second attendance row for same employee and day",
     "INSERT INTO attendance_records (employee_id,record_date) VALUES (101,'2026-09-17')"),
    ("face embedding for missing employee",
     "INSERT INTO face_embeddings (employee_id,embedding,model_version) VALUES (999,X'0102','m1')"),
])
def test_rejects(conn, name, sql):
    if "second attendance row" in name:
        # the duplicate only makes sense if the first row exists
        insert(conn, "INSERT INTO attendance_records (employee_id,record_date) VALUES (101,'2026-09-17')")
    assert_rejected_by_schema(conn, sql)


# ---- valid data must be ACCEPTED ----
@pytest.mark.parametrize("name,sql", [
    ("HR user under a client",
     "INSERT INTO users (client_id,username,email,password_hash,role) VALUES (1,'t_ok','t@x','h','MANAGER')"),
    ("second employee code in same client",
     "INSERT INTO employees (client_id,employee_code,first_name,last_name) VALUES (1,'EMP777','Ok','Person')"),
    ("attendance record with hours",
     "INSERT INTO attendance_records (employee_id,record_date,check_in,check_out,status,worked_hours,overtime_hours) "
     "VALUES (101,'2026-09-19','2026-09-19 08:52:00','2026-09-19 18:10:00','on_time',9.3,1.3)"),
    ("face embedding for real employee",
     "INSERT INTO face_embeddings (employee_id,embedding,model_version) VALUES (101,X'0102','arcface-v1')"),
    ("overtime alert",
     "INSERT INTO alerts (client_id,employee_id,alert_type,message,alert_date,value) "
     "VALUES (1,101,'overtime','Employee worked overtime','2026-09-19',1.3)"),
    ("audit log row",
     "INSERT INTO audit_logs (user_id,client_id,action,target_table,target_id,details) "
     "VALUES (1,NULL,'employee.create','employees',101,JSON_OBJECT('note','test'))"),
])
def test_accepts(conn, name, sql):
    insert(conn, sql)


# ---- cascades ----
def test_deleting_employee_cascades(conn):
    insert(conn, "INSERT INTO face_embeddings (employee_id,embedding,model_version) VALUES (101,X'0102','m1')")
    insert(conn, "INSERT INTO attendance_records (employee_id,record_date) VALUES (101,'2026-09-20')")
    insert(conn, "INSERT INTO alerts (client_id,employee_id,alert_type,message,alert_date) "
                 "VALUES (1,101,'late','Late arrival','2026-09-20')")
    insert(conn, "DELETE FROM employees WHERE id=101")
    left = conn.execute(text(
        "SELECT (SELECT COUNT(*) FROM face_embeddings WHERE employee_id=101)"
        "+(SELECT COUNT(*) FROM attendance_records WHERE employee_id=101)"
        "+(SELECT COUNT(*) FROM alerts WHERE employee_id=101)")).scalar()
    assert left == 0


def test_deleting_client_keeps_super_admin(conn):
    insert(conn, "DELETE FROM clients WHERE id=1")
    admins = conn.execute(text("SELECT COUNT(*) FROM users WHERE role='ADMIN'")).scalar()
    others = conn.execute(text("SELECT COUNT(*) FROM users WHERE role<>'ADMIN'")).scalar()
    assert admins == 1
    assert others == 0
