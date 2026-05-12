export interface RetrievalTrace {
  query: string;
  classification: {
    label: string;
    confidence: number;
    method: "rule" | "model";
  };
  retrieval: {
    chunks: RetrievedChunk[];
    filters: Array<{ type: string; value: string }> | Record<string, string>;
    latency_ms: number;
  };
  prompt_context: {
    assembled_context: string;
    estimated_tokens?: number;
  };
  response: {
    answer: string;
    citations: Citation[];
    grounded: boolean;
  };
  insights: Insight[];
}

export interface RetrievedChunk {
  chunk_id: string;
  document_id: string;
  section_title?: string;
  page_number?: number;
  similarity_score: number;
  chunk_type?: string;
  content: string;
  retrieval_reason?: string;
}

export interface Citation {
  chunk_id: string;
  section_title?: string;
}

export interface Insight {
  insight_id: string;
  insight_type: string;
  severity: "low" | "medium" | "high";
  title: string;
  description: string;
  source_chunks: string[];
  generated_by: "rule" | "llm";
}

export interface RetrievalDebugRequest {
  query: string;
  topK?: number;
  filters?: Record<string, string>;
}
