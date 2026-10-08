"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { GuestOnly } from "@/components/GuestOnly";
import { useAuth } from "@/context/AuthContext";
import { ApiError } from "@/lib/api";
import styles from "../auth.module.css";

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await register(username, email, password);
      router.replace("/workspaces");
    } catch (err) {
      setError(
        err instanceof ApiError
          ? String(err.detail)
          : "Could not create account.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <GuestOnly>
      <div className={styles.wrap}>
        <div className={`panel ${styles.card}`}>
          <h1 className={styles.brand}>Knowledge Workspace</h1>
          <p className="muted">Create an account to start uploading documents.</p>
          <form className={styles.form} onSubmit={onSubmit}>
            {error && <div className="error">{error}</div>}
            <div className="field">
              <label htmlFor="username">Username</label>
              <input
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                autoComplete="username"
              />
            </div>
            <div className="field">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </div>
            <div className="field">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                autoComplete="new-password"
              />
            </div>
            <button className="btn btnPrimary" type="submit" disabled={busy}>
              {busy ? "Creating…" : "Register"}
            </button>
          </form>
          <p className={styles.footer}>
            Already have an account? <Link href="/login">Log in</Link>
          </p>
        </div>
      </div>
    </GuestOnly>
  );
}
