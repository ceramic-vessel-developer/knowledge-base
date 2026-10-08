"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/context/AuthContext";

export function GuestOnly({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user) router.replace("/workspaces");
  }, [loading, user, router]);

  if (loading) {
    return (
      <div className="container" style={{ padding: "4rem 0" }}>
        <p className="muted">Loading…</p>
      </div>
    );
  }

  if (user) return null;
  return <>{children}</>;
}
