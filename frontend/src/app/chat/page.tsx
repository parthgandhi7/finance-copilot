import { ChatPanel } from "@/components/chat/chat-panel";

export default function ChatPage() {
  return (
    <section className="space-y-4">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">Copilot Chat</h1>
        <p className="text-muted-foreground">Ask questions about cashflow, trends, and anomalies across your uploaded documents.</p>
      </div>
      <ChatPanel />
    </section>
  );
}
