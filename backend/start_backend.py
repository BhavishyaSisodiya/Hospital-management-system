import subprocess, sys, os, time
os.chdir(r"E:\minor project HMS\hms\backend")
env = os.environ.copy()
env["PYTHONPATH"] = r"E:\minor project HMS\hms\backend\venv\Lib\site-packages;E:\minor project HMS\hms\backend"
log = open(r"E:\minor project HMS\hms\backend\uvicorn.log", "w", encoding="utf-8")
p = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
    cwd=r"E:\minor project HMS\hms\backend",
    env=env,
    stdout=log,
    stderr=log,
)
time.sleep(5)
print("running:", p.poll() is None)
log.close()