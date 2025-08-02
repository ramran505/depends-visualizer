#!/usr/bin/env python3
import argparse
import subprocess
import os
import sys
import shutil
import signal
import http.server
import socketserver
import time
import webbrowser
from pathlib import Path
import threading
import tempfile

# === Detect bundle context ===
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

def extract_temp_file(path_in_bundle):
    """
    Copies a bundled file to a real temp path so external processes (e.g., Java) can access it.
    """
    src = resource_path(path_in_bundle)
    dst = os.path.join(tempfile.gettempdir(), os.path.basename(path_in_bundle))
    shutil.copyfile(src, dst)
    return dst

# === CONFIGURATION ===
DEPENDSPATH = extract_temp_file("depends.jar")
CONVERTER_SCRIPT = extract_temp_file("convert_dot_ids.py")
VISUALIZER_DIR = resource_path("dep-visualizer/dist")  # React build output folder
VISUALIZER_PORT = 5173
DEFAULT_DOT_NAME = "deps_cleaned.dot"

# === FUNCTIONS ===
def kill_port(port):
    try:
        if shutil.which("lsof"):
            pids = subprocess.check_output(["lsof", "-ti", f":{port}"], text=True).split()
            for pid in pids:
                print(f"🔪 Killing PID {pid} on port {port} (lsof)")
                os.kill(int(pid), signal.SIGKILL)
        elif shutil.which("fuser"):
            subprocess.run(["fuser", "-k", f"{port}/tcp"], check=True)
            print(f"🔪 Killed process on port {port} (fuser)")
    except subprocess.CalledProcessError:
        print(f"⚠️ No process found on port {port}")
    except Exception as e:
        print(f"⚠️ Error killing port {port}: {e}")

def run_visualizer_server(directory, port):
    class SPAHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            return super().end_headers()

        def do_GET(self):
            if self.path.startswith("/?dot=") or self.path == "/" or self.path.startswith("/index.html"):
                self.path = "/index.html"  # Always serve index.html for SPA
            return super().do_GET()

        def translate_path(self, path):
            rel_path = path.lstrip("/")
            return os.path.join(directory, rel_path)

    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    os.chdir(directory)
    with ReusableTCPServer(("", port), SPAHandler) as httpd:
        print(f"🧪 React visualizer server started at http://localhost:{port}")
        httpd.serve_forever()



# === MAIN ===
def main():
    parser = argparse.ArgumentParser(description="Depends + DOT visualizer CLI")
    parser.add_argument("language", choices=["java", "cpp", "python", "ruby", "c"], help="Language")
    parser.add_argument("src", help="Source folder")
    parser.add_argument("out", help="Output folder")
    parser.add_argument("--web", action="store_true", help="Enable browser visualization")
    parser.add_argument("--port", type=int, default=8000, help="Port to serve DOT file")
    args = parser.parse_args()

    lang = "cpp" if args.language == "c" else args.language
    out = os.path.abspath(args.out)
    Path(out).mkdir(parents=True, exist_ok=True)

    print(f"🔎 Killing processes on ports {args.port} and {VISUALIZER_PORT}...")
    kill_port(args.port)
    kill_port(VISUALIZER_PORT)

    print("📦 Running Depends...")
    subprocess.run([
        "java", "-jar", DEPENDSPATH,
        lang, args.src, "deps",
        "-f", "dot,json", "--detail", "--auto-include", "--map",
        "-d", out
    ], check=True)

    dot_files = list(Path(out).glob("*.dot"))
    if not dot_files:
        print(f"❌ No .dot files found in: {out}")
        sys.exit(1)
    dot_input = dot_files[0]
    dot_output = str(Path(out) / DEFAULT_DOT_NAME)

    print("🧹 Converting DOT file...")
    subprocess.run(["python3", CONVERTER_SCRIPT, dot_input, dot_output, "--lang", lang], check=True)
    print("✅ Dot file processed: ", dot_output)

    print("🖼️ Exporting graph images...")
    subprocess.run(["dot", "-Tpng", dot_output, "-o", os.path.join(out, "deps_cleaned.png")])
    subprocess.run(["dot", "-Tsvg", dot_output, "-o", os.path.join(out, "deps_cleaned.svg")])

    if args.web:
        print("🌐 Launching web visualization...")

        # Serve output folder (DOT file)
        threading.Thread(target=run_visualizer_server, args=(out, args.port), daemon=True).start()

        # Serve static React app
        threading.Thread(target=run_visualizer_server, args=(VISUALIZER_DIR, VISUALIZER_PORT), daemon=True).start()

        dot_url = f"http://localhost:{args.port}/{DEFAULT_DOT_NAME}"
        visualizer_url = f"http://localhost:{VISUALIZER_PORT}/?dot={dot_url}"

        print(f"🌍 Opening visualizer: {visualizer_url}")
        time.sleep(1)
        webbrowser.open(visualizer_url)

        print("🕸️ Press Ctrl+C to stop the servers and exit.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("🛑 Servers stopped. Exiting.")
            sys.exit(0)

if __name__ == "__main__":
    main()
