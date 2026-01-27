"use client";
import { useState, useRef } from 'react';
import { Mic, Square, Trash2 } from 'lucide-react';
import styles from './VoiceRecorder.module.css';

interface VoiceRecorderProps {
  onAudioReady: (blob: Blob | null) => void;
}

export default function VoiceRecorder({ onAudioReady }: VoiceRecorderProps) {
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setAudioBlob(blob);
        onAudioReady(blob);
        stream.getTracks().forEach(track => track.stop());
      };

      recorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error(err);
      alert("Microphone access denied! Check browser permissions.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const reset = () => {
    setAudioBlob(null);
    onAudioReady(null);
  };

  return (
    <div className={styles.container}>
      {!audioBlob ? (
        !isRecording ? (
          <button type="button" onClick={startRecording} className={`btn btnPrimary ${styles.micBtn}`}>
            <Mic /> Tap to Narrate Story
          </button>
        ) : (
          <button type="button" onClick={stopRecording} className={`btn ${styles.stopBtn}`}>
            <Square /> Stop Recording...
          </button>
        )
      ) : (
        <div className={styles.playback}>
          <audio controls src={URL.createObjectURL(audioBlob)} className={styles.audioPlayer} />
          <button type="button" onClick={reset} className={`btn btnSecondary ${styles.deleteBtn}`}>
            <Trash2 size={16} />
          </button>
        </div>
      )}
    </div>
  );
}