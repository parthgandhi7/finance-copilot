import { UploadPanel } from "@/components/upload/upload-panel";

export default function UploadPage() {
  return (
    <section className="mx-auto max-w-3xl space-y-4">
      <h1 className="text-3xl font-semibold tracking-tight">Upload Financial Documents</h1>
      <p className="text-muted-foreground">Drop account statements, invoices, and reports to power your AI copilot.</p>
      <UploadPanel />
    </section>
  );
}
