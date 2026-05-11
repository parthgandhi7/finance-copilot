"use server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

export async function uploadPdfAction(formData: FormData) {
  const file = formData.get("file");
  if (!(file instanceof File)) {
    throw new Error("No file provided");
  }

  const res = await fetch(`${BACKEND_URL}/api/v1/documents/upload-and-extract`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error(`Upload failed: ${res.status} ${res.statusText}`);
  }

  const data = await res.json();

  return {
    id: String(data.id),
    name: data.filename,
    status: "ready" as const,
    uploadedAt: new Date().toISOString().slice(0, 10),
    size: `${(data.file_size / 1024 / 1024).toFixed(2)} MB`,
    extracted: {
      raw_text: (data.extracted?.raw_text ?? "") as string,
      structured_sections: (data.extracted?.structured_sections ?? []) as { heading: string; content: string }[],
      document_type_hints: (data.extracted?.document_type_hints ?? []) as string[],
    },
  };
}
