"use client";

import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import styles from "./AppShell.module.css";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();

  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <div className={`container ${styles.headerInner}`}>
          <Link href="/workspaces" className={styles.brand}>
            Knowledge Workspace
          </Link>
          <nav className={styles.nav}>
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
