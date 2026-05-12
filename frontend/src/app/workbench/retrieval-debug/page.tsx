"use client";

import { useState } from "react";

export default function RetrievalDebugPage() {
  const [query, setQuery] = useState("What are waiting periods and exclusions?");
  const [data, setData] = useState<any>(null);

  const run = async () => {
    const res = await fetch("http://localhost:8000/api/v1/retrieval/debug", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, top_k: 5, filters: {} }),
    });
    setData(await res.json());
  };

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Retrieval Insight Workbench</h1>
      <textarea className="w-full border p-2" value={query} onChange={(e) => setQuery(e.target.value)} />
      <button className="px-3 py-2 bg-black text-white rounded" onClick={run}>Run Retrieval Debug</button>
      {data && (
        <div className="space-y-3">
          <div><b>User Query:</b> {data.query}</div>
          <div><b>Prompt Context:</b><pre className="bg-gray-100 p-2 overflow-auto">{data.prompt_context}</pre></div>
          <div><b>AI Response:</b> {data.ai_response}</div>
          <div><b>Similarity / Chunks:</b>
            <ul>{data.retrieved_chunks?.map((c:any)=><li key={c.chunk_id}>{c.chunk_id} | {c.similarity_score} | {c.section_title}</li>)}</ul>
          </div>
          <div><b>Generated Insights:</b><pre className="bg-gray-100 p-2">{JSON.stringify(data.generated_insights, null, 2)}</pre></div>
          <div><b>Debug Trace:</b><pre className="bg-gray-100 p-2">{JSON.stringify(data.debug_trace, null, 2)}</pre></div>
        </div>
      )}
    </div>
  );
}
