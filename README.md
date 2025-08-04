# 📊 depends-visualizer

> Analyze and visualize code dependencies using [Depends](https://github.com/multilang-depends/depends), Graphviz, and a modern web-based interface.

---

## 🧩 What It Does

`depends-visualizer` is a Python-powered CLI tool that:
- Runs the Depends analysis engine on a codebase (Java, C/C++, Python, Ruby)
- Cleans up the output `.dot` file with human-readable labels
- Optionally renders dependency graphs to `.png`/`.svg` using Graphviz
- Launches a beautiful interactive web UI to explore the dependencies visually

---

## 🚀 Quick Start

### ✅ Prerequisites

Make sure the following are installed **on your system**:

| Tool         | Version | Install |
|--------------|---------|---------|
| Python       | 3.7+    | https://python.org |
| Java         | 8+      | https://adoptium.net or https://openjdk.org |
| Graphviz     | any     | https://graphviz.org/download |
| Node.js      | 16+     | https://nodejs.org |
| npm          | 6+      | included with Node |
| Bun          | latest  | https://bun.sh |

> ⚠️ If you bundle Java or Graphviz locally (e.g., inside the repo), no global installation is needed.

---

### 📦 Install Node Dependencies]

From the root of the repo:

```bash
cd app/dep-visualizer
bun install
```

## Create a build folder

From the `app/dep-visualizer` folder:

```
bun run build
```

---

## 📂 How to Use

From the `app/` folder:

```bash
python3 depends_visualize.py <language> <src> <output-dir> [--web] [--port <port>]
```

### Arguments

| Name        | Description                                       |
|-------------|---------------------------------------------------|
| `language`  | One of: `java`, `cpp`, `python`, `ruby`, `c`     |
| `src`       | Path to your source code directory                |
| `output-dir`| Output directory for `.dot`, `.svg`, `.png`, etc. |
| `--web`     | Launch local browser-based interactive visualizer |
| `--port`    | (Optional) Custom port for serving the `.dot` file (default: `8000`) |

---

### 🧪 Example

```bash
python3 depends_visualize.py java ../example-projects/demo-java output-java --web
```

This will:
1. Run Depends on `demo-java`
2. Convert and clean the `.dot` file
3. Export a `.png` and `.svg` of the dependency graph
4. Launch the interactive visualizer in your browser

---

## 🖥️ Visual Output

- **`deps_cleaned.dot`**: Cleaned DOT file
- **`deps_cleaned.svg/png`**: Exported images
- **Interactive UI**: http://localhost:5173

---

## 🔧 Developer Notes

- You can bundle this into a `.exe` with [PyInstaller](https://pyinstaller.org/) (includes Java, Graphviz, etc.)
- The visualizer React app is prebuilt in `dep-visualizer/dist/`
- Uses a CORS-enabled static server to serve `.dot` and assets

---

## 📁 Project Structure

```
app/
├── depends_visualize.py      # Main CLI tool
├── convert_dot_ids.py        # Cleans up Depends output
├── depends.jar               # Depends core analyzer
├── graphviz/ (optional)      # Bundled Graphviz (for PyInstaller)
├── openjdk/ (optional)       # Bundled Java (for PyInstaller)
├── dep-visualizer/
│   ├── dist/                 # Built React UI
│   └── ...                   # Source code
```

---

## 🧹 Troubleshooting

- `dot: command not found`: Install Graphviz or bundle it
- `java: not found`: Install Java or bundle OpenJDK
- Output is blank? Make sure the `.dot` file is valid or try using `--detail --auto-include` in the Depends command

---

## 📜 License

MIT License. See `LICENSE`.
