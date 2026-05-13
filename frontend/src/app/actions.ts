"use server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

export async function uploadDocumentAction(formData: FormData): Promise<{ id: string; filename: string; file_size: number }> {
  const res = await fetch(`${BACKEND_URL}/api/v1/documents/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    throw new Error(`Upload failed: ${res.status} ${res.statusText}`);
  }
  const data = await res.json();
  return { id: String(data.id), filename: data.filename, file_size: data.file_size };
}

export async function triggerExtractionAction(documentId: string): Promise<{ id: string; status: string }> {
  const res = await fetch(`${BACKEND_URL}/api/v1/documents/${documentId}/extract`, {
    method: "POST",
  });
  if (!res.ok) {
    throw new Error(`Failed to start extraction: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function getExtractionStatusAction(documentId: string): Promise<{ id: string; status: string }> {
  const res = await fetch(`${BACKEND_URL}/api/v1/documents/${documentId}/status`);
  if (!res.ok) {
    throw new Error(`Status check failed: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function getStructuredDataAction(documentId: string): Promise<{
  raw_text: string;
  structured_sections: { heading: string; content: string }[];
  document_type_hints: string[];
}> {
  const res = await fetch(`${BACKEND_URL}/api/v1/documents/${documentId}/structured`);
  if (!res.ok) {
    throw new Error(`Failed to fetch structured data: ${res.status} ${res.statusText}`);
  }
  const data = await res.json();
  return {
    raw_text: "",
    structured_sections: (data.structured_sections ?? []) as { heading: string; content: string }[],
    document_type_hints: (data.document_type_hints ?? []) as string[],
  };
}
