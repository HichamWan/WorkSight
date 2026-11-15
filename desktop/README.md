# WorkSight Desktop

WorkSight Desktop is a small PySide6 desktop prototype for an employee check-in/out terminal. The current app provides a login form, a live camera preview, and a record-history table with sample data.

## Features

- **Login screen:** asks for a company name and password and opens the app when both fields are filled in. It does not yet authenticate against a server.
- **Camera screen:** displays a live preview from the first camera device available to OpenCV. It does not yet recognize faces or create attendance events.
- **Record history:** displays a read-only table populated with sample check-in/out rows. The Sync button is a placeholder and does not contact a server.
- **Navigation:** switch between the camera and records screens from the menu after leaving the login screen.

## Requirements

- Python 3 compatible with the listed dependencies
- A camera for the camera-preview screen
- Windows is the primary target; the camera capture currently uses OpenCV's DirectShow backend

Python dependencies are listed in [`requirements.txt`](requirements.txt): PySide6, opencv-python, and requests.

## Setup and run

Run these commands from the `desktop` directory in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

If PowerShell does not allow activating the virtual environment, you can invoke its Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

## Project layout

```text
desktop/
├── api/                 # Placeholder modules for backend API operations
├── assets/
│   ├── icons/            # Reserved for application icons
│   └── styles.qss        # Reserved for Qt styles
├── models/               # Placeholder employee and attendance models
├── tests/                # Placeholder for desktop tests
├── ui/                   # Active login, camera, and records screens
├── utils/                # Placeholder shared utilities
├── views/                # Placeholder view implementation structure
├── workers/              # Placeholder background API and camera workers
├── config.py             # API URL, mock mode, camera index, and timeout settings
├── main.py               # Application entry point and screen navigation
└── requirements.txt      # Python dependencies
```

The `api`, `models`, `utils`, `views`, and `workers` modules are currently empty scaffolding. The running application is implemented in `main.py` and the three screens under `ui/`.

## Configuration and current limitations

[`config.py`](config.py) defines an API base URL, a mock-mode flag, a camera index, and a request timeout. These settings are not yet connected to the active screens: the camera screen currently uses device index `0`, and the API client and backend operations have not been implemented.

There is no persistent local storage or backend integration yet. Login, face recognition, employee registration/deletion, attendance recording, and record synchronization remain future work.
