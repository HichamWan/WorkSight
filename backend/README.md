## 1. How to run it
* install packages:
pip install uvicorn fastapi python-multipart pyjwt bcrypt numpy Pillow
* Start the server:
uvicorn app.main:app --reload --port 8000
* Open the Interactive API docs to test everything: http://localhost:8000/api/docs

## 🧪 2. How to test the Face AI & Multi-Tenancy
To test the flow from start to finish in the browser docs link, follow these steps in order:

   1. Get Token: Go to POST /api/hr/auth/login, submit username "alice" and password "password". Copy the access_token string.
   2. Authorize Page: Click the green Authorize padlock button at the top right of the page, paste your token, and click Authorize.
   3. Create Employee: Go to POST /api/hr/employees and click Execute. The server will create a profile and give you ID 102.
   4. Register Face: Go to POST /api/face/register. Input 102 as the ID, upload a portrait picture file, and click Execute.
   5. Verify Face: Go to POST /api/face/verify, upload the same picture, and hit Execute. The server will recognize you instantly!

Note: All data, passwords, and 128-number face vectors automatically save into a file called database.json in your project folder so you can open it in VS Code and view it directly! 💾
