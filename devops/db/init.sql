-- WorkSight database schema
-- Owner: Orgil O. (Database / DevOps & QA)
-- Aligned with WorkSight_API_Contract.md (Hicham, Week 2).
-- Runs automatically on first container start via docker-entrypoint-initdb.d.
--
-- Multi-tenancy: a Super Admin (no client) manages Client companies.
-- Each client has its own HR / MANAGER / EXECUTIVE users and employees.
-- Client users may only see rows where client_id matches their own.

SET NAMES utf8mb4;

-- ---------------------------------------------------------------
-- Client companies (contract section 5)
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clients (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    company_name    VARCHAR(100) NOT NULL,
    company_code    VARCHAR(20)  NOT NULL UNIQUE,
    status          ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------
-- Accounts: Super Admin (client_id NULL) and client users (client_id set)
-- Roles match the contract: ADMIN, HR, MANAGER, EXECUTIVE
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    client_id       INT NULL,
    username        VARCHAR(50)  NOT NULL UNIQUE,
    email           VARCHAR(100) NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    role            ENUM('ADMIN', 'HR', 'MANAGER', 'EXECUTIVE') NOT NULL,
    status          ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
    CHECK ((role = 'ADMIN' AND client_id IS NULL) OR (role <> 'ADMIN' AND client_id IS NOT NULL))
);

-- ---------------------------------------------------------------
-- Employees (contract section 8). Always belongs to one client.
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS employees (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    client_id       INT NOT NULL,
    employee_code   VARCHAR(20)  NOT NULL,
    first_name      VARCHAR(50)  NOT NULL,
    last_name       VARCHAR(50)  NOT NULL,
    email           VARCHAR(100),
    phone           VARCHAR(20),
    department      VARCHAR(50),
    position        VARCHAR(50),
    status          ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
    UNIQUE KEY uq_employee_code (client_id, employee_code),
    INDEX idx_employee_client (client_id)
);

-- ---------------------------------------------------------------
-- Face data (Face AI). Kept separate from employees on purpose so biometric
-- data can be encrypted, isolated, or deleted independently.
-- NFR3 (encrypted BLOB vs hashed embedding) is still open with Hicham.
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS face_embeddings (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    employee_id     INT NOT NULL,
    embedding       BLOB NOT NULL,           -- face vector, never a raw photo
    model_version   VARCHAR(30) NOT NULL,    -- which Face-AI model produced it
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------
-- Daily attendance records (contract sections 9, 10, 14).
-- One row per employee per day. Hours are filled in on check-out.
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS attendance_records (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    employee_id     INT NOT NULL,
    record_date     DATE NOT NULL,
    check_in        DATETIME NULL,
    check_out       DATETIME NULL,
    status          ENUM('on_time', 'late', 'absent') NOT NULL DEFAULT 'on_time',
    worked_hours    DECIMAL(5,2) NOT NULL DEFAULT 0,
    overtime_hours  DECIMAL(5,2) NOT NULL DEFAULT 0,
    undertime_hours DECIMAL(5,2) NOT NULL DEFAULT 0,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    UNIQUE KEY uq_employee_day (employee_id, record_date)
);

-- ---------------------------------------------------------------
-- Raw check-in / check-out events (the desktop "Record History" trail).
-- Keeps how each event was verified and how confident the face match was.
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS attendance_logs (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    employee_id       INT NOT NULL,
    check_type        ENUM('in', 'out') NOT NULL,
    verified_by       ENUM('face', 'manual') NOT NULL DEFAULT 'face',
    confidence_score  DECIMAL(5,4) NULL,     -- face match confidence, NULL if manual
    logged_at         DATETIME NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    INDEX idx_employee_time (employee_id, logged_at)
);

-- ---------------------------------------------------------------
-- Alerts (contract section 12): overtime, under-time, late arrival.
-- Alert type values are an assumption until Hicham confirms them.
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS alerts (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    client_id       INT NOT NULL,
    employee_id     INT NOT NULL,
    alert_type      ENUM('overtime', 'under_time', 'late') NOT NULL,
    message         VARCHAR(255) NOT NULL,
    alert_date      DATE NOT NULL,
    value           DECIMAL(5,2) NULL,       -- e.g. hours of overtime
    status          ENUM('active', 'resolved') NOT NULL DEFAULT 'active',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    INDEX idx_alert_client_status (client_id, status)
);

-- ---------------------------------------------------------------
-- Audit trail (NFR5): every admin action that changes data.
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_logs (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NULL,
    client_id       INT NULL,
    action          VARCHAR(50) NOT NULL,    -- e.g. 'employee.create', 'attendance.manual_edit'
    target_table    VARCHAR(50),
    target_id       INT,
    details         JSON,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL
);

-- ---------------------------------------------------------------
-- Dev seed data. Dev-only credentials, matching the contract examples:
--   Super Admin : admin / password
--   HR (ABC)    : alice / password
-- Rotate before anything real or public touches this database.
-- ---------------------------------------------------------------
INSERT INTO clients (id, company_name, company_code)
VALUES (1, 'ABC Technology', 'ABC001')
ON DUPLICATE KEY UPDATE company_name = company_name;

INSERT INTO users (id, client_id, username, email, password_hash, role)
VALUES
    (1, NULL, 'admin', 'admin@worksight.com',
     '$2b$12$nAC44wmxWjt/TAJwl/7wxe1KeMjWRzLUUvXB0n9A6IVEB41p0cIlK', 'ADMIN'),
    (2, 1, 'alice', 'alice@abc.com',
     '$2b$12$ZcWWFN/dYN.8VsbAOP1hpeByI15Z2b9SGpOcxth/3eOOv2D8LMgCa', 'HR')
ON DUPLICATE KEY UPDATE username = username;

INSERT INTO employees (id, client_id, employee_code, first_name, last_name, email, phone, department, position)
VALUES (101, 1, 'EMP001', 'John', 'Smith', 'john@abc.com', '123456789', 'IT', 'Software Engineer')
ON DUPLICATE KEY UPDATE employee_code = employee_code;
