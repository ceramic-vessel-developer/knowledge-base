"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import styles from "./AppShell.module.css";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();
  const [healthOk, setHealthOk] = useState<boolean | null>(null);

  useEffect(() => {
    api
      .health()
      .then((h) => setHealthOk(h.status === "ok"))
      .catch(() => setHealthOk(false));
  }, []);

  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <div className={`container ${styles.headerInner}`}>
          <Link href="/workspaces" className={styles.brand}>
            Knowledge Workspace
          </Link>
          <nav className={styles.nav}>
            {healthOk !== null && (
              <span
                className={`${styles.health} ${
                  healthOk ? styles.healthOk : styles.healthBad
                }`}
              >
                {healthOk ? "API ok" : "API issue"}
              </span>
            )}
            <Link href="/workspaces">Workspaces</Link>
            {user && <span className={styles.user}>{user.username}</span>}
            <button type="button" className="btn btnGhost" onClick={logout}>
              Log out
            </button>
          </nav>
        </div>
      </header>
      <main className={`container ${styles.main}`}>{children}</main>
    </div>
  );
}
