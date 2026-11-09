
import type { ChatRequest, ChatResponse } from "@/types/chat";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_CHAT_API_URL ?? "http://localhost:8000";

export async function sendChatMessage(
  message: string,
  signal?: AbortSignal,
): Promise<ChatResponse> {
  const payload: ChatRequest = { message };

  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
      signal,
    });
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      throw error;
    }

    throw new Error(
      "Unable to reach the chatbot server. Check that the backend is running.",
    );
  }

  if (!response.ok) {
    if (response.status === 422) {
      throw new Error("Please enter a valid message and try again.");
    }

    if (response.status === 429) {
      throw new Error("Too many requests. Please wait a moment and try again.");
    }

    if (response.status >= 500) {
      throw new Error("The chatbot service is temporarily unavailable.");
    }

    throw new Error(`The chatbot request failed (HTTP ${response.status}).`);
  }

  let data: ChatResponse;

  try {
    data = (await response.json()) as ChatResponse;
  } catch {
    throw new Error("The chatbot returned an invalid response.");
  }

  if (
    typeof data.answer !== "string" ||
    !Array.isArray(data.sources) ||
    !data.sources.every(
      (source) =>
        typeof source.title === "string" &&
        typeof source.source === "string",
    )
  ) {
    throw new Error("The chatbot returned an unexpected response format.");
  }

  return data;
}
