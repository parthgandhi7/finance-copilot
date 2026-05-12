import { Card } from "@/components/ui/card";
import { ExtractionWorkbenchResponse } from "./types";

type Props = { data: ExtractionWorkbenchResponse | null };

export function MetadataPanel({ data }: Props) {
  return (
    <Card className="p-4">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">Extraction Metadata</h2>
      {!data ? (
        <p className="text-sm text-muted-foreground">Upload a PDF to populate metadata.</p>
      ) : (
        <dl className="grid grid-cols-1 gap-2 text-sm">
          <div className="rounded-md border bg-muted/30 p-2"><dt className="text-muted-foreground">Document ID</dt><dd>{data.id}</dd></div>
          <div className="rounded-md border bg-muted/30 p-2"><dt className="text-muted-foreground">Filename</dt><dd>{data.filename}</dd></div>
          <div className="rounded-md border bg-muted/30 p-2"><dt className="text-muted-foreground">Size (bytes)</dt><dd>{data.file_size}</dd></div>
          <div className="rounded-md border bg-muted/30 p-2"><dt className="text-muted-foreground">Processed At</dt><dd>{data.created_at ?? "N/A"}</dd></div>
          <div className="rounded-md border bg-muted/30 p-2"><dt className="text-muted-foreground">Sections</dt><dd>{data.extracted?.structured_sections.length ?? 0}</dd></div>
        </dl>
      )}
    </Card>
  );
}
