"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import type { Document } from "@/lib/types";
import { FILE_TYPE_LABELS } from "@/lib/types";
import styles from "./page.module.css";

export default function DocumentDetailPage() {
  const params = useParams<{ workspaceId: string; documentId: string }>();
  const router = useRouter();
  const [doc, setDoc] = useState<Document | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    const data = await api.getDocument(params.documentId);
    setDoc(data);
  }, [params.documentId]);

  useEffect(() => {
    load().catch((err) =>
      setError(err instanceof ApiError ? String(err.detail) : "Failed to load document"),
    );
  }, [load]);

  async function onDelete() {
    if (!doc || !window.confirm(`Delete “${doc.filename}”?`)) return;
    try {
      await api.deleteDocument(doc.id);
      router.replace(`/workspaces/${params.workspaceId}`);
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Delete failed");
    }
  }

  return (
    <div>
      <p className={styles.crumb}>
        <Link href="/workspaces">Workspaces</Link>
        {" / "}
        <Link href={`/workspaces/${params.workspaceId}`}>Workspace</Link>
        {" / "}
        Document
      </p>
      <h1 className={styles.title}>{doc?.filename || "Document"}</h1>
      {error && <div className="error" style={{ marginBottom: "1rem" }}>{error}</div>}

      {doc && (
        <div className="panel">
          <dl className={styles.meta}>
            <div className={styles.metaRow}>
              <dt>Filename</dt>
              <dd>{doc.filename}</dd>
            </div>
            <div className={styles.metaRow}>
              <dt>Type</dt>
              <dd>{FILE_TYPE_LABELS[doc.filetype]}</dd>
            </div>
            <div className={styles.metaRow}>
              <dt>Created</dt>
              <dd>{new Date(doc.created_at).toLocaleString()}</dd>
            </div>
            <div className={styles.metaRow}>
              <dt>Modified</dt>
              <dd>{new Date(doc.modified_at).toLocaleString()}</dd>
            </div>
          </dl>
          <div className={styles.actions}>
            <Link
              href={`/workspaces/${params.workspaceId}`}
              className="btn btnGhost"
            >
              Back
            </Link>
            <button type="button" className="btn btnDanger" onClick={onDelete}>
              Delete
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
