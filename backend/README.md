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
python uvicorn app.main:app --reload --port 8000
* Open the Interactive API docs to test everything: http://localhost:8000/api/docs
# Terminal 1 — backend
cd d:\WorkSight\backend
python -m uvicorn app.main:app --port 8000

# Terminal 2 — frontend
cd d:\WorkSight\frontend
npm run dev

## 🧪 2. How to test the Face AI & Multi-Tenancy
To test the flow from start to finish in the browser docs link, follow these steps in order:

   1. Get Token: Go to POST /api/hr/auth/login, submit username "alice" and password "password". Copy the access_token string.
   2. Authorize Page: Click the green Authorize padlock button at the top right of the page, paste your token, and click Authorize.
   3. Create Employee: Go to POST /api/hr/employees and click Execute. The server will create a profile and give you ID 102.
   4. Register Face: Go to POST /api/face/register. Input 102 as the ID, upload a portrait picture file, and click Execute.
   5. Verify Face: Go to POST /api/face/verify, upload the same picture, and hit Execute. The server will recognize you instantly!

Note: All data, passwords, and 128-number face vectors automatically save into a file called database.json in your project folder so you can open it in VS Code and view it directly! 💾
