from pydantic import BaseModel
from typing import List, Optional, Literal
from enum import Enum
from datetime import datetime

class MaturityLevel(str, Enum):
    TODDLER = "toddler"       # Simple words, 3-5 pages
    INTERMEDIATE = "child"    # Full sentences, 5-8 pages
    YOUTH = "youth"           # Complex themes, 8-10 pages

class StatusLog(BaseModel):
    """Represents a single step in the process history"""
    stage: str           # e.g., "analyzing_narrative"
    message: str         # e.g., "Extracted themes: Friendship, Courage"
    progress: int        # 0-100
    timestamp: datetime  # When this step happened

class StoryInput(BaseModel):
    # If using text input mode
    prompt_text: Optional[str] = None
    theme: str = "Fun"
    maturity: MaturityLevel = MaturityLevel.TODDLER

class Page(BaseModel):
    page_number: int
    text_content: str
    image_url: Optional[str] = None 
    image_prompt: str 
    duration: Optional[float] = 5
    audio_url: Optional[str] = None 


class StoryStatus(str, Enum):
    QUEUED = "queued"
    ANALYZING = "analyzing_narrative"
    STORYBOARDING = "storyboarding"
    ILLUSTRATING = "illustrating"
    COMPLETED = "completed"
    FAILED = "failed"

class StoryResponse(BaseModel):
    id: str
    status: StoryStatus
    progress: int # 0 to 100
    current_stage_message: str
    creation_metadata: Optional[dict] = None
    status_history: Optional[List[StatusLog]] = None
    title: Optional[str] = None
    pages: List[Page] = []