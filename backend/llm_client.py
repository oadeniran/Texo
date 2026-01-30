# backend/llm_client.py
import os
import logging
from google import genai
from google.genai import types
from PIL import Image
import time
import tempfile
from PROMPTS import get_image_generation_prompt_rewrite_system_prompt

logger = logging.getLogger("uvicorn")

class VertexAIClient:
    def __init__(self):
        # Initialize the new Gen AI Client
        self.client = genai.Client(http_options=types.HttpOptions(api_version="v1"))

    def chat_completion(self, messages: list[dict], model: str = "gemini-3-flash-preview", **kwargs) -> str:
        try:
            formatted_contents = []

            for msg in messages:
                role = msg["role"]
                raw_content = msg["content"]
                parts = []

                if isinstance(raw_content, list):
                    # Handle Mixed Content (Text + Audio/Image Parts)
                    for item in raw_content:
                        if isinstance(item, str):
                            parts.append(types.Part.from_text(text=item))
                        elif hasattr(item, "mime_type"): 
                            # If it's already a types.Part (audio/image) created in orchestrator
                            parts.append(item)
                        else:
                            # Fallback for unknown types, try to cast to string
                            parts.append(types.Part.from_text(text=str(item)))
                else:
                    # Simple String
                    parts.append(types.Part.from_text(text=str(raw_content)))

                formatted_contents.append(types.Content(role=role, parts=parts))

            response = self.client.models.generate_content(
                model=model,
                contents=formatted_contents,
                config=types.GenerateContentConfig(
                    temperature=kwargs.get("temperature", 0.7),
                    response_mime_type=kwargs.get("response_mime_type", "text/plain")
                )
            )
            
            return response.text

        except Exception as err:
            logger.exception(f"Error in LLM Client: {err}")
            # Return a fallback JSON to prevent the Orchestrator from crashing entirely
            return {"error": "LLM generation failed."}
    
    def _rewrite_prompt_for_safety(self, unsafe_prompt: str,previous_failures: list[str] = []) -> str:
        """
        Uses the LLM to intelligently rewrite a prompt that triggered safety filters.
        """
        system_instruction = get_image_generation_prompt_rewrite_system_prompt(previous_failures)
        
        try:
            response = self.chat_completion(
                messages=[
                    {"role": "user", "content": system_instruction},
                    {"role": "user", "content": "Original Prompt: " + unsafe_prompt}
                ],
                temperature=0.3 # Low temp for strict adherence
            )
            # Clean up response just in case
            return response.strip().replace("Prompt:", "").strip()
        except Exception as e:
            logger.error(f"Failed to rewrite prompt: {e}")
            # Fallback: simple age scrubber if LLM fails
            return unsafe_prompt.replace("year-old", "young").replace("child", "character")
    
    def generate_image(self, prompt: str, retries: int = 3) -> Image.Image | None:
        """
        Uses Imagen 3.0 with Retry Logic + Safety Filter Handling.
        Returns None if generation is blocked.
        """
        attempt = 0
        while attempt < retries:
            try:
                # 1. Configuration with Relaxed Safety
                # We ask it to only block "High" probability risks to avoid false positives on innocent prompts.
                config = types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="1:1",
                    safety_filter_level="block_only_high", 
                    person_generation="allow_adult"
                )

                response = self.client.models.generate_images(
                    model='imagen-3.0-generate-001',
                    prompt=prompt,
                    config=config
                )
                
                # 2. Safety Check: Did we actually get an image?
                if not response.generated_images:
                    logger.warning(f"⚠️ Image generation blocked by Safety Filters for prompt: {prompt[:50]}...")
                    # We return None instead of crashing. The Orchestrator will handle the fallback.
                    return None

                return response.generated_images[0].image

            except Exception as err:
                error_str = str(err).lower()
                
                # Retry on Quota (429) or Server Errors (500)
                if any(x in error_str for x in ["429", "quota", "resource exhausted", "503", "500"]):
                    attempt += 1
                    if attempt >= retries:
                        logger.error(f"❌ Max retries reached for image gen: {err}")
                        raise err
                    
                    wait_time = (2 * attempt) + 2
                    print(f"⚠️ Image Gen Rate Limit. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    # If it's a client error (400, 404), don't retry, just fail
                    logger.exception(f"Error in Image Gen: {err}")
                    return None
        return None
    
    def generate_content_with_audio(self, audio_bytes: bytes, prompt: str, mime_type: str = "audio/webm") -> str:
        """
        Sends audio bytes directly (Inline) to Vertex AI.
        Avoids 'files.upload' error and works perfectly for files < 20MB.
        """
        try:
            print(f"🎤 Sending {len(audio_bytes)} bytes inline to Gemini...")

            # 1. Create the Audio Part correctly
            # This wraps the raw bytes so Vertex knows it's media, not text.
            audio_part = types.Part.from_bytes(
                data=audio_bytes,
                mime_type=mime_type
            )

            # 2. Create the Text Part
            text_part = types.Part.from_text(text=prompt)

            # 3. Single "Super-Call"
            response = self.client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=[
                    types.Content(
                        role="user",
                        parts=[audio_part, text_part] # Order matters: Audio context first, then Prompt
                    )
                ]
            )
            
            return response.text

        except Exception as e:
            logger.error(f"Audio generation failed: {e}")
            raise e

    def execute_code(self, text_prompt: str) -> str:
        """
        Executes code using the Gemini Code Execution tool.
        """
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=text_prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(code_execution=types.ToolCodeExecution)],
                    temperature=0,
                ),
            )
            return response.text
        except Exception as err:
            logger.exception(f"Error in execute_code: {err}")
            return "Error executing code."
    
    def embed_text(self, text: str, model: str = "text-embedding-004") -> list[float]:
        """
        Converts text into a vector embedding.
        """
        try:
            # The new SDK syntax for embeddings
            response = self.client.models.embed_content(
                model=model,
                contents=text,
            )
            return response.embeddings[0].values
        except Exception as err:
            logger.exception(f"Error generating embedding: {err}")
            return []