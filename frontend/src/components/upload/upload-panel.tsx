"use client";

import { useState, DragEvent } from "react";
import { UploadCloud } from "lucide-react";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  uploadDocumentAction,
  triggerExtractionAction,
  getExtractionStatusAction,
  getStructuredDataAction,
} from "@/app/actions";
import { useCopilotStore } from "@/store/use-copilot-store";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

type ExtractionResult = {
  raw_text: string;
  structured_sections: { heading: string; content: string }[];
  document_type_hints: string[];
};

export function UploadPanel() {
  const [file, setFile] = useState<File | null>(null);
  const [extractedResult, setExtractedResult] = useState<ExtractionResult | null>(null);
  const [uploadedDocId, setUploadedDocId] = useState<string | null>(null);
  const [extractionError, setExtractionError] = useState<string | null>(null);
  const addDocument = useCopilotStore((s) => s.addDocument);

  const uploadMutation = useMutation({
    mutationFn: async (uploadFile: File) => {
      const formData = new FormData();
      formData.append("file", uploadFile);
      const doc = await uploadDocumentAction(formData);
      await triggerExtractionAction(doc.id);
      return doc;
    },
    onSuccess: (doc) => {
      addDocument({
        id: doc.id,
        name: doc.filename,
        status: "ready" as const,
        uploadedAt: new Date().toISOString().slice(0, 10),
        size: `${(doc.file_size / 1024 / 1024).toFixed(2)} MB`,
      });
      setFile(null);
      setUploadedDocId(doc.id);
      setExtractionError(null);
    },
  });

  const isPolling =
    !!uploadedDocId && !extractedResult && !extractionError;

  useQuery({
    queryKey: ["extraction-status", uploadedDocId],
    queryFn: async () => {
      const { status } = await getExtractionStatusAction(uploadedDocId!);
      if (status === "extracted") {
        const structured = await getStructuredDataAction(uploadedDocId!);
        setExtractedResult(structured);
        setUploadedDocId(null);
      } else if (status === "failed") {
        setExtractionError("Extraction failed. Please try again.");
        setUploadedDocId(null);
      }
      return status;
    },
    enabled: isPolling,
    refetchInterval: isPolling ? 2000 : false,
  });

  function onDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    const dropped = event.dataTransfer.files?.[0];
    if (dropped?.type === "application/pdf") {
      setFile(dropped);
      setExtractedResult(null);
      setExtractionError(null);
    }
  }

  function onFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    setFile(e.target.files?.[0] ?? null);
    setExtractedResult(null);
    setExtractionError(null);
  }

  const isPending = uploadMutation.isPending || isPolling;
  const buttonLabel = uploadMutation.isPending ? "Uploading..." : isPolling ? "Extracting..." : "Upload PDF";

  return (
    <div className="flex flex-col gap-6">
      <Card className="p-6">
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={onDrop}
          className="flex min-h-64 flex-col items-center justify-center rounded-lg border border-dashed border-border bg-muted/40 p-8 text-center"
        >
          <UploadCloud className="mb-3 h-8 w-8 text-primary" />
          <p className="text-base font-medium">Drag and drop your PDF here</p>
          <p className="mt-1 text-sm text-muted-foreground">or choose a file to start AI-powered analysis</p>
          <input type="file" accept="application/pdf" className="mt-4 block text-sm" onChange={onFileChange} />
          <Button
            className="mt-4"
            disabled={!file || isPending}
            onClick={() => file && uploadMutation.mutate(file)}
          >
            {buttonLabel}
          </Button>
          {(uploadMutation.isError || extractionError) && (
            <p className="mt-3 text-sm text-destructive">
              {extractionError ??
                (uploadMutation.error instanceof Error ? uploadMutation.error.message : "Upload failed")}
            </p>
          )}
        </div>
      </Card>

      {extractedResult && (
        <Card className="p-6">
          <h2 className="mb-4 text-lg font-semibold">Extracted Content</h2>

          {extractedResult.document_type_hints.length > 0 && (
            <div className="mb-4 flex flex-wrap gap-2">
              {extractedResult.document_type_hints.map((hint) => (
                <span
                  key={hint}
                  className="rounded-full bg-primary/10 px-3 py-0.5 text-xs font-medium text-primary capitalize"
                >
                  {hint.replace(/_/g, " ")}
                </span>
              ))}
            </div>
          )}

          {extractedResult.structured_sections.length > 0 ? (
            <div className="flex flex-col gap-4">
              {extractedResult.structured_sections.map((section, i) => (
                <div key={i} className="rounded-md border border-border bg-muted/30 p-4">
                  {section.heading && (
                    <p className="mb-1 text-sm font-semibold text-foreground">{section.heading}</p>
                  )}
                  <p className={cn("text-sm text-muted-foreground whitespace-pre-wrap", !section.heading && "text-foreground")}>
                    {section.content}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <pre className="max-h-96 overflow-y-auto rounded-md border border-border bg-muted/30 p-4 text-xs text-muted-foreground whitespace-pre-wrap break-words">
              {extractedResult.raw_text || "No text extracted."}
            </pre>
          )}
        </Card>
      )}
    </div>
  );
}
