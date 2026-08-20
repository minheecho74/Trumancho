#!/usr/bin/env python3
"""Local-only editor for the TrumanSite Timeline. Not exposed publicly --
run this on your own Mac (python3 admin_server.py) and open
http://localhost:3459 in a browser. Never deploy this file or route it
through Cloudflare.

Save writes to _data/timeline_curated.json and regenerates the HTML.
Publish additionally commits, pushes to GitHub, and deploys to Cloudflare.
"""
import json, os, subprocess, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "_data")
IMG = os.path.join(ROOT, "assets/img")
PORT = 3459


def load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


def save(name, obj):
    with open(os.path.join(DATA, name), "w") as f:
        json.dump(obj, f, indent=1)


def run(cmd, cwd=ROOT, env=None):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    return result.returncode, result.stdout + result.stderr


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # keep terminal quiet

    def _json(self, obj, status=200):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path, content_type):
        if not os.path.exists(path):
            self.send_response(404)
            self.end_headers()
            return
        with open(path, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self._file(os.path.join(ROOT, "admin.html"), "text/html")
            return

        if path == "/api/timeline/pool":
            timeline = load("timeline_images.json")
            years = load("timeline_years.json")
            path_map = load("url_to_path.json")
            pool = []
            for i, t in enumerate(timeline):
                year, sourced = years.get(str(i), [None, False])
                pool.append({
                    "index": i,
                    "caption": t.get("caption", ""),
                    "year": year,
                    "sourced": sourced,
                    "img": "/img/" + path_map.get(t["src"], ""),
                })
            self._json(pool)
            return

        if path == "/api/timeline/curated":
            self._json(load("timeline_curated.json"))
            return

        if path.startswith("/img/"):
            rel = path[len("/img/"):]
            full = os.path.join(IMG, rel)
            ext = os.path.splitext(full)[1].lower()
            ctype = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
                     ".gif": "image/gif"}.get(ext, "application/octet-stream")
            self._file(full, ctype)
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        if path == "/api/timeline/curated":
            save("timeline_curated.json", payload)
            code, out = run([sys.executable, "build_site.py"])
            self._json({"ok": code == 0, "log": out})
            return

        if path == "/api/build":
            code, out = run([sys.executable, "build_site.py"])
            self._json({"ok": code == 0, "log": out})
            return

        if path == "/api/publish":
            log = []
            code, out = run([sys.executable, "build_site.py"])
            log.append(out)
            if code != 0:
                self._json({"ok": False, "log": "\n".join(log)})
                return

            code, out = run(["git", "add", "-A"])
            log.append(out)

            code, out = run(["git", "commit", "-m", "Edit via local admin tool"])
            log.append(out)
            # commit returns non-zero if nothing changed -- not fatal

            code, out = run(["git", "push", "origin", "main"])
            log.append(out)
            if code != 0:
                self._json({"ok": False, "log": "\n".join(log)})
                return

            env_path = os.path.join(ROOT, ".env")
            env = os.environ.copy()
            if os.path.exists(env_path):
                for line in open(env_path):
                    line = line.strip()
                    if line.startswith("export "):
                        line = line[len("export "):]
                    if "=" in line:
                        k, v = line.split("=", 1)
                        env[k] = v.strip('"')
            code, out = run(["npx", "wrangler", "deploy"], env=env)
            log.append(out)
            self._json({"ok": code == 0, "log": "\n".join(log)})
            return

        self.send_response(404)
        self.end_headers()


if __name__ == "__main__":
    print(f"Admin tool running at http://localhost:{PORT}  (local only, Ctrl+C to stop)")
    HTTPServer(("localhost", PORT), Handler).serve_forever()
