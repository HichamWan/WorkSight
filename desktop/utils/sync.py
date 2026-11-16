from api.client import api, ApiError


def send_records(pending, id_map):
    """Runs in a background thread. Sends each record to the server.

    pending: list of record dicts (oldest first)
    id_map:  {employee code: server id}
    """
    synced, failed = [], []
    for r in pending:
        server_id = id_map.get(r["employee_id"])
        if server_id is None:
            failed.append((r["id"], f'{r["name"]} is not on the server'))
            continue
        path = ("/hr/attendance/check-in" if r["type"] == "Check in"
                else "/hr/attendance/check-out")
        body = {"employee_id": server_id,
                "timestamp": r["time"].replace(" ", "T")}
        try:
            reply = api.request("POST", path, json=body)
            if isinstance(reply, dict) and reply.get("success") is False:
                raise ApiError(reply.get("message", "The server refused the record"))
            synced.append(r["id"])
        except ApiError as e:
            failed.append((r["id"], str(e)))
            if e.status is None:     # server unreachable: stop, try again later
                break
    return {"synced": synced, "failed": failed, "total": len(pending)}