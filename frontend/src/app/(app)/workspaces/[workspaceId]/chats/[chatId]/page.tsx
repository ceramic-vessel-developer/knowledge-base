"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import type { Chat, ChatMessage } from "@/lib/types";
import styles from "./page.module.css";

export default function ChatPage() {
  const params = useParams<{ workspaceId: string; chatId: string }>();
  const [chat, setChat] = useState<Chat | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [total, setTotal] = useState(0);
  const [question, setQuestion] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  const load = useCallback(async () => {
    const [chatData, msgData] = await Promise.all([
      api.getChat(params.chatId),
      api.listMessages(params.chatId, 0, 100),
    ]);
    setChat(chatData);
    setMessages(msgData.items);
    setTotal(msgData.total);
  }, [params.chatId]);

  useEffect(() => {
    load().catch((err) =>
      setError(err instanceof ApiError ? String(err.detail) : "Failed to load chat"),
    );
  }, [load]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function onAsk(e: FormEvent) {
    e.preventDefault();
    if (!question.trim()) return;
    setBusy(true);
    setError(null);
    try {
      const result = await api.ask(params.chatId, question.trim());
      setMessages((prev) => [...prev, result.user_message, result.ai_message]);
      setTotal((t) => t + 2);
      setQuestion("");
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Ask failed");
    } finally {
      setBusy(false);
    }
  }

  async function onRename() {
    if (!chat) return;
    const next = window.prompt("New chat name", chat.name);
    if (!next || next.trim() === chat.name) return;
    try {
      const updated = await api.renameChat(chat.id, next.trim());
      setChat(updated);
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Rename failed");
    }
  }

  return (
    <div>
      <p className={styles.crumb}>
        <Link href="/workspaces">Workspaces</Link>
        {" / "}
        <Link href={`/workspaces/${params.workspaceId}`}>Workspace</Link>
        {" / "}
        Chat
      </p>

      <div className={styles.header}>
        <h1 className={styles.title}>{chat?.name || "Chat"}</h1>
        <button type="button" className="btn btnGhost" onClick={onRename}>
          Rename
        </button>
      </div>

      {error && <div className="error" style={{ marginBottom: "1rem" }}>{error}</div>}

      <div className="panel">
        <div className={styles.thread}>
          {messages.length === 0 && (
            <div className="empty">
              Ask a question about documents in this workspace.
            </div>
          )}
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`${styles.bubble} ${
                msg.author === "user" ? styles.user : styles.ai
              }`}
            >
              <div className={styles.author}>
                {msg.author === "user" ? "You" : "Assistant"}
              </div>
              <div>{msg.content}</div>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>

        <form className={styles.composer} onSubmit={onAsk}>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question…"
            required
          />
          <div className={styles.actions}>
            <span className="muted" style={{ fontSize: "0.85rem" }}>
              {messages.length} of {total} messages
            </span>
            <button className="btn btnPrimary" type="submit" disabled={busy}>
              {busy ? "Thinking…" : "Ask"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
