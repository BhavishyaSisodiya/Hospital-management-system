import json, urllib.request, urllib.error

BASE = "http://127.0.0.1:8000"

def req(path, method="GET", body=None, token=None):
    r = urllib.request.Request(BASE + path, method=method)
    if token:
        r.add_header("Authorization", "Bearer " + token)
    if body is not None:
        r.add_header("Content-Type", "application/json")
        r.data = json.dumps(body).encode()
    try:
        resp = urllib.request.urlopen(r, timeout=10)
        raw = resp.read().decode()
        try:
            return resp.status, json.loads(raw)
        except Exception:
            return resp.status, raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw
    except Exception as e:
        return -1, str(e)

def login(email, pw):
    s, b = req("/auth/login", "POST", {"email": email, "password": pw})
    if s != 200:
        print(f"LOGIN FAIL {email}: {s} {str(b)[:200]}")
        return None
    return b["access_token"]

def main():
    tok = login("admin@hms.com", "Admin@123")
    # list all registered paths from openapi
    s, spec = req("/openapi.json")
    paths = sorted(spec["paths"].keys())
    with open("routes_full.txt", "w") as f:
        for p in paths:
            for m in spec["paths"][p]:
                f.write(f"{m.upper():6} {p}\n")
    print(f"total paths: {len(paths)}")

main()