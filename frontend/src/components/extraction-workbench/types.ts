export type ExtractionResult = {
  raw_text: string;
  structured_sections: { heading: string; content: string }[];
  document_type_hints: string[];
};

export type ExtractionWorkbenchResponse = {
  id: string;
  filename: string;
  file_size: number;
  created_at?: string;
  extracted?: ExtractionResult;
};
