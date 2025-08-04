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
import platform
from urllib.parse import urlparse, unquote

# === Detect bundle context ===
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

# === CONFIGURATION ===
JAVA_PATH = resource_path(r"openjdk\bin\java.exe") if platform.system() == "Windows" else resource_path("openjdk/bin/java")
DEPENDSPATH = resource_path("depends.jar")
CONVERTER_SCRIPT = resource_path("convert_dot_ids.py")
VISUALIZER_DIR = resource_path("dep-visualizer/dist")
VISUALIZER_PORT = 5173
DEFAULT_DOT_NAME = "deps_cleaned.dot"
GRAPHVIZ_DOT_PATH = resource_path(r"graphviz\bin\dot.exe") if platform.system() == "Windows" else resource_path("graphviz/bin/dot")

# === FUNCTIONS ===
def java_command():
    if JAVA_PATH and os.path.isfile(JAVA_PATH):
        print(f"✔️ Using bundled Java: {JAVA_PATH}")
        return JAVA_PATH
    java_sys = shutil.which("java")
    if java_sys:
        try:
            subprocess.run([java_sys, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            print(f"✔️ Using system Java: {java_sys}")
            return java_sys
        except subprocess.CalledProcessError:
            pass
    print("❌ No valid Java executable found. Please install Java or check JAVA_PATH.")
    sys.exit(1)

def find_dot_command():
    dot_sys = shutil.which("dot")
    if dot_sys:
        print(f"✔️ Found system Graphviz: {dot_sys}")
        return dot_sys
    if os.path.isfile(GRAPHVIZ_DOT_PATH):
        print(f"✔️ Using bundled Graphviz: {GRAPHVIZ_DOT_PATH}")
        return GRAPHVIZ_DOT_PATH
    print("❌ 'dot' from Graphviz not found. Please install Graphviz or bundle it in 'graphviz/bin/dot(.exe)'")
    sys.exit(1)

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

def run_cors_server(directory, port):
    directory = os.path.abspath(directory)
    if not os.path.isdir(directory):
        print(f"❌ Directory not found: {directory}")
        print("💡 Did you forget to build the React app or specify the correct output folder?")
        sys.exit(1)

    class CORSHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            return super().end_headers()
        def translate_path(self, path):
            parsed = urlparse(path)
            rel_path = os.path.normpath(unquote(parsed.path.lstrip("/")))
            full_path = os.path.join(directory, rel_path)
            print(f"📡 Resolving {path} -> {full_path}")
            return full_path
        def log_message(self, format, *args):
            print(f"[HTTP] {self.address_string()} - - {format % args}")

    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    print(f"📂 Static server root: {directory}")
    os.chdir(directory)
    with ReusableTCPServer(("", port), CORSHandler) as httpd:
        print(f"🚀 File server started on http://localhost:{port}")
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

    print(f"🔎 Checking for existing process on port {args.port}...")
    kill_port(args.port)
    kill_port(VISUALIZER_PORT)

    print("📦 Running Depends...")
    java = java_command()
    subprocess.run([
        java, "-jar", DEPENDSPATH,
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
    subprocess.run(["python", CONVERTER_SCRIPT, dot_input, dot_output, "--lang", lang], check=True)
    print("✅ Dot file processed successfully.")

    print("🖼️ Exporting graph images...")
    dot = find_dot_command()

    # Set plugin path for Windows Graphviz
    if platform.system() == "Windows":
        plugin_path = os.path.join(os.path.dirname(dot), "..", "lib", "graphviz")
        plugin_path = os.path.abspath(plugin_path)
        os.environ["GRAPHVIZ_DOT_PLUGIN_PATH"] = plugin_path
        print(f"🔌 Set GRAPHVIZ_DOT_PLUGIN_PATH={plugin_path}")

    try:
        subprocess.run([dot, "-Tpng", dot_output, "-o", os.path.join(out, "deps_cleaned.png")], check=True)
        subprocess.run([dot, "-Tsvg", dot_output, "-o", os.path.join(out, "deps_cleaned.svg")], check=True)
        print("✅ Export complete.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Graphviz 'dot' command failed: {e}")
        print("💡 Check if the DOT file is valid and Graphviz is correctly bundled.")
        sys.exit(1)

    if args.web:
        print("🌐 Launching web visualization...")

        server_thread = threading.Thread(target=run_cors_server, args=(out, args.port), daemon=True)
        server_thread.start()

        viz_server_thread = threading.Thread(target=run_cors_server, args=(VISUALIZER_DIR, VISUALIZER_PORT), daemon=True)
        viz_server_thread.start()

        dot_url = f"http://localhost:{args.port}/{DEFAULT_DOT_NAME}"
        visualizer_url = f"http://localhost:{VISUALIZER_PORT}/?dot={dot_url}"

        print(f"🌍 Opening: {visualizer_url}")
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
