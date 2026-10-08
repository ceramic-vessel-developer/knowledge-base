import Link from "next/link";
import styles from "./page.module.css";

export default function LandingPage() {
  return (
    <>
      <div className={styles.backdrop} aria-hidden />
      <section className={`container ${styles.hero}`}>
        <div>
          <h1 className={styles.brand}>Knowledge Workspace</h1>
          <p className={styles.lead}>
            Upload documents into private workspaces and ask grounded questions
            with retrieval-augmented chat.
          </p>
          <div className={styles.actions}>
            <Link href="/register" className="btn btnPrimary">
              Get started
            </Link>
            <Link href="/login" className="btn btnGhost">
              Log in
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}
