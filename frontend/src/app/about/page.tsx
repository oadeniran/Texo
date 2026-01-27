import Navbar from '../../components/Navbar';
import styles from './about.module.css';

export default function AboutPage() {
  return (
    <>
      <Navbar />
      <div className={styles.container}>
        <div className={`card ${styles.card}`}>
          <h1 className={styles.title}>About Texo</h1>
          <p className={styles.description}>
            <strong>Texo</strong> (Latin for <em>"to weave"</em>) is an autonomous AI publisher designed to weave oral traditions and personal memories into tangible legacies.
          </p>
          <p className={styles.description}>
            Whether you are a parent/Teacher creating a custom social story for a neurodivergent child, or a grandchild preserving a family legend, Texo turns your voice into a fully illustrated book in seconds.
          </p>

          <hr className={styles.divider} />

          <h3 className={styles.sectionTitle}>The Agentic Workflow</h3>
          <ul className={styles.stepsList}>
            <li><strong>👂 1. Deep Listening:</strong> Texo uses Gemini 3 to "hear" your raw audio, capturing not just words, but tone and intent.</li>
            <li><strong>🧠 2. The Orchestrator:</strong> A reasoning agent creates a "Story Bible" to ensure plot coherence and visual consistency.</li>
            <li><strong>🛡️ 3. Self-Correction:</strong> If an illustration request hits a safety filter, Texo automatically rewrites the prompt to be safe while keeping the art style intact.</li>
            <li><strong>🎨 4. Production:</strong> Parallel workers generate high-fidelity illustrations using Imagen 3.</li>
          </ul>

          <h3 className={styles.sectionTitle}>Built With Gemini 3</h3>
          <div className={styles.tagContainer}>
            {['Gemini 3', 'Imagen 3', 'Vertex AI', 'Next.js', 'FastAPI'].map(tag => (
              <span key={tag} className={styles.tag}>
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}