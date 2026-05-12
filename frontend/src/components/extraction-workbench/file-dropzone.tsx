"use client";

import { DragEvent } from "react";
import { FileUp } from "lucide-react";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

type FileDropzoneProps = {
  file: File | null;
  onFileChange: (file: File | null) => void;
  isDragging: boolean;
  setIsDragging: (value: boolean) => void;
};

export function FileDropzone({ file, onFileChange, isDragging, setIsDragging }: FileDropzoneProps) {
  function onDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);
    const dropped = event.dataTransfer.files?.[0];
    if (dropped?.type === "application/pdf") onFileChange(dropped);
  }

  return (
    <Card className="p-4">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={onDrop}
        className={cn(
          "flex min-h-56 flex-col items-center justify-center rounded-lg border border-dashed p-6 text-center transition",
          isDragging ? "border-primary bg-primary/5" : "border-border bg-muted/40"
        )}
      >
        <FileUp className="mb-3 h-8 w-8 text-primary" />
        <p className="text-base font-medium">Drop a PDF to run extraction</p>
        <p className="mt-1 text-sm text-muted-foreground">Built for raw, structured, and chunk-level debugging.</p>
        <input
          type="file"
          accept="application/pdf"
          className="mt-4 block text-sm"
          onChange={(e) => onFileChange(e.target.files?.[0] ?? null)}
        />
        {file && <p className="mt-2 text-xs text-muted-foreground">Selected: {file.name}</p>}
      </div>
    </Card>
  );
}
