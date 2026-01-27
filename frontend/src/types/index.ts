export type MaturityLevel = 'toddler' | 'child' | 'youth';

export interface Page {
  page_number: number;
  text_content: string;
  image_url: string | null;
  image_prompt: string;
  duration: number; // in seconds
  audio_url: string | null;
}

export interface StatusLog {
  stage: string;
  message: string;
  progress: number;
  timestamp: string;
}

export interface Story {
  id: string;
  status: 'queued' | 'analyzing_narrative' | 'storyboarding' | 'illustrating' | 'completed' | 'failed';
  progress: number;
  current_stage_message: string;
  title: string | null;
  status_history: StatusLog[];
  pages: Page[];
  creation_metadata?: {
    theme: string;
    maturity: string;
    prompt_text?: string;
  };
}