"""
WorkSight SQLAlchemy models (MySQL / MariaDB).

Owner: Orgil O. (Database / DevOps & QA)
Mirrors db/init.sql exactly. If you change one, change the other.
tests/verify_models.py checks that the two still agree.

Usage (from Hicham's FastAPI backend):
    from db.models import Base, Client, User, Employee, ...
    engine = create_engine(DATABASE_URL)
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BLOB, CheckConstraint, DECIMAL, DATE, DATETIME, JSON, TIMESTAMP,
    ForeignKey, Index, Integer, String, UniqueConstraint, func, text,
)
from sqlalchemy.dialects.mysql import ENUM
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# Enum values come from the API contract (WorkSight_API_Contract.md).
ROLE_VALUES = ("ADMIN", "HR", "MANAGER", "EXECUTIVE")
ACCOUNT_STATUS = ("active", "inactive")
ATTENDANCE_STATUS = ("on_time", "late", "absent")
CHECK_TYPE = ("in", "out")
VERIFIED_BY = ("face", "manual")
ALERT_TYPE = ("overtime", "under_time", "late")   # assumption, confirm with Hicham
ALERT_STATUS = ("active", "resolved")


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_name: Mapped[str] = mapped_column(String(100), nullable=False)
    company_code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(ENUM(*ACCOUNT_STATUS), nullable=False, server_default="active")
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    users: Mapped[list["User"]] = relationship(back_populates="client", cascade="all, delete-orphan")
    employees: Mapped[list["Employee"]] = relationship(back_populates="client", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "(role = 'ADMIN' AND client_id IS NULL) OR (role <> 'ADMIN' AND client_id IS NOT NULL)",
            name="ck_user_role_client",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    client_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"), nullable=True
    )
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(ENUM(*ROLE_VALUES), nullable=False)
    status: Mapped[str] = mapped_column(ENUM(*ACCOUNT_STATUS), nullable=False, server_default="active")
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    client: Mapped[Optional["Client"]] = relationship(back_populates="users")


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (
        UniqueConstraint("client_id", "employee_code", name="uq_employee_code"),
        Index("idx_employee_client", "client_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    employee_code: Mapped[str] = mapped_column(String(20), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(100))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    department: Mapped[Optional[str]] = mapped_column(String(50))
    position: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(ENUM(*ACCOUNT_STATUS), nullable=False, server_default="active")
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    client: Mapped["Client"] = relationship(back_populates="employees")
    face_embeddings: Mapped[list["FaceEmbedding"]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )
    attendance_records: Mapped[list["AttendanceRecord"]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )
    attendance_logs: Mapped[list["AttendanceLog"]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )


class FaceEmbedding(Base):
    """Biometric data. Kept apart from employees on purpose (NFR3 still open)."""
    __tablename__ = "face_embeddings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    embedding: Mapped[bytes] = mapped_column(BLOB, nullable=False)
    model_version: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, server_default=func.now())

    employee: Mapped["Employee"] = relationship(back_populates="face_embeddings")


class AttendanceRecord(Base):
    """One row per employee per day (contract sections 9, 10, 14)."""
    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint("employee_id", "record_date", name="uq_employee_day"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    record_date: Mapped[date] = mapped_column(DATE, nullable=False)
    check_in: Mapped[Optional[datetime]] = mapped_column(DATETIME)
    check_out: Mapped[Optional[datetime]] = mapped_column(DATETIME)
    status: Mapped[str] = mapped_column(ENUM(*ATTENDANCE_STATUS), nullable=False, server_default="on_time")
    worked_hours: Mapped[Decimal] = mapped_column(DECIMAL(5, 2), nullable=False, server_default="0")
    overtime_hours: Mapped[Decimal] = mapped_column(DECIMAL(5, 2), nullable=False, server_default="0")
    undertime_hours: Mapped[Decimal] = mapped_column(DECIMAL(5, 2), nullable=False, server_default="0")

    employee: Mapped["Employee"] = relationship(back_populates="attendance_records")


class AttendanceLog(Base):
    """Raw check-in / check-out events. Feeds the desktop 'Record History' view."""
    __tablename__ = "attendance_logs"
    __table_args__ = (
        Index("idx_employee_time", "employee_id", "logged_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    check_type: Mapped[str] = mapped_column(ENUM(*CHECK_TYPE), nullable=False)
    verified_by: Mapped[str] = mapped_column(ENUM(*VERIFIED_BY), nullable=False, server_default="face")
    confidence_score: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 4))
    logged_at: Mapped[datetime] = mapped_column(DATETIME, nullable=False)

    employee: Mapped["Employee"] = relationship(back_populates="attendance_logs")


class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (
        Index("idx_alert_client_status", "client_id", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    alert_type: Mapped[str] = mapped_column(ENUM(*ALERT_TYPE), nullable=False)
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    alert_date: Mapped[date] = mapped_column(DATE, nullable=False)
    value: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 2))
    status: Mapped[str] = mapped_column(ENUM(*ALERT_STATUS), nullable=False, server_default="active")
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, server_default=func.now())


class AuditLog(Base):
    """Every admin action that changes data (NFR5)."""
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    client_id: Mapped[Optional[int]] = mapped_column(ForeignKey("clients.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    target_table: Mapped[Optional[str]] = mapped_column(String(50))
    target_id: Mapped[Optional[int]] = mapped_column(Integer)
    details: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, server_default=func.now())
