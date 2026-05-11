export type DocumentItem = {
  id: string;
  name: string;
  status: "processing" | "ready";
  uploadedAt: string;
  size: string;
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};
