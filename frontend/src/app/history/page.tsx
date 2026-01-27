"use client";
import { useEffect, useState } from 'react';
import Link from 'next/link';
import Navbar from '../../components/Navbar';
import { API_URL } from '../../lib/config';
import { Story } from '../../types';
import { Loader2, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import styles from './history.module.css';

export default function HistoryPage() {
  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch(`${API_URL}/api/history`);
        const data = await res.json();
        setStories(data);
      } catch (err) { console.error(err); } finally { setLoading(false); }
    };
    fetchHistory();
  }, []);

  return (
    <>
      <Navbar />
      <div className="container">
        <h1 style={{ marginBottom: '2rem' }}>Your Story Collection</h1>

        {loading ? (
          <div className={styles.emptyState}>
            <Loader2 className="spin" size={40} color="var(--primary)" />
          </div>
        ) : stories.length === 0 ? (
          <div className={styles.emptyState}>
            <p>No stories yet. Go create one!</p>
            <Link href="/" className="btn btnPrimary" style={{ marginTop: '1rem' }}>
              Create Story
            </Link>
          </div>
        ) : (
          <div className={styles.grid}>
            {stories.map((story) => (
              <Link href={`/story/${story.id}`} key={story.id} className={styles.cardLink}>
                <div className={`card ${styles.historyCard}`}>
                  <div className={styles.thumbnail}>
                    {story.pages?.[0]?.image_url ? (
                      <img src={story.pages[0].image_url} alt="Cover" className={styles.thumbImg} />
                    ) : (
                      <span style={{ fontSize: '3rem' }}>📖</span>
                    )}
                    <div className={`${styles.statusBadge} ${story.status === 'completed' ? styles.completed : story.status === 'failed' ? styles.failed : styles.processing}`}>
                      {story.status === 'completed' ? <CheckCircle size={14}/> : 
                       story.status === 'failed' ? <AlertCircle size={14}/> : <Clock size={14}/>}
                      {story.status}
                    </div>
                  </div>
                  <div className={styles.content}>
                    <h3 className={styles.title}>{story.title || "Untitled Story"}</h3>
                    <p className={styles.date}>
                      {new Date(story.status_history[0]?.timestamp || Date.now()).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </>
  );
}