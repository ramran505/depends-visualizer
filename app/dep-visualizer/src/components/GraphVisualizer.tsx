import { useRef, useEffect, useState } from "react";
import cytoscape from "cytoscape";
import { Button } from "@/components/ui/button";

function parseDot(text: string) {
  const nodes = new Set<string>();
  const edges: { source: string; target: string }[] = [];
  const regex = /"([^"]+)"\s*->\s*"([^"]+)"/g;

  let match;
  while ((match = regex.exec(text)) !== null) {
    const [, src, tgt] = match;
    nodes.add(src);
    nodes.add(tgt);
    edges.push({ source: src, target: tgt });
  }

  return { nodes: Array.from(nodes), edges };
}

export default function GraphVisualizer() {
  const cyRef = useRef<cytoscape.Core | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [graphInput, setGraphInput] = useState("");
  const [error, setError] = useState<string | null>(null);

  const loadGraph = (text: string) => {
    try {
      const { nodes, edges } = parseDot(text);
      const elements = [
        ...nodes.map((id) => ({ data: { id, label: id } })),
        ...edges.map((e) => ({ data: { source: e.source, target: e.target } })),
      ];

      if (!cyRef.current) return;

      cyRef.current.elements().remove();
      cyRef.current.add(elements);
      cyRef.current.layout({ name: "breadthfirst", directed: true }).run();
    } catch (err) {
      setError("❌ Failed to parse graph data.");
    }
  };

  useEffect(() => {
    if (!containerRef.current) return;
    const cy = cytoscape({
      container: containerRef.current,
      elements: [],
      style: [
        {
          selector: "node",
          style: {
            label: "data(label)",
            "background-color": "#60a5fa",
            color: "#fff",
            "text-valign": "center",
            "text-outline-color": "#60a5fa",
            "text-outline-width": 2,
            "font-size": "12px",
            width: 40,
            height: 40,
          },
        },
        {
          selector: "edge",
          style: {
            width: 2,
            "line-color": "#aaa",
            "target-arrow-shape": "triangle",
            "target-arrow-color": "#aaa",
            "arrow-scale": 1.5,
            "curve-style": "bezier",
          },
        },
      ],
    });

    cyRef.current = cy;
    return () => cy.destroy();
  }, []);

  // Automatically fetch dot file from URL param (?dot=...)
  useEffect(() => {
    const url = new URL(window.location.href);
    const dotParam = url.searchParams.get("dot");

    if (dotParam) {
      fetch(dotParam)
        .then((res) => {
          if (!res.ok) throw new Error("Fetch failed");
          return res.text();
        })
        .then((text) => {
          setGraphInput(text);
          loadGraph(text);
        })
        .catch(() => setError("❌ Failed to fetch DOT file from URL."));
    }
  }, []);

  return (
    <div className="flex flex-col h-screen w-screen p-4 box-border">
      <div className="flex flex-col gap-2 mb-4 w-full">
        <textarea
          className="w-full h-48 border p-2 font-mono text-sm rounded-lg resize-none"
          placeholder='Paste DOT content here or use ?dot=... in URL'
          value={graphInput}
          onChange={(e) => {
            setGraphInput(e.target.value);
            setError(null);
          }}
        />
        <Button onClick={() => loadGraph(graphInput)}>Load Graph</Button>
        {error && <div className="text-red-500 mt-2">{error}</div>}
      </div>

      <div className="flex-1 w-full border rounded-lg" ref={containerRef} />
    </div>
  );
}
