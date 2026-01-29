"use client";
import { useEffect, useState, use } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Loader2, Play, Pause, ArrowLeft, ArrowRight, Home, Brain, X, CheckCircle, AlertCircle ,
  Sparkles, Baby, GraduationCap, User, Mic, Type
} from 'lucide-react';
import { Story, Page } from '../../../types';
import { API_URL } from '../../../lib/config';
import Navbar from '../../../components/Navbar';
import styles from './story.module.css';
import { motion, AnimatePresence } from 'framer-motion';


const transitions = {
  slide: {
    initial: { x: 50, opacity: 0 },
    animate: { x: 0, opacity: 1 },
    exit: { x: -50, opacity: 0 }
  },
  fade: {
    initial: { opacity: 0, scale: 0.98 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 1.02 }
  },
  zoom: {
    initial: { scale: 0.8, opacity: 0 },
    animate: { scale: 1, opacity: 1 },
    exit: { scale: 1.2, opacity: 0 }
  },
  flip: {
    initial: { rotateY: 90, opacity: 0 },
    animate: { rotateY: 0, opacity: 1 },
    exit: { rotateY: -90, opacity: 0 }
  }
};

const transitionKeys = Object.keys(transitions) as Array<keyof typeof transitions>;

export default function StoryViewer({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params); 
  const router = useRouter();
  const [story, setStory] = useState<Story | null>(null);
  const [currentPageIndex, setCurrentPageIndex] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  
  const [showLogs, setShowLogs] = useState<boolean>(false);

  const [currentAnim, setCurrentAnim] = useState<keyof typeof transitions>('fade');

  const [progress, setProgress] = useState(0); // 0 to 100%
  const [duration, setDuration] = useState(5000); // milliseconds
  const [timeLeftOnPage, setTimeLeftOnPage] = useState(5); // seconds

  const isAudioInput = story?.creation_metadata?.prompt_text === "Audio Input";

  const getMaturityIcon = (level?: string) => {
    switch(level) {
      case 'toddler': return <Baby size={14} />;
      case 'child': return <User size={14} />;
      case 'youth': return <GraduationCap size={14} />;
      default: return <User size={14} />;
    }
  };

  const getPageDuration = (text: string) => {
    const wordCount = text.split(' ').length;
    // Minimum 5 seconds, or 0.4 seconds per word
    return Math.max(5000, wordCount * 400); 
  };

  const changePage = (direction: 'next' | 'prev') => {
    if (!story) return;

    // A. Pick Random Animation
    const randomKey = transitionKeys[Math.floor(Math.random() * transitionKeys.length)];
    setCurrentAnim(randomKey);

    // B. Update Index
    if (direction === 'next') {
      if (currentPageIndex < story.pages.length - 1) {
        setCurrentPageIndex(prev => prev + 1);
      } else {
        setIsPlaying(false); // Stop at end
      }
    } else {
      if (currentPageIndex > 0) {
        setCurrentPageIndex(prev => prev - 1);
      }
    }
  };

  const renderLogEntry = (log: any, index: number, totalLogs: number, status: string) => {
    // Logic: 
    // If status is NOT completed/failed, the *latest* log (index 0 in reversed list) is "In Progress"
    // All others are "Done"
    
    const isLatest = index === 0;
    const isProcessing = status !== 'completed' && status !== 'failed';
    const isError = status === 'failed' && isLatest;

    return (
      <div key={index} className={styles.logEntry}>
        <div style={{ minWidth: '24px', display: 'flex', alignItems: 'center' }}>
          {isError ? (
            <AlertCircle size={16} color="red" />
          ) : isProcessing && isLatest ? (
            <Loader2 size={16} className="spin" color="var(--primary)" />
          ) : (
            <CheckCircle size={16} color="green" />
          )}
        </div>
        
        <span className={styles.logTime}>
          {new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
        </span>
        <span style={{ fontWeight: isProcessing && isLatest ? 'bold' : 'normal', color: isProcessing && isLatest ? 'var(--primary)' : 'inherit' }}>
          {log.message}
        </span>
      </div>
    );
  };

  useEffect(() => {
    let intervalId: NodeJS.Timeout;
    const fetchStatus = async () => {
      try {
        const res = await fetch(`${API_URL}/api/story/${id}`);
        const data: Story = await res.json();
        setStory(data);
        if (data.status === 'completed' || data.status === 'failed') {
          clearInterval(intervalId);
          if (data.status === 'completed' && !isPlaying) {
             // Only auto-play if we haven't started yet
             setIsPlaying(true);
             setTimeLeftOnPage(data.pages[0]?.duration || 5);
          }
        }
      } catch (err) { console.error(err); }
    };
    fetchStatus();
    intervalId = setInterval(fetchStatus, 2000);
    return () => clearInterval(intervalId);
  }, [id]);

  useEffect(() => {
    if (story) {
      const text = story.pages[currentPageIndex]?.text_content || "";
      setDuration(getPageDuration(text));
      setProgress(0);
    }
  }, [currentPageIndex, story]);

  useEffect(() => {
    let timer: NodeJS.Timeout;

    if (isPlaying && story && progress < 100) {
      // Update every 100ms for smooth UI
      const interval = 100; 
      
      timer = setInterval(() => {
        setProgress((prev) => {
          const nextProgress = prev + (interval / duration) * 100;
          
          // If finished, Trigger Next Page
          if (nextProgress >= 100) {
            changePage('next');
            return 0;
          }
          return nextProgress;
        });
      }, interval);
    }

    return () => clearInterval(timer);
  }, [isPlaying, progress, duration, story]);

  // LOADING STATE
  if (!story || story.status !== 'completed') {
    return (
      <>
        <Navbar />
        <div className={`card ${styles.loaderCard}`}>
          <Loader2 className="spin" size={48} color="var(--primary)" style={{ margin: '0 auto 1rem' }} />
          <h2>Creating Your Masterpiece...</h2>
          <p className={styles.loaderText}>{story?.current_stage_message || "Connecting to agent..."}</p>
          
          <div className={styles.progressContainer}>
            <div className={styles.progressBar} style={{ width: `${story?.progress || 0}%` }} />
          </div>

          <div className={styles.timeline}>
            <h4 style={{ marginTop: 0 }}>Agent Activity Log</h4>
            {story?.status_history?.slice().reverse().map((log, i) => 
              renderLogEntry(log, i, story.status_history.length, story.status)
            )}
          </div>
        </div>
      </>
    );
  }

  // VIEWER STATE
  const currentPage: Page = story.pages[currentPageIndex];

  return (
    <>
      <Navbar />
      <div className={`container ${styles.viewerContainer}`}>
        
        <div className={styles.header}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', width: '100%' }}>
            
            {/* Title Row */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <button onClick={() => router.push('/')} className="btn btnSecondary" style={{ padding: '8px 12px' }}>
                <Home size={16} />
              </button>
              <h2 style={{ margin: 0 }}>{story.title || "Untitled Story"}</h2>
            </div>

            {/* Metadata Badges Row */}
            {story.creation_metadata && (
              <div className={styles.metaContainer}>
                
                {/* Theme Badge */}
                <span className={`${styles.metaBadge} ${styles.badgeTheme}`}>
                  <Sparkles size={12} />
                  {story.creation_metadata.theme}
                </span>

                {/* Maturity Badge */}
                <span className={`${styles.metaBadge} ${styles.badgeMaturity}`}>
                  {getMaturityIcon(story.creation_metadata.maturity)}
                  {story.creation_metadata.maturity} Level
                </span>

                {/* Input Mode Badge */}
                <span className={`${styles.metaBadge} ${styles.badgeMode}`}>
                  {isAudioInput ? <Mic size={12} /> : <Type size={12} />}
                  {isAudioInput ? "Voice Story" : "Text Prompt"}
                </span>

              </div>
            )}
          </div>

          {/* Right Side: Thinking Button */}
          <button onClick={() => setShowLogs(true)} className={styles.thinkingBtn}>
            <Brain size={18} /> View Thoughts
          </button>
        </div>

        {/* BOOK FRAME */}
        <div className={styles.bookFrame}>
          <AnimatePresence mode="wait">
            <motion.div
              key={currentPageIndex} 
              variants={transitions[currentAnim]} 
              initial="initial"
              animate="animate"
              exit="exit"
              transition={{ duration: 0.5, ease: "easeInOut" }} 
              style={{ width: '100%', display: 'flex', flexDirection: 'column', flex: 1 }}
            >
              <div className={styles.imageLayer}>
                {currentPage?.image_url ? (
                  <img src={currentPage.image_url} alt="Story Art" className={styles.storyImage} />
                ) : (
                  <div className="spin" style={{ color: '#ccc' }}>Generating Art...</div>
                )}
              </div>

              <div className={styles.textOverlay}>
                <p>{currentPage?.text_content || "Writing story..."}</p>
              </div>
            </motion.div>
          </AnimatePresence>

          {/* TIMER BAR */}
          {isPlaying && (
            <div style={{ height: '6px', background: '#e36565', width: '100%' }}>
               <div 
                 style={{ 
                   height: '100%', 
                   background: 'var(--secondary)', 
                   width: `${progress}%`, 
                   transition: 'width 0.1s linear'
                 }}
               />
            </div>
          )}
        </div>

        {/* CONTROLS */}
        <div className={styles.controls}>
          <button 
            onClick={() => { setIsPlaying(false); changePage('prev'); }} 
            disabled={currentPageIndex === 0}
            className="btn btnSecondary"
          >
            <ArrowLeft size={20} /> Prev
          </button>

          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <span style={{ fontWeight: 600, color: '#888' }}>
              Page {currentPageIndex + 1} of {story.pages.length}
            </span>
            
            <button 
              className={`btn btnPrimary ${styles.playBtn}`}
              onClick={() => setIsPlaying(!isPlaying)}
              style={{ borderRadius: '50%', width: '50px', height: '50px', padding: 0 }}
            >
              {isPlaying ? <Pause fill="white" size={20} /> : <Play fill="white" size={20} style={{ marginLeft: '4px' }} />}
            </button>
          </div>

          <button 
            onClick={() => { setIsPlaying(false); changePage('next'); }} 
            disabled={currentPageIndex === story.pages.length - 1}
            className="btn btnSecondary"
          >
            Next <ArrowRight size={20} />
          </button>
        </div>
      </div>

      {/* Thinking Modal */}
      {showLogs && (
        <div className={styles.modalOverlay} onClick={() => setShowLogs(false)}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h3><Brain color="var(--primary)" /> Agent Thought Process</h3>
              <button className={styles.closeBtn} onClick={() => setShowLogs(false)}>
                <X size={24} />
              </button>
            </div>
            <div className={styles.modalBody}>
              <div className={styles.timeline} style={{ border: 'none', maxHeight: 'none' }}>
                 {story?.status_history?.slice().reverse().map((log, i) => 
                   renderLogEntry(log, i, story.status_history.length, story.status)
                 )}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}