"use client";

import { Card } from "@/components/ui/card";
import { useCopilotStore } from "@/store/use-copilot-store";

export function DocumentList() {
  const docs = useCopilotStore((s) => s.documents);
  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold">Documents</h2>
      <div className="mt-4 space-y-3">
        {docs.map((doc) => (
          <div key={doc.id} className="flex items-center justify-between rounded-lg border border-border p-3">
            <div>
              <p className="font-medium">{doc.name}</p>
              <p className="text-xs text-muted-foreground">Uploaded {doc.uploadedAt} • {doc.size}</p>
            </div>
            <span className="rounded-full bg-muted px-2 py-1 text-xs capitalize">{doc.status}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}
