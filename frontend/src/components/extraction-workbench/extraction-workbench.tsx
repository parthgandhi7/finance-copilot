"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { FileDropzone } from "./file-dropzone";
import { MetadataPanel } from "./metadata-panel";
import { ExtractionViewers } from "./extraction-viewers";
import { ExtractionWorkbenchResponse } from "./types";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

async function uploadPdfWithProgress(file: File, onProgress: (value: number) => void): Promise<ExtractionWorkbenchResponse> {
  return await new Promise((resolve, reject) => {
    const formData = new FormData();
    formData.append("file", file);

    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${BACKEND_URL}/api/v1/documents/upload-and-extract`);

    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) onProgress(Math.round((event.loaded / event.total) * 100));
    };

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        reject(new Error(`Upload failed: ${xhr.status} ${xhr.statusText}`));
      }
    };

    xhr.onerror = () => reject(new Error("Network error during upload"));
    xhr.send(formData);
  });
}

export function ExtractionWorkbench() {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<ExtractionWorkbenchResponse | null>(null);

  const uploadMutation = useMutation({
    mutationFn: async (uploadFile: File) => uploadPdfWithProgress(uploadFile, setProgress),
    onSuccess: (data) => {
      setResult(data);
      setFile(null);
      setProgress(100);
    },
  });

  return (
    <section className="space-y-4">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">Document Extraction Workbench</h1>
        <p className="text-muted-foreground">Developer-facing pipeline visibility for PDF extraction and schema outputs.</p>
      </div>

      <div className="grid gap-4 lg:grid-cols-[320px_1fr]">
        <div className="space-y-4">
          <FileDropzone file={file} onFileChange={setFile} isDragging={isDragging} setIsDragging={setIsDragging} />
          <Button className="w-full" disabled={!file || uploadMutation.isPending} onClick={() => file && uploadMutation.mutate(file)}>
            {uploadMutation.isPending ? "Extracting..." : "Run Extraction"}
          </Button>
          <Progress value={progress} />
          {uploadMutation.isError && <p className="text-sm text-red-600">{uploadMutation.error.message}</p>}
          <MetadataPanel data={result} />
        </div>

        <div className="min-h-[60vh]">
          {result ? (
            <ExtractionViewers data={result} />
          ) : (
            <div className="flex h-full items-center justify-center rounded-xl border border-dashed bg-muted/20 p-8 text-center text-sm text-muted-foreground">
              Upload a PDF to inspect raw text, JSON extraction, semantic chunks, and metadata.
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
