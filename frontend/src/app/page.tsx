"use client";
import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { Type, Mic as MicIcon } from 'lucide-react';
import Navbar from '../components/Navbar';
import VoiceRecorder from '../components/VoiceRecorder';
import { MaturityLevel } from '../types';
import { API_URL } from '../lib/config';
import styles from './page.module.css';

const THEMES = [
  "Adventure", "Animals", "Bedtime Story", "Bravery", "Circus", 
  "Courage", "Dinosaurs", "Discovery", "Education", "Fairy Tale", 
  "Family", "Fantasy", "Folklore", "Friendship", "Funny", 
  "History", "Holidays", "Kindness", "Magic", "Monsters", 
  "Morals", "Mystery", "Nature", "Ocean", "Pirates", 
  "Princesses", "Robots", "School", "Sci-Fi", "Space", 
  "Sports", "Superheroes", "Travel", "Underwater"
];

export default function CreateStory() {
  const router = useRouter();
  const [mode, setMode] = useState<'audio' | 'text'>('audio');
  const [loading, setLoading] = useState<boolean>(false);
  const [theme, setTheme] = useState<string>('Fantasy');
  const [maturity, setMaturity] = useState<MaturityLevel>('toddler');
  const [textPrompt, setTextPrompt] = useState<string>('');
  const [audioFile, setAudioFile] = useState<Blob | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('theme', theme);
      formData.append('maturity', maturity);

      let url = '';
      let options: RequestInit = {}; 
      
      if (mode === 'audio') {
        if (!audioFile) return alert("Please record a story first!");
        formData.append('file', audioFile, 'story.webm');
        url = `${API_URL}/api/create/audio`; 
        options = { method: 'POST', body: formData };
      } else {
        if (!textPrompt) return alert("Please write a story concept!");
        url = `${API_URL}/api/create/text`;
        options = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt_text: textPrompt, theme, maturity })
        };
      }

      const response = await fetch(url, options);
      if (!response.ok) throw new Error('API Failed');
      const data = await response.json();
      router.push(`/story/${data.id}`);
    } catch (err) {
      console.error(err);
      alert("Failed to start story agent.");
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <div className="container">
        <div className={`card ${styles.card}`}>
          <div className={styles.modeSwitch}>
            <button 
              type="button"
              className={`btn ${mode === 'audio' ? 'btnPrimary' : 'btnSecondary'}`}
              onClick={() => setMode('audio')}
            >
              <MicIcon size={18} /> Voice Mode
            </button>
            <button 
              type="button"
              className={`btn ${mode === 'text' ? 'btnPrimary' : 'btnSecondary'}`}
              onClick={() => setMode('text')}
            >
              <Type size={18} /> Text Mode
            </button>
          </div>

          <form onSubmit={handleSubmit}>
            <div className={styles.inputArea}>
              {mode === 'audio' ? (
                <VoiceRecorder onAudioReady={setAudioFile} />
              ) : (
                <div className={styles.inputGroup}>
                  <label>What is your story about?</label>
                  <textarea 
                    className={styles.inputControl} 
                    rows={5} 
                    placeholder="Once upon a time, a little robot named Beep..."
                    value={textPrompt}
                    onChange={(e) => setTextPrompt(e.target.value)}
                  />
                </div>
              )}
            </div>

            <hr className={styles.divider} />

            <div className={styles.metadataGrid}>
              <div className={styles.inputGroup}>
                
                <label className={styles.labelShiny}>✨ Theme / Lesson</label>
                <input 
                  className={styles.inputControl} 
                  value={theme}
                  onChange={(e) => setTheme(e.target.value)}
                  placeholder="Type or select a theme..."
                  list="theme-options" // Connects to the datalist below
                />
                <datalist id="theme-options">
                  {THEMES.map(t => <option key={t} value={t} />)}
                </datalist>
              </div>
              <div className={styles.inputGroup}>
                
                <label className={styles.labelShiny}>👶 Target Audience</label>
                <select 
                  className={styles.inputControl}
                  value={maturity}
                  onChange={(e) => setMaturity(e.target.value as MaturityLevel)}
                >
                  <option value="toddler">Toddler (Simple words)</option>
                  <option value="child">Child (Full story)</option>
                  <option value="youth">Youth (Complex themes)</option>
                </select>
              </div>
            </div>

            <button 
              type="submit" 
              className={`btn btnPrimary ${styles.submitBtn}`}
              disabled={loading}
            >
              {loading ? (
                <>Texo is Weaving...</> 
              ) : (
                <>✨ Create My Story</>
              )}
            </button>
          </form>
        </div>
      </div>
    </>
  );
}