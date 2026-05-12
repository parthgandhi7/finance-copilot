import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { ExtractionWorkbenchResponse } from "./types";

type Props = { data: ExtractionWorkbenchResponse };

function buildChunks(rawText: string): string[] {
  const lines = rawText.split(/\n+/).map((line) => line.trim()).filter(Boolean);
  const chunks: string[] = [];
  let buffer: string[] = [];

  lines.forEach((line) => {
    buffer.push(line);
    if (buffer.join(" ").length > 320) {
      chunks.push(buffer.join(" "));
      buffer = [];
    }
  });

  if (buffer.length > 0) chunks.push(buffer.join(" "));
  return chunks;
}

export function ExtractionViewers({ data }: Props) {
  const extracted = data.extracted;
  if (!extracted) return null;
  const chunks = buildChunks(extracted.raw_text ?? "");

  return (
    <Card className="p-4">
      <Tabs defaultValue="raw" className="w-full">
        <TabsList className="w-full justify-start overflow-x-auto">
          <TabsTrigger value="raw">Raw Text</TabsTrigger>
          <TabsTrigger value="json">Structured JSON</TabsTrigger>
          <TabsTrigger value="chunks">Semantic Chunks</TabsTrigger>
        </TabsList>

        <TabsContent value="raw">
          <pre className="max-h-[60vh] overflow-auto rounded-md border bg-muted/30 p-3 text-xs whitespace-pre-wrap">
            {extracted.raw_text || "No raw text found."}
          </pre>
        </TabsContent>

        <TabsContent value="json">
          <pre className="max-h-[60vh] overflow-auto rounded-md border bg-muted/30 p-3 text-xs whitespace-pre-wrap">
            {JSON.stringify(extracted, null, 2)}
          </pre>
        </TabsContent>

        <TabsContent value="chunks" className="space-y-3">
          <div className="flex flex-wrap gap-2">
            {extracted.document_type_hints.map((hint) => (
              <Badge key={hint}>{hint.replaceAll("_", " ")}</Badge>
            ))}
          </div>
          {chunks.length > 0 ? (
            <div className="space-y-2">
              {chunks.map((chunk, index) => (
                <div key={index} className="rounded-md border bg-muted/20 p-3">
                  <p className="mb-1 text-xs font-semibold text-muted-foreground">Chunk {index + 1}</p>
                  <p className="text-sm">{chunk}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">No chunks to display.</p>
          )}
        </TabsContent>
      </Tabs>
    </Card>
  );
}
