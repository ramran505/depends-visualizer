# 🕸️ depends-visualizer

**Visualize code dependencies in seconds — no setup required.**  
A self-contained tool that runs [Depends](https://github.com/multilang-depends/depends), cleans up the results, and opens an interactive browser-based graph for exploring your code’s structure.

---

## 🚀 One-Step Usage

Just run:

```bash
depends_visualize java example-projects/java-project output-java --web
```

✅ Works on Windows, macOS, and Linux  
✅ No installation required  
✅ No config needed  
✅ Interactive web-based graph viewer auto-launches

> The `depends_visualize` executable bundles everything: Depends engine, DOT processor, static visualizer, and file server.

---

## 🧠 What It Does

1. **Analyzes source code** with [`depends`](https://github.com/multilang-depends/depends)
2. **Generates a dependency graph** in Graphviz `.dot` format
3. **Cleans node IDs** for readable filenames and structures
4. **Serves an interactive viewer** (React + Cytoscape)
5. **Opens your browser** to explore the graph instantly

---

## 💡 Example

```bash
depends_visualize java example-projects/java-project output-java --web
```

This will:
- Analyze the Java code in `example-projects/java-project`
- Generate output in `output-java/`
- Launch a local server and open your browser to view the graph

---

## 🖥️ Alternative: Run as JAR

If you only have Java and want to run via `.jar`:

```bash
java -jar depends_visualize.jar java example-projects/java-project output-java --web
```

This version does the same thing — just requires Java 8+ installed.

---

## 🧩 Supported Languages

All languages supported by **Depends**:

- Java
- Python
- JavaScript
- Ruby
- C/C++
- C#
- More (as supported by [multilang-depends](https://github.com/multilang-depends/depends))

Just change the first argument in the command:

```bash
depends_visualize python my-python-project output-python --web
```

---

## 📁 Output Folder

After running, your output directory (e.g. `output-java`) will include:

| File | Description |
|------|-------------|
| `relations.dot` | Raw DOT graph from Depends |
| `relations.cleaned.dot` | Human-readable cleaned graph |
| (optional) `relations.png` | Future enhancement: export to image |

---

## 🌐 Visualizer Features

- Interactive graph viewer (Zoom / Pan / Click nodes)
- Nodes represent files or classes
- Edges show dependency relationships
- Fast and responsive even for large graphs

---

## 🔧 System Requirements

| Environment | Needed |
|-------------|--------|
| Python      | ❌ Not required (bundled) |
| Java        | ❌ Not required if using bundled version |
| Browser     | ✅ Required to view the graph (Chrome, Firefox, etc.)

> If using `java -jar`, Java 8+ must be installed manually.

---

## 🛠 Dev Mode (Optional)

If you want to modify or build your own:

- `dep-visualizer/` — React-based frontend (uses Cytoscape.js)
- `convert_dot_ids.py` — Clean DOT file node labels
- `depends.jar` — Original Depends analyzer

---

## 📦 Packaging

This tool is available as:

- ✅ Python CLI (`depends_visualize.py`)
- ✅ One-file `.exe` (Windows) or `.pyz` (cross-platform)
- ✅ `.jar` (Java-only usage)

Everything is bundled — no external installs needed.

---

## 📄 License

MIT License.  
Built on top of [Depends](https://github.com/multilang-depends/depends) and other open-source components.
