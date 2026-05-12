import { RetrievalDebugRequest, RetrievalTrace } from "./types";

export async function runRetrievalDebug(request: RetrievalDebugRequest): Promise<RetrievalTrace> {
  const response = await fetch("/api/v1/retrieval/debug", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: request.query,
      top_k: request.topK ?? 8,
      filters: request.filters ?? {},
    }),
  });

  if (!response.ok) {
    throw new Error(`Retrieval debug failed with status ${response.status}`);
  }

  return response.json() as Promise<RetrievalTrace>;
}
