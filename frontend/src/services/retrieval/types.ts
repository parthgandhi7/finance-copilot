export type ClassificationMethod = "rule" | "model";

export interface RetrievalTrace {
  query: string;
  queryClassification: {
    label: string;
    confidence: number;
    method: ClassificationMethod;
  };
  retrieval: {
    chunks: RetrievedChunk[];
    appliedFilters: RetrievalFilter[];
    retrievalLatencyMs: number;
  };
  promptContext: {
    systemPrompt: string;
    assembledContext: string;
    tokenEstimate?: number;
  };
  response: {
    answer: string;
    citations: Citation[];
    grounded: boolean;
    confidence?: number;
  };
  insights: Insight[];
}

export interface RetrievedChunk {
  chunkId: string;
  documentId: string;
  sectionTitle?: string;
  pageNumber?: number;
  similarityScore: number;
  chunkType?: string;
  preview: string;
  retrievalReason?: string;
}

export interface RetrievalFilter {
  type: string;
  value: string;
}

export interface Citation {
  chunkId: string;
  sectionTitle?: string;
}

export interface Insight {
  insightId: string;
  insightType: string;
  severity: "low" | "medium" | "high";
  title: string;
  description: string;
  sourceChunks: string[];
  generatedBy: "rule" | "llm";
}

export interface RetrievalDebugRequest {
  query: string;
  topK?: number;
  filters?: RetrievalFilter[];
}
