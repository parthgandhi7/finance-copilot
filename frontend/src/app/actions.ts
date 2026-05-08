"use server";

export async function uploadPdfAction(formData: FormData) {
  const file = formData.get("file");
  if (!(file instanceof File)) {
    throw new Error("No file provided");
  }

  return {
    id: crypto.randomUUID(),
    name: file.name,
    status: "processing" as const,
    uploadedAt: new Date().toISOString().slice(0, 10),
    size: `${(file.size / 1024 / 1024).toFixed(2)} MB`
  };
}
