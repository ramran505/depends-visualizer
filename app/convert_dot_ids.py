import sys
import argparse
import os
import re

def parse_args():
    parser = argparse.ArgumentParser(description="Convert dot node IDs to readable class/file names")
    parser.add_argument("input_dot", help="Path to input .dot file")
    parser.add_argument("output_dot", help="Path to output cleaned .dot file")
    parser.add_argument("--lang", default="java", help="Project language: java | cpp | python | c | ruby")
    return parser.parse_args()

def extract_mapping(lines, lang):
    mapping = {}
    for line in lines:
        if line.strip().startswith("//"):
            try:
                idx, path = line.strip()[2:].split(":", 1)
                idx = idx.strip()

                if "src/" in path:
                    relevant = path.split("src/", 1)[1]
                else:
                    relevant = os.path.basename(path)

                # Language-specific cleanup
                if lang == "java":
                    name = relevant.replace("_java", "").replace("/", ".").replace(".java", "")
                elif lang in ["cpp", "c"]:
                    name = os.path.basename(relevant).replace(".cpp", "").replace(".h", "")
                elif lang == "python":
                    name = relevant.replace(".py", "").replace("/", ".")
                elif lang == "ruby":
                    name = relevant.replace(".rb", "").replace("/", ".")
                else:
                    name = os.path.basename(relevant)

                mapping[idx] = name
            except Exception:
                continue
    return mapping

def transform_dot(lines, mapping):
    output = ["digraph\n{"]
    node_pattern = re.compile(r'(\d+)\s*->\s*(\d+);')

    for line in lines:
        if line.strip().startswith("//") or line.strip() in ["digraph", "{", "}"]:
            continue

        match = node_pattern.search(line)
        if match:
            src, dst = match.groups()
            src_label = mapping.get(src, src)
            dst_label = mapping.get(dst, dst)
            output.append(f'"{src_label}" -> "{dst_label}";')

    output.append("}")
    return output

if __name__ == "__main__":
    args = parse_args()

    try:
        lines = open(args.input_dot).readlines()
        mapping = extract_mapping(lines, args.lang.lower())
        cleaned = transform_dot(lines, mapping)

        with open(args.output_dot, "w") as f:
            f.write("\n".join(cleaned))

        print("✅ Dot file processed successfully.")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
