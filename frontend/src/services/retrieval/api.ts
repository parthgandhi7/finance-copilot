import { RetrievalDebugRequest, RetrievalTrace } from "./types";
import { runRetrievalDebugMock } from "./mock";

const USE_MOCK = true;

export async function runRetrievalDebug(request: RetrievalDebugRequest): Promise<RetrievalTrace> {
  if (USE_MOCK) {
    return runRetrievalDebugMock(request);
  }

  const response = await fetch("/api/v1/retrieval/debug", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Retrieval debug failed with status ${response.status}`);
  }

  return response.json() as Promise<RetrievalTrace>;
}
