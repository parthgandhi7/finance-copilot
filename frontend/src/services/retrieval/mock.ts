import { RetrievalDebugRequest, RetrievalTrace } from "./types";

const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export async function runRetrievalDebugMock(request: RetrievalDebugRequest): Promise<RetrievalTrace> {
  await wait(450);

  return {
    query: request.query,
    queryClassification: {
      label: "policy_exclusions",
      confidence: 0.91,
      method: "model",
    },
    retrieval: {
      retrievalLatencyMs: 142,
      appliedFilters: request.filters ?? [
        { type: "document_type", value: "insurance_policy" },
        { type: "locale", value: "us" },
      ],
      chunks: [
        {
          chunkId: "chunk_1001",
          documentId: "doc_policy_2025_04",
          sectionTitle: "Waiting Periods",
          pageNumber: 7,
          similarityScore: 0.93,
          chunkType: "policy_clause",
          preview: "Coverage for pre-existing conditions has a 12 month waiting period unless continuous coverage criteria are met.",
          retrievalReason: "High lexical overlap with 'waiting periods'.",
        },
        {
          chunkId: "chunk_1008",
          documentId: "doc_policy_2025_04",
          sectionTitle: "General Exclusions",
          pageNumber: 13,
          similarityScore: 0.89,
          chunkType: "exclusion_clause",
          preview: "The policy excludes elective cosmetic procedures, non-prescribed treatment, and experimental therapies.",
          retrievalReason: "Semantic similarity to exclusion language.",
        },
      ],
    },
    promptContext: {
      systemPrompt: "You are Finance Copilot. Answer only using supplied evidence. Return citations by chunkId.",
      assembledContext:
        "[chunk_1001] Coverage for pre-existing conditions has a 12 month waiting period...\n[chunk_1008] The policy excludes elective cosmetic procedures...",
      tokenEstimate: 386,
    },
    response: {
      grounded: true,
      confidence: 0.87,
      answer:
        "The policy has a 12-month waiting period for pre-existing conditions and excludes elective cosmetic and experimental procedures unless explicitly covered.",
      citations: [
        { chunkId: "chunk_1001", sectionTitle: "Waiting Periods" },
        { chunkId: "chunk_1008", sectionTitle: "General Exclusions" },
      ],
    },
    insights: [
      {
        insightId: "ins_01",
        insightType: "retrieval_precision",
        severity: "medium",
        title: "Top chunks are tightly clustered in one document",
        description: "Retrieval may miss supplemental riders; consider expanding document scope when confidence is below 0.9.",
        sourceChunks: ["chunk_1001", "chunk_1008"],
        generatedBy: "rule",
      },
      {
        insightId: "ins_02",
        insightType: "citation_coverage",
        severity: "low",
        title: "All response claims are cited",
        description: "Current answer terms map directly to retrieved evidence with explicit chunk references.",
        sourceChunks: ["chunk_1001", "chunk_1008"],
        generatedBy: "llm",
      },
    ],
  };
}
