# WorkSight Desktop Client

The front-desk app of the WorkSight attendance system. It runs on the reception computer, recognizes employees by their face through the webcam, records check-ins and check-outs, and sends them to the WorkSight server.

Built by Team Leviathan. Desktop client: Orgil Naranchuluun. Backend API: Hicham. Web dashboard: Noura.

---

## What it does

- **Login** with a WorkSight HR account (username and password, checked by the server).
- **Check in / out** by looking at the camera. The first scan of the day is a check-in, the next is a check-out, and so on.
- **Register employees** with their details and a short face scan (5 samples while turning the head slightly). New employees are created on the server; employees that already exist on the server only need the face scan.
- **Employee list** loaded from the server, with edit and delete.
- **Record history** with a sync status for every record, and a **Sync now** button.
- **Kiosk mode**: full screen after login, the menu hides when the mouse is idle (F11 or Esc leaves full screen).
- **Camera recovery**: if the camera is unplugged, the app shows a message and reconnects by itself.

## How face recognition works

1. **YuNet** finds the face in each camera frame.
2. **SFace** turns the face into 128 numbers (an embedding).
3. The embedding is compared with the saved samples using cosine similarity. A score of **0.363 or higher** counts as the same person.
4. To avoid mistakes, the same person must match **3 times in a row** before a record is made, and the same person is ignored for a **cooldown** period afterwards.

Face samples are stored **only on the desktop computer**. The server stores employees and attendance, not face data.

## Requirements

- Windows 10 or 11
- A webcam
- Python 3.14 (the version used during development)
- The WorkSight backend running and reachable

## Setup

```powershell
cd desktop
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

The two AI model files (YuNet and SFace, `.onnx`) must be in `desktop/assets/models/`.

## Run

1. Start the backend (in the `backend` folder, with its own virtual environment active):

   ```powershell
   python -m uvicorn app.main:app --reload --port 8000
   ```

   Check that `http://localhost:8000/api/docs` opens. The demo account is `alice` / `password`.

2. Start the desktop app:

   ```powershell
   cd desktop
   python main.py
   ```

## Configuration

Settings are in `desktop/config.py`:

| Setting | Meaning | Default |
|---|---|---|
| `API_BASE_URL` | Address of the server API | `http://localhost:8000/api` |
| `REQUEST_TIMEOUT` | Seconds to wait for the server | `5` |
| `COOLDOWN_SECONDS` | Same person is ignored for this long after a scan | `180` |
| `FULLSCREEN` | Go full screen after login | `True` |
| `MENU_HIDE_SECONDS` | Menu hides on the camera page after this idle time | `15` |

For a quick demo of check-in then check-out, set `COOLDOWN_SECONDS = 10`.

## How to use

1. **Log in** with your username and password.
2. **Register** an employee: enter the code and details, press the button, and look at the camera while slowly turning the head. For an employee who already exists on the server, enter only their code.
3. **Check in/out**: employees stand in front of the camera. The screen shows their name and "Check in" or "Check out".
4. **Records**: shows every scan. Records start as "Not synced" and become "Synced" after **Sync now**. If the server is unreachable, records are kept on the computer and sent next time.
5. **Employees**: edit or delete employees. Deleting removes them from the server and deletes their face data from this computer.

## Project structure

```
desktop/
  main.py                 main window, menu, kiosk behaviour
  config.py               settings
  api/client.py           server client (login, requests, automatic re-login)
  workers/api_worker.py   runs server calls in the background
  utils/
    face_engine.py        detection, embedding, matching
    storage.py            employees and face samples (local JSON)
    records.py            attendance records (local JSON)
    sync.py               sends unsynced records to the server
  ui/                     login, camera, register, employee list, records pages
  assets/
    models/               YuNet and SFace model files
    style.qss             the look of the app
  data/                   created at run time (not in git)
```

## Data and privacy

- `desktop/data/` holds face samples and records. It is listed in `.gitignore` and must never be committed.
- Face samples are 128-number vectors, not photos.
- The login is kept in memory only, to log in again when the server session expires. It is never written to disk.

## Known limitations

- No liveness check: a photo of an employee held to the camera could be accepted. This is planned future work.
- Accuracy was tested with a small number of people. The 0.363 threshold should be re-checked in the real lighting of the deployment.
- Records are sent when someone presses **Sync now**, not automatically.
- A packaged installer is not part of this version; the app is started with Python.
