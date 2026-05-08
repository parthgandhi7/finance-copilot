"use client";

import { FormEvent, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useCopilotStore } from "@/store/use-copilot-store";

export function ChatPanel() {
  const [input, setInput] = useState("");
  const { messages, addMessage } = useCopilotStore();

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!input.trim()) return;
    addMessage({ id: crypto.randomUUID(), role: "user", content: input });
    addMessage({ id: crypto.randomUUID(), role: "assistant", content: "Got it — I will analyze your documents and provide actionable financial insights." });
    setInput("");
  }

  return (
    <Card className="flex h-[70vh] flex-col p-4">
      <div className="flex-1 space-y-3 overflow-y-auto p-2">
        {messages.map((message) => (
          <div key={message.id} className={message.role === "assistant" ? "mr-8 rounded-lg bg-muted p-3" : "ml-8 rounded-lg bg-primary/10 p-3"}>{message.content}</div>
        ))}
      </div>
      <form onSubmit={onSubmit} className="mt-4 flex gap-2">
        <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask your copilot about spending, savings, or anomalies..." className="h-10 flex-1 rounded-md border border-border bg-card px-3 text-sm" />
        <Button type="submit">Send</Button>
      </form>
    </Card>
  );
}
