"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { runRetrievalDebug } from "@/services/retrieval/api";
import { RetrievalTrace } from "@/services/retrieval/types";

function severityClasses(severity: "low" | "medium" | "high") {
  if (severity === "high") return "bg-red-100 text-red-700";
  if (severity === "medium") return "bg-amber-100 text-amber-700";
  return "bg-emerald-100 text-emerald-700";
}

export function RetrievalDebugWorkbench() {
  const [query, setQuery] = useState("What are waiting periods and exclusions?");
  const [trace, setTrace] = useState<RetrievalTrace | null>(null);

  const retrievalMutation = useMutation({
    mutationFn: runRetrievalDebug,
    onSuccess: (data) => setTrace(data),
  });

  return (
    <div className="space-y-4 p-6">
      <Card className="p-4 space-y-3">
        <h1 className="text-xl font-semibold">Retrieval Debug Workbench</h1>
        <p className="text-sm text-muted-foreground">Observability-first UI for retrieval explainability, trace inspection, and AI evaluation workflows.</p>
        <textarea
          className="min-h-24 w-full rounded-md border border-border bg-background p-3 text-sm"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Enter user query to run retrieval debug trace"
        />
        <div className="flex items-center gap-2">
          <Button onClick={() => retrievalMutation.mutate({ query, topK: 8 })} disabled={retrievalMutation.isPending || !query.trim()}>
            {retrievalMutation.isPending ? "Running trace..." : "Run Retrieval Trace"}
          </Button>
          {retrievalMutation.isError && <span className="text-sm text-red-600">Failed to run trace.</span>}
        </div>
      </Card>

      {retrievalMutation.isPending && <Card className="p-4 text-sm text-muted-foreground">Loading retrieval trace...</Card>}

      {trace && (
        <Tabs defaultValue="retrieval" className="space-y-2">
          <TabsList>
            <TabsTrigger value="retrieval">Retrieval</TabsTrigger>
            <TabsTrigger value="prompt">Prompt</TabsTrigger>
            <TabsTrigger value="response">Response</TabsTrigger>
            <TabsTrigger value="insights">Deterministic Insights</TabsTrigger>
          </TabsList>

          <TabsContent value="retrieval" className="grid gap-3 md:grid-cols-2">
            <Card className="p-4 space-y-3">
              <h2 className="font-medium">Intent Classification</h2>
              <div className="text-sm">{trace.queryClassification.label}</div>
              <div className="text-sm text-muted-foreground">Method: {trace.queryClassification.method}</div>
              <div className="text-sm text-muted-foreground">Confidence: {trace.queryClassification.confidence.toFixed(2)}</div>
            </Card>

            <Card className="p-4 space-y-3">
              <h2 className="font-medium">Retrieval Trace</h2>
              <div className="text-sm text-muted-foreground">Latency: {trace.retrieval.retrievalLatencyMs}ms</div>
              <div className="text-sm">Metadata Filters</div>
              <div className="flex flex-wrap gap-2">
                {trace.retrieval.appliedFilters.map((filter) => (
                  <Badge key={`${filter.type}-${filter.value}`}>{filter.type}: {filter.value}</Badge>
                ))}
              </div>
            </Card>

            <Card className="p-4 space-y-3 md:col-span-2">
              <h2 className="font-medium">Retrieved Chunks + Similarity Scores</h2>
              <div className="space-y-2">
                {trace.retrieval.chunks.map((chunk) => (
                  <details key={chunk.chunkId} className="rounded-md border border-border p-3">
                    <summary className="cursor-pointer text-sm font-medium">
                      {chunk.chunkId} · score {chunk.similarityScore.toFixed(2)} · {chunk.sectionTitle ?? "Untitled"}
                    </summary>
                    <div className="mt-2 space-y-1 text-sm text-muted-foreground">
                      <div>document: {chunk.documentId}</div>
                      <div>page: {chunk.pageNumber ?? "n/a"}</div>
                      <div>type: {chunk.chunkType ?? "n/a"}</div>
                      <div>reason: {chunk.retrievalReason ?? "n/a"}</div>
                      <p className="rounded bg-muted p-2 text-foreground">{chunk.preview}</p>
                    </div>
                  </details>
                ))}
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="prompt">
            <Card className="p-4 space-y-3">
              <h2 className="font-medium">Prompt Context Viewer</h2>
              <div className="text-sm text-muted-foreground">Token Estimate: {trace.promptContext.tokenEstimate ?? "n/a"}</div>
              <details open>
                <summary className="cursor-pointer text-sm font-medium">System Prompt</summary>
                <pre className="mt-2 overflow-x-auto rounded bg-muted p-2 text-xs">{trace.promptContext.systemPrompt}</pre>
              </details>
              <details>
                <summary className="cursor-pointer text-sm font-medium">Assembled Retrieval Context (Collapsible)</summary>
                <pre className="mt-2 max-h-72 overflow-auto rounded bg-muted p-2 text-xs">{trace.promptContext.assembledContext}</pre>
              </details>
            </Card>
          </TabsContent>

          <TabsContent value="response" className="grid gap-3 md:grid-cols-2">
            <Card className="p-4 space-y-2 md:col-span-2">
              <h2 className="font-medium">Grounded AI Response</h2>
              <Badge className={trace.response.grounded ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"}>
                {trace.response.grounded ? "Grounded" : "Not Grounded"}
              </Badge>
              <p className="text-sm">{trace.response.answer}</p>
            </Card>

            <Card className="p-4 space-y-2">
              <h2 className="font-medium">Evidence / Citations</h2>
              <ul className="space-y-1 text-sm">
                {trace.response.citations.map((citation) => (
                  <li key={`${citation.chunkId}-${citation.sectionTitle ?? "none"}`}>{citation.chunkId} · {citation.sectionTitle ?? "n/a"}</li>
                ))}
              </ul>
            </Card>
          </TabsContent>

          <TabsContent value="insights">
            <Card className="p-4 space-y-3">
              <h2 className="font-medium">Deterministic Insights Panel</h2>
              <div className="space-y-2">
                {trace.insights.map((insight) => (
                  <div key={insight.insightId} className="rounded-md border border-border p-3 text-sm">
                    <div className="mb-2 flex items-center gap-2">
                      <span className="font-medium">{insight.title}</span>
                      <Badge className={severityClasses(insight.severity)}>{insight.severity}</Badge>
                      <Badge>{insight.generatedBy}</Badge>
                    </div>
                    <p className="text-muted-foreground">{insight.description}</p>
                  </div>
                ))}
              </div>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}
