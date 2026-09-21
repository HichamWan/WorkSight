# WorkSight

AI-powered attendance and workforce management system for tracking employee check-ins, work hours, attendance patterns, and workplace alerts.

> **Status:** In development

## Overview

WorkSight is a decoupled attendance management system built around a **FastAPI backend**, **MySQL database**, **Vue.js management portal**, and **PySide6 desktop client**.

The FastAPI backend acts as the central service connecting the web dashboard, desktop face-scanning client, and database through JSON over HTTP REST APIs.

## Architecture

```text
                         ┌──────────────────────────┐
                         │      Vue.js Portal        │
                         │   HR / Manager Dashboard  │
                         └────────────┬─────────────┘
                                      │ JSON / REST
                                      ▼
┌──────────────────────────┐   ┌──────────────────────────┐
│    PySide6 Desktop App   │──►│     FastAPI Backend      │
│ Webcam / Face Capture    │   │   REST API + AI Logic    │
└──────────────────────────┘   └────────────┬─────────────┘
                                             │
                                             ▼
                                  ┌──────────────────────┐
                                  │    MySQL Database    │
                                  │   Docker Container   │
                                  └──────────────────────┘
```

## Main Features

### Employee Management

* Create and manage employee profiles
* Store employee codes, contact information, department, and position
* Track face-registration status
* Retrieve individual employee information

### Attendance

* Employee check-in and check-out
* Attendance history
* Filtering by date, employee, department, and status
* Late and on-time attendance status
* Worked-hour calculation
* Overtime and under-time calculation

### Dashboard & Analytics

The system provides data for management dashboards, including:

* Total employees
* Present and absent employees
* Late and on-time employees
* Overtime and under-time statistics
* Attendance trends
* Historical attendance data

### Alerts

Attendance-related alerts include:

* Late arrivals
* Overtime
* Under-time

### Face AI

The desktop client communicates with the backend for:

* Employee face registration
* Face verification
* Employee identification from captured images

### Reports

The API provides endpoints for:

* Attendance reports
* Work-hour reports
* CSV export
* XLSX export

## Authentication & Access Control

WorkSight uses a multi-level account structure:

```text
Super Admin
│
├── Client Company
│   ├── HR
│   ├── Manager
│   └── Employees
│
├── Client Company
│   ├── HR
│   └── Employees
│
└── Client Company
    └── HR
```

The Super Admin manages client companies and their accounts.

Client users are restricted to data belonging to their own company through the `client_id` relationship.

The API defines separate authentication flows for:

* Super Admin
* HR
* Manager
* Executive

## API

The backend follows standard REST conventions:

| Method   | Purpose                          |
| -------- | -------------------------------- |
| `GET`    | Read data                        |
| `POST`   | Create data or perform an action |
| `PUT`    | Update existing data             |
| `DELETE` | Delete or deactivate data        |

API responses use JSON unless an endpoint specifically exports CSV/XLSX data.

### Development Base URL

```text
http://localhost:8000/api
```

### Mock API

```text
https://worksight.today/api
```

The frontend and desktop applications should use a configurable `API_BASE_URL` rather than hard-coding the API address.

Example:

```text
API_BASE_URL=http://localhost:8000/api
```

## API Endpoint Groups

```text
/admin/auth/*
/admin/clients/*
/admin/users/*

/hr/auth/*
/hr/employees/*
/hr/attendance/*
/hr/work-hours/*
/hr/dashboard/*
/hr/alerts/*
/hr/reports/*

/face/register
/face/verify

/health
```

### Example

Check in an employee:

```http
POST /api/hr/attendance/check-in
```

Request:

```json
{
  "employee_id": 101,
  "timestamp": "2026-09-17T08:52:00"
}
```

Example response:

```json
{
  "success": true,
  "attendance": {
    "id": 1001,
    "employee_id": 101,
    "date": "2026-09-17",
    "check_in": "2026-09-17T08:52:00",
    "check_out": null,
    "status": "on_time",
    "worked_hours": 0,
    "overtime_hours": 0,
    "undertime_hours": 0
  }
}
```

## Technology Stack

### Backend & AI

* Python
* FastAPI
* REST API
* Face AI / computer vision pipeline

### Database & Infrastructure

* MySQL
* Docker
* Docker Compose

### Frontend

* Vue.js
* JavaScript
* HTML
* CSS

### Desktop Client

* Python
* PySide6
* OpenCV

### Testing & Development

* Postman
* Git
* GitHub
* CORS-enabled API integration

## Development Workflow

### Phase 1 — API Contract & Mocking

The backend provides FastAPI endpoints with mock JSON responses so the frontend and desktop applications can develop against stable API paths independently.

### Phase 2 — Core Development

The system components are developed in parallel:

* FastAPI backend and Face AI logic
* MySQL database
* Vue.js management interface
* PySide6 desktop client

### Phase 3 — Integration

The components are connected through the real API.

CORS is configured on the backend, clients switch from mock data to real endpoints, and Postman is used for integration validation.

## Project Status

WorkSight is currently under active development.

The API contract defines the backend interface required by the Vue.js management portal and PySide6 desktop client. The system is being developed incrementally so that the components can be built and tested independently before final integration.

## Notes

This is a student software engineering project focused on practical backend development, AI integration, REST API architecture, database integration, and full-stack system development.

The API examples in this README are based on the current project API contract and may change as implementation progresses.
