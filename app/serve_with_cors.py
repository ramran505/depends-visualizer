#!/usr/bin/env python3
import http.server
import socketserver
import os
import sys
import subprocess
import signal
import time
import shutil

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
INPUT_DIR = sys.argv[2] if len(sys.argv) > 2 else "."

# Always resolve to absolute path
DIRECTORY = os.path.abspath(INPUT_DIR)

# === Brute-force kill existing port processes ===
def brute_force_kill_port(port: int):
    killed = False
    print(f"🔎 Checking for existing process on port {port}...")

    # Try lsof
    if shutil.which("lsof"):
        try:
            result = subprocess.run(["lsof", "-ti", f":{port}"], capture_output=True, text=True)
            pids = result.stdout.strip().splitlines()
            for pid in pids:
                print(f"🔪 Killing PID {pid} (lsof)")
                os.kill(int(pid), signal.SIGKILL)
                killed = True
        except Exception as e:
            print(f"⚠️ lsof error: {e}")

    # Try fuser
    if not killed and shutil.which("fuser"):
        try:
            subprocess.run(["fuser", "-k", f"{port}/tcp"], check=True)
            print(f"🔪 Killed process on port {port} (fuser)")
            killed = True
        except Exception as e:
            print(f"⚠️ fuser error: {e}")

    # Try netstat + lsof fallback
    if not killed and shutil.which("netstat"):
        try:
            result = subprocess.run(f"netstat -tuln | grep :{port}", shell=True, capture_output=True, text=True)
            if result.stdout.strip():
                pids = subprocess.check_output(
                    f"lsof -ti tcp:{port}",
                    shell=True,
                    text=True
                ).strip().splitlines()
                for pid in pids:
                    print(f"🔪 Killing PID {pid} (netstat/lsof)")
                    os.kill(int(pid), signal.SIGKILL)
                killed = True
        except Exception as e:
            print(f"⚠️ netstat fallback error: {e}")

    if killed:
        time.sleep(1)  # Let OS release the port
        print(f"✅ Port {port} cleared")
    else:
        print(f"⚠️ No process found using port {port}")

brute_force_kill_port(PORT)

# === Reusable TCP Server ===
class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

# === CORS-enabled File Server ===
class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        return super().end_headers()

    def translate_path(self, path):
        rel_path = path.lstrip("/")
        return os.path.join(DIRECTORY, rel_path)

# === Start server ===
try:
    os.chdir(DIRECTORY)
    print(f"🌐 Serving files from: {DIRECTORY}")
    print(f"✅ URL: http://localhost:{PORT}/deps_cleaned.dot")
    with ReusableTCPServer(("", PORT), CORSRequestHandler) as httpd:
        httpd.serve_forever()
except Exception as e:
    print(f"❌ Failed to start server: {e}")
    sys.exit(1)
