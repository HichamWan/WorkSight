import requests
import config

BASE_URL = getattr(config, "API_BASE_URL", "http://localhost:8000/api").rstrip("/")
TIMEOUT = getattr(config, "REQUEST_TIMEOUT", 5)


class ApiError(Exception):
    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


class ApiClient:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self._creds = None      # kept in memory only, used to log in again quietly

    def request(self, method, path, _retry=True, **kwargs):
        headers = dict(kwargs.pop("headers", {}))
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        try:
            r = self.session.request(method, f"{BASE_URL}{path}",
                                     headers=headers, timeout=TIMEOUT, **kwargs)
        except requests.exceptions.ConnectionError:
            raise ApiError("Cannot reach the server")
        except requests.exceptions.Timeout:
            raise ApiError("The server took too long to answer")
        if r.status_code == 401:
            if _retry and self._creds and path != "/hr/auth/login":
                self.login(*self._creds)          # token expired: log in again
                return self.request(method, path, _retry=False, **kwargs)
            raise ApiError("Please log in again", 401)
        if not r.ok:
            try:
                detail = r.json().get("detail", r.text)
            except Exception:
                detail = r.text
            raise ApiError(str(detail), r.status_code)
        return r.json() if r.content else None

    def health(self):
        return self.request("GET", "/health")

    def login(self, username, password):
        try:
            data = self.request("POST", "/hr/auth/login",
                                json={"username": username, "password": password})
        except ApiError as e:
            if e.status in (400, 401, 403):
                raise ApiError("Wrong username or password", e.status)
            raise
        token = None
        if isinstance(data, dict):
            token = data.get("access_token") or data.get("token")
        if not token:
            raise ApiError(f"Logged in, but no token found in: {data}")
        self.token = token
        self._creds = (username, password)
        return data


api = ApiClient()