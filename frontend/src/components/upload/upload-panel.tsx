"use client";

import { useState, DragEvent } from "react";
import { UploadCloud } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { uploadPdfAction } from "@/app/actions";
import { useCopilotStore } from "@/store/use-copilot-store";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export function UploadPanel() {
  const [file, setFile] = useState<File | null>(null);
  const addDocument = useCopilotStore((s) => s.addDocument);

  const uploadMutation = useMutation({
    mutationFn: async (uploadFile: File) => {
      const formData = new FormData();
      formData.append("file", uploadFile);
      return uploadPdfAction(formData);
    },
    onSuccess: (document) => {
      addDocument(document);
      setFile(null);
    }
  });

  function onDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    const dropped = event.dataTransfer.files?.[0];
    if (dropped?.type === "application/pdf") setFile(dropped);
  }

  return (
    <Card className="p-6">
      <div onDragOver={(e) => e.preventDefault()} onDrop={onDrop} className="flex min-h-64 flex-col items-center justify-center rounded-lg border border-dashed border-border bg-muted/40 p-8 text-center">
        <UploadCloud className="mb-3 h-8 w-8 text-primary" />
        <p className="text-base font-medium">Drag and drop your PDF here</p>
        <p className="mt-1 text-sm text-muted-foreground">or choose a file to start AI-powered analysis</p>
        <input type="file" accept="application/pdf" className="mt-4 block text-sm" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        <Button className="mt-4" disabled={!file || uploadMutation.isPending} onClick={() => file && uploadMutation.mutate(file)}>
          {uploadMutation.isPending ? "Uploading..." : "Upload PDF"}
        </Button>
      </div>
    </Card>
  );
}
