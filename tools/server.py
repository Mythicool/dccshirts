"""Shirt Studio: local web app for rating designs, viewing mockups and generating the next batch.

Start with "Shirt Studio.cmd" (or: uv run --with pillow --with numpy --with scipy tools/server.py).
Listens on 127.0.0.1 only. Votes are saved to feedback.json; jobs run tools/next_batch.py / mockups.py.
"""
import json, mimetypes, subprocess, sys, threading, time, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import taste

ROOT = taste.ROOT
FEEDBACK = ROOT / "feedback.json"
JOB = ROOT / "studio/job.json"
PORT = 8765
STATIC = ("designs/preview/", "designs/print/", "mockups/tpl/", "mockups/out/")
lock = threading.Lock()
proc = {"p": None}


def read_json(p, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return default


def state():
    designs = read_json(ROOT / "designs.json", [])
    notes = read_json(ROOT / "designs/notes.json", {})
    for d in designs:
        d["ready"] = (ROOT / "designs/preview" / f"{d['id']}.png").exists()
        d["notes"] = notes.get(d["id"], [])
    votes = read_json(FEEDBACK, {})
    return {"designs": designs, "votes": votes, "taste": taste.scores(designs, votes),
            "templates": read_json(ROOT / "mockups/tpl/index.json", []), "job": job(), "server": True}


def job():
    j = read_json(JOB, {})
    p = proc["p"]
    j["running"] = bool(p and p.poll() is None)
    if not j["running"] and j.get("state") == "running":
        j["state"] = "done"  # mockup renders don't write job.json themselves
    log = ROOT / "studio/job.log"
    j["tail"] = log.read_text(encoding="utf-8", errors="replace").splitlines()[-12:] if log.exists() else []
    return j


def start(args):
    if proc["p"] and proc["p"].poll() is None:
        return False
    JOB.parent.mkdir(exist_ok=True)
    JOB.write_text(json.dumps({"state": "running", "step": "Starting", "log": []}), encoding="utf-8")
    log = open(ROOT / "studio/job.log", "w", encoding="utf-8")
    proc["p"] = subprocess.Popen([sys.executable, *args], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    return True


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, body, ctype="application/json"):
        b = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if path in ("/", "/index.html"):
            return self.send(200, (ROOT / "tools/studio.html").read_bytes(), "text/html; charset=utf-8")
        if path == "/api/state":
            return self.send(200, state())
        if path == "/api/job":
            return self.send(200, job())
        if path.startswith("/api/plan"):
            n = int(dict(p.split("=") for p in urlparse(self.path).query.split("&") if "=" in p).get("n", 10))
            return self.send(200, taste.plan(n, "auto", seed=1))
        rel = path.lstrip("/")
        f = (ROOT / rel).resolve()
        if rel.startswith(STATIC) and f.is_file() and ROOT in f.parents:
            return self.send(200, f.read_bytes(), mimetypes.guess_type(f.name)[0] or "application/octet-stream")
        self.send(404, {"error": "not found"})

    def do_POST(self):
        if self.headers.get("Origin") not in (None, f"http://127.0.0.1:{PORT}", f"http://localhost:{PORT}"):
            return self.send(403, {"error": "origin"})
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0)) or 0) or b"{}")
        path = urlparse(self.path).path
        if path == "/api/vote":
            with lock:
                fb = read_json(FEEDBACK, {})
                e = fb.setdefault(body["id"], {})
                for k in ("vote", "note", "qa"):
                    if k in body:
                        e[k] = body[k]
                e["ts"] = time.time()
                fb = {k: v for k, v in fb.items() if v.get("vote") or v.get("note") or v.get("qa")}
                FEEDBACK.write_text(json.dumps(fb, indent=1), encoding="utf-8")
                taste.write_report()
            return self.send(200, {"ok": True})
        if path == "/api/generate":
            n, tr = max(1, min(int(body.get("n", 10)), 30)), body.get("track", "auto")
            ok = start(["tools/next_batch.py", "generate", "--n", str(n), "--track", tr])
            return self.send(200 if ok else 409, {"ok": ok})
        if path == "/api/redo":
            return self.send(200, {"ok": start(["tools/next_batch.py", "redo"])})
        if path == "/api/mockups":
            args = ["tools/mockups.py", "render", "--tpl", ",".join(body.get("tpl", ["flatlay", "hanger", "model"])),
                    "--colors", ",".join(body.get("colors", ["Black"]))]
            args += ["--ids", ",".join(body["ids"])] if body.get("ids") else ["--liked"]
            return self.send(200, {"ok": start(args)})
        self.send(404, {"error": "not found"})


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    url = f"http://127.0.0.1:{PORT}/"
    print("Shirt Studio running at", url, "(close this window to stop)")
    if "--no-browser" not in sys.argv:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    srv.serve_forever()
