import json, re, os, glob, urllib.request

BASE = "http://127.0.0.1:8000"

spec = json.loads(urllib.request.urlopen(BASE + "/openapi.json").read())
backend = {}
for path, item in spec["paths"].items():
    for method in item:
        backend[(method.upper(), path)] = True

FRONT = r"E:\minor project HMS\hms\frontend\src\api"
def norm(p):
    p = re.sub(r'\$\{[^}]*\}', '{P}', p)
    return re.sub(r'\{[^}]*\}', '{P}', p)

backend_norm = {(m, norm(p)) for (m, p) in backend}

front = {}
for f in glob.glob(os.path.join(FRONT, "*.js")):
    src = open(f, encoding="utf-8").read()
    for m in re.finditer(r'api\.(get|post|put|patch|delete)\s*\(\s*([`"\'])(.*?)\2', src, re.S):
        method, path = m.group(1).upper(), m.group(3)
        front.setdefault((method, norm(path)), set()).add(os.path.basename(f))

print("=== FRONTEND CALLS WITHOUT A BACKEND ROUTE ===")
seen = set()
for (method, path), files in sorted(front.items()):
    if (method, path) not in backend_norm:
        key = (method, path)
        if key in seen:
            continue
        seen.add(key)
        print(f"{method:6} {path:40} <- {','.join(sorted(files))}")
print(f"\ntotal distinct: {len(seen)}")