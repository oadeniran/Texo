from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
import uuid
from init_env import ENVIRONMENT

from models import StoryInput, StoryResponse, StoryStatus
from database import save_story, get_story, get_all_stories
from orchestrator import generate_story_task
from utils import upload_file_bytes

app = FastAPI(title="Gemini Storyteller Agent",
              description="An API to generate children's stories using Gemini LLMs.",
              version="1.0.0",
              docs_url="/api/docs",)

# Enable CORS for Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/create/text", response_model=StoryResponse)
async def create_story_text(input_data: StoryInput, background_tasks: BackgroundTasks):
    story_id = str(uuid.uuid4())
    
    # Initialize DB entry
    new_story = {
        "id": story_id,
        "creation_metadata": input_data.dict(),
        "status": StoryStatus.QUEUED,
        "progress": 0,
        "current_stage_message": "Queued...",
        "creation_process_context": {},
        "pages": []
    }
    save_story(story_id, new_story)
    
    # Start Agent in Background
    background_tasks.add_task(generate_story_task, story_id, input_data.dict(), None)
    
    return new_story

@app.post("/api/create/audio", response_model=StoryResponse)
async def create_story_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    theme: str = Form("Fun"),
    maturity: str = Form("toddler")
):
    story_id = str(uuid.uuid4())
    
    # Read audio bytes
    audio_bytes = await file.read()

    audio_url = upload_file_bytes(
        file_name=None,
        file_bytes=audio_bytes,
        content_type=file.content_type
    )

    # DEBUG: Print size to confirm we actually got data
    print(f"🎤 Received Audio File: {len(audio_bytes)} bytes") 
    
    if len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail="Audio file is empty")
    
    input_data = {
        "theme": theme,
        "maturity": maturity,
        "prompt_text": "Audio Input",
        "audio_url": audio_url
    }

    new_story = {
        "id": story_id,
        "status": StoryStatus.QUEUED,
        "creation_metadata": input_data,
        "progress": 0,
        "current_stage_message": "Processing audio...",
        "creation_process_context": {},
        "pages": []
    }
    save_story(story_id, new_story)
    
    # Start Agent
    background_tasks.add_task(generate_story_task, story_id, input_data, audio_bytes)
    
    return new_story

@app.get("/api/story/{story_id}", response_model=StoryResponse)
async def get_story_status(story_id: str):
    story = get_story(story_id)
    if not story:
        return {"id": story_id, "status": "failed", "progress": 0, "current_stage_message": "Not found", "pages": []}
    if 'creation_process_context' in story:
        del story['creation_process_context']
    return story

@app.get("/api/history")
async def get_history():
    # Convert dict to list
    return get_all_stories()

if __name__ == "__main__":
    import uvicorn
    if ENVIRONMENT == "development":
        # Start in reload mode
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    else:
        uvicorn.run("main:app", host="0.0.0.0", port=8000)