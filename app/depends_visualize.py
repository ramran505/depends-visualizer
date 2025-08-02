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
import runpy
import platform  # ✅ added to detect OS

# === Detect bundle context ===
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

def extract_temp_file(path_in_bundle):
    src = resource_path(path_in_bundle)
    dst = os.path.join(tempfile.gettempdir(), os.path.basename(path_in_bundle))
    shutil.copyfile(src, dst)
    return dst

# === CONFIGURATION ===
DEPENDSPATH = extract_temp_file("depends.jar")
CONVERTER_SCRIPT = resource_path("convert_dot_ids.py")
VISUALIZER_DIR = resource_path("dep-visualizer/dist")
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
            self.path = self.path.rstrip("/")  # Prevent index.html/
            if self.path in ["/", "/index.html"] or self.path.startswith("/?dot=") or self.path.startswith("/index.html?"):
                self.path = "/index.html"
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

    print("🧺 Converting DOT file...")
    sys.argv = ['convert_dot_ids.py', str(dot_input), dot_output, '--lang', lang]
    script_path = os.path.join(sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__), 'convert_dot_ids.py')
    runpy.run_path(script_path, run_name="__main__")

    print("✅ Dot file processed: ", dot_output)
    print("🖼️ Exporting graph images...")

    # Setup dot and plugin path
    if getattr(sys, 'frozen', False) and platform.system() == "Windows":
        dot_exe = os.path.join(sys._MEIPASS, 'graphviz', 'bin', 'dot.exe')
        plugin_path = os.path.join(sys._MEIPASS, 'graphviz', 'bin')
    else:
        dot_exe = shutil.which("dot") or "dot"
        plugin_path = None

    if not os.path.exists(dot_exe):
        print("❌ Could not find Graphviz dot executable.")
        print("💡 Install Graphviz or bundle it in /graphviz/bin/")
        sys.exit(1)

    env = os.environ.copy()
    if plugin_path:
        env["GRAPHVIZ_DOT_PLUGIN_PATH"] = plugin_path

    subprocess.run([dot_exe, "-Tpng", dot_output, "-o", os.path.join(out, "deps_cleaned.png")], check=True, env=env)
    subprocess.run([dot_exe, "-Tsvg", dot_output, "-o", os.path.join(out, "deps_cleaned.svg")], check=True, env=env)

    if args.web:
        print("🌐 Launching web visualization...")
        threading.Thread(target=run_visualizer_server, args=(out, args.port), daemon=True).start()
        threading.Thread(target=run_visualizer_server, args=(VISUALIZER_DIR, VISUALIZER_PORT), daemon=True).start()

        dot_url = f"http://localhost:{args.port}/{DEFAULT_DOT_NAME}"
        visualizer_url = f"http://localhost:{VISUALIZER_PORT}/?dot={dot_url}"

        print(f"🌍 Opening visualizer: {visualizer_url}")
        time.sleep(1)
        webbrowser.open(visualizer_url)

        print("🔸 Press Ctrl+C to stop the servers and exit.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("🛑 Servers stopped. Exiting.")
            sys.exit(0)

if __name__ == "__main__":
    main()