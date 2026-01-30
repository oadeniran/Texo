import json
import os
from google.genai import types 
from llm_client import VertexAIClient
from database import update_status, save_story, get_story
from PROMPTS import get_narrative_analysis_system_prompt, get_storyboard_prompt
import math
from utils import upload_file_bytes
import concurrent.futures

# Initialize the client once
vertex_client = VertexAIClient()

def process_single_page_task(page_data, metadata={}) -> dict:
    """
    1. Generates Image
    2. Uploads to Azure
    3. Returns the Page Object with the URL
    """
    maturity = metadata.get("maturity", "toddler")
    story_id = metadata.get("story_id", "unknown")
    max_retries = 4
    attempt = 0
    current_prompt = page_data['image_prompt_description']
    failed_prompts = [] # Keep track of what didn't work
    
    final_image_url = None

    try:
        while attempt < max_retries:
            print(f"🎨 Page {page_data['page_number']} - Attempt {attempt + 1}/{max_retries}")
            
            # A. Try to Generate
            generated_result = vertex_client.generate_image(prompt=current_prompt, retries=1)

            if generated_result:
                # --- SUCCESS PATH ---
                print(f"✅ Success on Page {page_data['page_number']}")
                image_bytes = generated_result.image_bytes
                
                # Upload
                final_image_url = upload_file_bytes(
                    file_name=None,
                    file_bytes=image_bytes,
                    content_type="image/png"
                )
                
                # If we succeeded after a rewrite, update status to let user know we fixed it
                if attempt > 0:
                     update_status(
                        story_id, "illustrating", -1, 
                        f"✅ Fixed Page {page_data['page_number']} after {attempt} retries."
                    )
                break # Exit Loop

            else:
                # --- FAILURE PATH (Blocked) ---
                print(f"⚠️ Page {page_data['page_number']} blocked on Attempt {attempt + 1}")
                failed_prompts.append(current_prompt)
                attempt += 1
                
                if attempt < max_retries:
                    # Notify User
                    update_status(
                        story_id, "illustrating", -1,
                        f"⚠️ Safety block (Page {page_data['page_number']}). AI is rewriting prompt (Try {attempt}/{max_retries})..."
                    )
                    
                    # REWRITE WITH CONTEXT
                    # Pass the list of failed prompts so the AI avoids them
                    current_prompt = vertex_client._rewrite_prompt_for_safety(
                        page_data['image_prompt_description'], 
                        previous_failures=failed_prompts
                    )
                else:
                    print(f"❌ Page {page_data['page_number']} failed after max retries.")

        # B. Fallback if Loop ends without success
        if not final_image_url:
            print(f"⚠️ Using fallback image for Page {page_data['page_number']}")
            final_image_url = "https://placehold.co/1024x1024/EEE/31343C.png?text=Illustration+Unavailable&font=lora"

        return {
            "page_number": page_data['page_number'],
            "text_content": page_data['text_content'],
            "image_url": final_image_url,
            "image_prompt": current_prompt,
            "duration": estimate_reading_time(page_data['text_content'], maturity),
            "audio_url": None,
            "success": True
        }

    except Exception as e:
        print(f"Failed page {page_data['page_number']}: {e}")
        return {
            "page_number": page_data['page_number'],
            "text_content": page_data['text_content'],
            "image_url": "https://via.placeholder.com/512?text=Error", # Fallback
            "image_prompt": current_prompt,
            "success": False
        }

def estimate_reading_time(text: str, maturity: str) -> int:
    """
    Estimates reading time in seconds.
    Toddlers read slower (or parents read slower to them).
    """
    words = len(text.split())
    
    # Words per minute adjustments
    if maturity == "toddler":
        wpm = 100 
    else:
        wpm = 150
        
    # Minimum 4 seconds per page so it doesn't flash too fast
    seconds = math.ceil((words / wpm) * 60)
    return max(4, seconds)

def generate_story_task(story_id: str, input_data: dict, audio_file_bytes: bytes = None):
    """
    The Main Orchestrator Loop (Synchronous).
    """
    try:
        # --- STAGE 1: ANALYZING NARRATIVE ---
        update_status(story_id, "analyzing_narrative", 10, "Listening to story and extracting themes...")
        
        # Get Prompt from PROMPTS.py
        system_prompt_str = get_narrative_analysis_system_prompt(
            maturity=input_data['maturity'],
            theme=input_data['theme'],
            audio_type = True if audio_file_bytes else False
        )
        
        messages = []
        if audio_file_bytes:
            transcript = vertex_client.generate_content_with_audio(
                audio_bytes=audio_file_bytes,
                prompt="Transcribe the audio exactly."
            )
            user_content = f"{system_prompt_str}\n\nHere is the transcript:\n{transcript}"
            response_text = vertex_client.generate_content_with_audio(
                audio_bytes=audio_file_bytes,
                prompt=system_prompt_str
            )
        else:
            # Text Input
            user_content = f"{system_prompt_str}\n\nStory Concept: {input_data['prompt_text']}"
            messages.append({"role": "user", "content": user_content})

            # Call LLM (Force JSON output via prompt instructions + low temp)
            response_text = vertex_client.chat_completion(messages, temperature=0.4, model="gemini-3-pro-preview")

        if 'error' in response_text and type(response_text) == dict:
            raise Exception("LLM Generation Failed during Narrative Analysis")

        
        # Clean & Parse JSON
        clean_json = response_text.replace("```json", "").replace("```", "").strip()
        analysis = json.loads(clean_json)
        
        # Save Metadata
        story = get_story(story_id)
        story["title"] = analysis.get("title", "Untitled Story")
        story["creation_process_context"]["narrative_analysis"] = analysis
        save_story(story_id, story)

        # --- STAGE 2: STORYBOARDING ---
        update_status(story_id, "storyboarding", 30, "Splitting story into pages...")
        
        page_count = 5 if input_data['maturity'] == "toddler" else 8
        
        # Get Prompt from PROMPTS.py
        sb_prompt_str = get_storyboard_prompt(page_count, analysis)
        
        sb_response_text = vertex_client.chat_completion(
            [{"role": "user", "content": sb_prompt_str}], 
            temperature=0.7
        )
        if 'error' in sb_response_text and type(sb_response_text) == dict:
            raise Exception("LLM Generation Failed during Storyboarding")
        
        sb_clean_json = sb_response_text.replace("```json", "").replace("```", "").strip()
        pages_data = json.loads(sb_clean_json)
        print(f"Generated {len(pages_data)} pages.")
        print(pages_data[0])

        # --- STAGE 3: ILLUSTRATING ---
        update_status(story_id, "illustrating", 30, "Starting parallel image generation...")
        
        final_pages = []
        total_pages = len(pages_data)
        completed_count = 0
        
        # We use ThreadPoolExecutor to run tasks in parallel
        # Max workers = number of pages to go fast
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            
            # 1. Submit all tasks immediately
            future_to_page = {
                executor.submit(process_single_page_task, page, {"maturity": input_data['maturity'], "story_id": story_id}): page 
                for page in pages_data
            }
            
            # 2. Process them AS THEY FINISH (Main thread handles this loop)
            for future in concurrent.futures.as_completed(future_to_page):
                result = future.result()
                final_pages.append(result)
                
                # 3. Safe Status Update
                # Only this main thread updates the DB, so no race conditions.
                completed_count += 1
                progress = 30 + int((completed_count / total_pages) * 60)
                
                update_status(
                    story_id, 
                    "illustrating", 
                    progress, 
                    f"Finished page {completed_count} of {total_pages}..."
                )

        # 4. Re-sort pages (Important!)
        # Because they finish out of order (simple pages finish fast), we must sort them back.
        final_pages.sort(key=lambda x: x['page_number'])
        
        

        # --- FINISH ---
        story = get_story(story_id)
        story["pages"] = final_pages
        story["creation_process_context"]["storyboard_pages"] = pages_data
        save_story(story_id, story)
        update_status(story_id, "completed", 100, "Story ready!")

    except Exception as e:
        print(f"CRITICAL ERROR in orchestrator: {e}")
        import traceback
        traceback.print_exc()
        update_status(story_id, "failed", 0, f"Error: {str(e)}")