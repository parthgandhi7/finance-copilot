import { create } from "zustand";
import { ChatMessage, DocumentItem } from "@/lib/types";

type CopilotState = {
  documents: DocumentItem[];
  messages: ChatMessage[];
  addDocument: (document: DocumentItem) => void;
  addMessage: (message: ChatMessage) => void;
};

export const useCopilotStore = create<CopilotState>((set) => ({
  documents: [
    {
      id: "seed-1",
      name: "Q1_Statement.pdf",
      status: "ready",
      uploadedAt: "2026-05-08",
      size: "2.1 MB"
    }
  ],
  messages: [
    {
      id: "seed-msg-1",
      role: "assistant",
      content: "I reviewed your latest statement. Cash flow improved by 8.2% month-over-month."
    }
  ],
  addDocument: (document) => set((state) => ({ documents: [document, ...state.documents] })),
  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] }))
}));
