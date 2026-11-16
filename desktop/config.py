# Central settings. Change API_BASE_URL when switching from mock to real backend.
API_BASE_URL = "http://localhost:8000/api"
USE_MOCK = True
CAMERA_INDEX = 0
REQUEST_TIMEOUT = 10  # seconds
COOLDOWN_SECONDS = 180      # cooldown per scan
FULLSCREEN = True           # kiosk mode after login 
MENU_HIDE_SECONDS = 15      # menu hides on the camera page after this much idle time