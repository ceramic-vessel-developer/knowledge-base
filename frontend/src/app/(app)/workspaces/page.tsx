"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { Workspace } from "@/lib/types";
import styles from "./page.module.css";

export default function WorkspacesPage() {
  const [items, setItems] = useState<Workspace[]>([]);
  const [total, setTotal] = useState(0);
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    const data = await api.listWorkspaces(0, 100);
    setItems(data.items);
    setTotal(data.total);
  }, []);

  useEffect(() => {
    load().catch((err) =>
      setError(err instanceof ApiError ? String(err.detail) : "Failed to load"),
    );
  }, [load]);

  async function onCreate(e: FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setBusy(true);
    setError(null);
    try {
      await api.createWorkspace(name.trim());
      setName("");
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Create failed");
    } finally {
      setBusy(false);
    }
  }

  async function onRename(ws: Workspace) {
    const next = window.prompt("New workspace name", ws.name);
    if (!next || next.trim() === ws.name) return;
    try {
      await api.renameWorkspace(ws.id, next.trim());
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Rename failed");
    }
  }

  async function onDelete(ws: Workspace) {
    if (!window.confirm(`Delete workspace “${ws.name}”?`)) return;
    try {
      await api.deleteWorkspace(ws.id);
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Delete failed");
    }
  }

  return (
    <div>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Workspaces</h1>
          <p className="muted">Your private spaces for documents and chats.</p>
        </div>
        <form className={styles.create} onSubmit={onCreate}>
          <input
            placeholder="New workspace name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <button className="btn btnPrimary" type="submit" disabled={busy}>
            Create
          </button>
        </form>
      </div>

      {error && <div className="error" style={{ marginBottom: "1rem" }}>{error}</div>}

      <div className="panel">
        <div className="list">
          {items.length === 0 && (
            <div className="empty">No workspaces yet. Create one above.</div>
          )}
          {items.map((ws) => (
            <div key={ws.id} className="listRow">
              <div>
                <Link href={`/workspaces/${ws.id}`}>
                  <strong>{ws.name}</strong>
                </Link>
                <div className={styles.meta}>
                  {ws.type} · updated {new Date(ws.modified_at).toLocaleString()}
                </div>
              </div>
              <div className="rowActions">
                <button type="button" className="btn btnGhost" onClick={() => onRename(ws)}>
                  Rename
                </button>
                <button type="button" className="btn btnDanger" onClick={() => onDelete(ws)}>
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
        <p className={styles.meta} style={{ marginTop: "0.85rem" }}>
          Showing {items.length} of {total}
        </p>
      </div>
    </div>
  );
}
