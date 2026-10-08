"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import type { Chat, Document, FileType, Workspace } from "@/lib/types";
import { FILE_TYPE_LABELS } from "@/lib/types";
import styles from "./page.module.css";

function inferFileType(file: File): FileType {
  const name = file.name.toLowerCase();
  if (name.endsWith(".pdf") || file.type === "application/pdf") return 1;
  if (name.endsWith(".txt") || file.type.startsWith("text/")) return 2;
  return 3;
}

export default function WorkspaceDetailPage() {
  const params = useParams<{ workspaceId: string }>();
  const workspaceId = params.workspaceId;
  const router = useRouter();

  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [chats, setChats] = useState<Chat[]>([]);
  const [docTotal, setDocTotal] = useState(0);
  const [chatTotal, setChatTotal] = useState(0);
  const [chatName, setChatName] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    const [ws, docs, chatList] = await Promise.all([
      api.getWorkspace(workspaceId),
      api.listDocuments(workspaceId, 0, 100),
      api.listChats(workspaceId, 0, 100),
    ]);
    setWorkspace(ws);
    setDocuments(docs.items);
    setDocTotal(docs.total);
    setChats(chatList.items);
    setChatTotal(chatList.total);
  }, [workspaceId]);

  useEffect(() => {
    load().catch((err) =>
      setError(err instanceof ApiError ? String(err.detail) : "Failed to load workspace"),
    );
  }, [load]);

  async function onUpload(e: FormEvent) {
    e.preventDefault();
    if (!file) return;
    setBusy(true);
    setError(null);
    try {
      await api.uploadDocument({
        filename: file.name,
        filetype: inferFileType(file),
        workspaceId,
        file,
      });
      setFile(null);
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  async function onDeleteDoc(doc: Document) {
    if (!window.confirm(`Delete “${doc.filename}”?`)) return;
    try {
      await api.deleteDocument(doc.id);
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Delete failed");
    }
  }

  async function onCreateChat(e: FormEvent) {
    e.preventDefault();
    if (!chatName.trim()) return;
    setBusy(true);
    setError(null);
    try {
      const chat = await api.createChat(chatName.trim(), workspaceId);
      setChatName("");
      router.push(`/workspaces/${workspaceId}/chats/${chat.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Create chat failed");
      setBusy(false);
    }
  }

  async function onRenameChat(chat: Chat) {
    const next = window.prompt("New chat name", chat.name);
    if (!next || next.trim() === chat.name) return;
    try {
      await api.renameChat(chat.id, next.trim());
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Rename failed");
    }
  }

  async function onDeleteChat(chat: Chat) {
    if (!window.confirm(`Delete chat “${chat.name}”?`)) return;
    try {
      await api.deleteChat(chat.id);
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Delete failed");
    }
  }

  return (
    <div>
      <p className={styles.crumb}>
        <Link href="/workspaces">Workspaces</Link> / {workspace?.name || "…"}
      </p>
      <h1 className={styles.title}>{workspace?.name || "Workspace"}</h1>
      {error && <div className="error" style={{ marginBottom: "1rem" }}>{error}</div>}

      <div className={styles.grid}>
        <section className="panel">
          <h2 className="panelTitle">Documents</h2>
          <form className={styles.toolbar} onSubmit={onUpload}>
            <input
              type="file"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              required
            />
            <button className="btn btnPrimary" type="submit" disabled={busy || !file}>
              Upload
            </button>
          </form>
          <div className="list">
            {documents.length === 0 && (
              <div className="empty">No documents yet. Upload a TXT or PDF.</div>
            )}
            {documents.map((doc) => (
              <div key={doc.id} className="listRow">
                <div>
                  <Link href={`/workspaces/${workspaceId}/documents/${doc.id}`}>
                    <strong>{doc.filename}</strong>
                  </Link>
                  <div className={styles.meta}>
                    {FILE_TYPE_LABELS[doc.filetype]} ·{" "}
                    {new Date(doc.created_at).toLocaleString()}
                  </div>
                </div>
                <div className="rowActions">
                  <button
                    type="button"
                    className="btn btnDanger"
                    onClick={() => onDeleteDoc(doc)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
          <p className={styles.meta} style={{ marginTop: "0.75rem" }}>
            {documents.length} of {docTotal}
          </p>
        </section>

        <section className="panel">
          <h2 className="panelTitle">Chats</h2>
          <form className={styles.toolbar} onSubmit={onCreateChat}>
            <input
              type="text"
              placeholder="New chat name"
              value={chatName}
              onChange={(e) => setChatName(e.target.value)}
              required
            />
            <button className="btn btnPrimary" type="submit" disabled={busy}>
              Create chat
            </button>
          </form>
          <div className="list">
            {chats.length === 0 && (
              <div className="empty">No chats yet. Create one to ask questions.</div>
            )}
            {chats.map((chat) => (
              <div key={chat.id} className="listRow">
                <div>
                  <Link href={`/workspaces/${workspaceId}/chats/${chat.id}`}>
                    <strong>{chat.name}</strong>
                  </Link>
                  <div className={styles.meta}>
                    {new Date(chat.created_at).toLocaleString()}
                  </div>
                </div>
                <div className="rowActions">
                  <button
                    type="button"
                    className="btn btnGhost"
                    onClick={() => onRenameChat(chat)}
                  >
                    Rename
                  </button>
                  <button
                    type="button"
                    className="btn btnDanger"
                    onClick={() => onDeleteChat(chat)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
          <p className={styles.meta} style={{ marginTop: "0.75rem" }}>
            {chats.length} of {chatTotal}
          </p>
        </section>
      </div>
    </div>
  );
}
