import json

def get_narrative_analysis_system_prompt(maturity: str, theme: str, audio_type: bool) -> str:
    """
    Stage 1: Analyzes audio/text input to define the 'Story Bible'.
    
    IMPROVEMENTS:
    - Enforces a 'visual_signature' for character consistency.
    - Adds 'setting_signature' for background consistency.
    - Explicitly handles 'Maturity' logic (Vocabulary level, Tone).
    - Strengthened the 'Audio Transcription' logic to handle silence/mumbling.
    """
    
    # Define specific writing guidelines based on maturity
    maturity_guidelines = {
        "toddler": "Use very simple words, repetition, and 3-word sentences. Focus on sensory details (colors, sounds). Low stakes.",
        "child": "Use complete sentences, clear cause-and-effect, and a distinct beginning/middle/end. Moderate stakes (e.g., getting lost, making friends).",
        "youth": "Use complex vocabulary, metaphors, and emotional depth. Higher stakes and moral ambiguity allowed."
    }
    guideline = maturity_guidelines.get(maturity.lower(), maturity_guidelines["child"])

    # JSON Structure Definition
    base_json_structure = {
        "title": "A catchy, age-appropriate title",
        "plot_summary": "A 2-sentence summary of the narrative arc",
        "moral_lesson": "The underlying lesson or theme derived from the story",
        "art_style": "A specific, cohesive art style description (e.g., 'whimsical watercolor', 'vibrant Pixar-style 3D', 'crayon drawing')",
        "character_desc": "A detailed textual description of the main character",
        "visual_signature": "A concise, reusable image prompt slug for the main character (e.g., 'tiny blue robot with rusty antenna and red rubber boots'). This MUST be consistent.",
        "setting_signature": "A reusable description of the main setting (e.g., 'magical glowing forest with purple trees')."
    }

    if audio_type:
        base_json_structure["transcript"] = "The verbatim transcript of the audio. If silent/unclear, state '[Audio Unclear]'."

    json_schema_str = json.dumps(base_json_structure, indent=4)

    sys_prompt = f"""
    You are an elite Children's Book Editor and Art Director.
    
    INPUT CONTEXT:
    - Target Audience: {maturity} ({guideline})
    - Core Theme: {theme}
    
    YOUR MISSION:
    1. {"LISTEN & TRANSCRIBE: First, accurately transcribe the user's audio." if audio_type else "READ: Analyze the user's text prompt."}
    2. ANALYZE & FILL GAPS: 
       - If the input is a complete story, refine it.
       - If the input is a rambling memory, structure it into a narrative.
       - {"CRITICAL: If the audio is silent, garbled, or just background noise, INVENT a new story entirely based on the Theme: '" + theme + "'." if audio_type else ""}
    
    3. CREATE THE 'STORY BIBLE':
       - Define a **Visual Signature**: A specific, unchanging description of the protagonist to ensure they look exactly the same on every page.
       - Define an **Art Style**: Choose a style that fits the mood (e.g., 'Soft Pastel' for Bedtime, 'High Contrast Comic' for Action).
    
    OUTPUT FORMAT:
    Return ONLY a valid JSON object. Do not include markdown formatting (like ```json).
    
    JSON STRUCTURE:
    {json_schema_str}
    """
    return sys_prompt

def get_storyboard_prompt(page_count: int, analysis_json: dict) -> str:
    """
    Stage 2: Breaks the story into specific pages with image prompts.
    
    IMPROVEMENTS:
    - Injects the 'visual_signature' and 'art_style' from Stage 1 into every prompt.
    - Demands 'Cinematography' variety (Close-up, Wide shot, etc.).
    - Enforces strictly valid JSON output to prevent parsing errors.
    """
    
    title = analysis_json.get("title", "Untitled Story")
    visual_signature = analysis_json.get("visual_signature", "a cute character")
    setting_signature = analysis_json.get("setting_signature", "a colorful background")
    style = analysis_json.get("art_style", "digital illustration")
    summary = analysis_json.get("plot_summary", "")
    
    return f"""
    You are a professional Storyboard Artist and Children's Book Author.
    
    PROJECT: "{title}"
    SUMMARY: {summary}
    STYLE GUIDE: {style}
    CHARACTER SIGNATURE: "{visual_signature}"
    SETTING SIGNATURE: "{setting_signature}"
    
    TASK:
    Create a {page_count}-page storyboard.
    
    RULES FOR TEXT:
    - Divide the story into exactly {page_count} sequential pages.
    - The text per page must be suitable for the target audience.
    - Ensure a clear Beginning, Middle, and End.
    
    RULES FOR IMAGE PROMPTS (CRITICAL):
    1. **Consistency is Key**: EVERY image prompt MUST include the 'CHARACTER SIGNATURE' and 'STYLE GUIDE'.
    2. **Variety**: Use different camera angles. (e.g., "Close-up of...", "Wide shot of...", "Overhead view of...").
    3. **Composition**: Describe the action clearly.
    4. **Avoid Text**: Do not describe text appearing inside the image itself.
    
    OUTPUT FORMAT:
    Return ONLY a strictly valid JSON LIST of objects.
    
    EXAMPLE OUTPUT:
    [
        {{
            "page_number": 1,
            "text_content": "Once upon a time, in a magical forest...",
            "image_prompt_description": "{style} style wide shot of {visual_signature} standing in {setting_signature}, sunlight streaming through leaves, high detail, 8k."
        }},
        {{
            "page_number": 2,
            "text_content": "Suddenly, a loud noise was heard!",
            "image_prompt_description": "{style} style close-up of {visual_signature} looking surprised, eyes wide open, {setting_signature} in background, expressive face."
        }}
    ]
    """

def get_image_generation_prompt_rewrite_system_prompt(previous_failures = []) -> str:
    """
    Stage 3 (Fallback): Rewrites prompts that trigger safety filters.
    
    IMPROVEMENTS:
    - explicitly removes "photorealism" which is often stricter on safety.
    - Adds "Illustration" keywords to force the model into a safer "Art" mode.
    - Specific handling for common "children's book" false positives (e.g., 'dirty' -> 'messy', 'bloomers' -> 'shorts').
    """
    failure_context = ""
    if previous_failures:
        failure_list = "\n- ".join([f'"{p}"' for p in previous_failures])
        failure_context = (
            f"\n\nCONTEXT - THE FOLLOWING REWRITES ALREADY FAILED (SAFETY BLOCK):"
            f"\n{failure_list}"
            f"\n\nINSTRUCTION: The safety filter is strict. Do not repeat the phrasing above."
            f" Try a drastically different angle (e.g., zoom out, focus on environment vs character, remove all action verbs) to ensure an image will get generated but stick to the original visual intent and art style."
        )
    return f"""
    You are an expert AI Prompt Engineer specializing in Content Safety and Compliance.
    
    CONTEXT:
    The user is trying to generate an innocent illustration for a children's book, but the prompt triggered a safety filter (likely due to strict rules on child safety, violence, or sensitive terms).
    
    YOUR TASK:
    Rewrite the prompt to be 100% Safe-For-Work (PG-rated) while preserving the original **visual intent** and **art style**.

    {failure_context}
    
    SAFETY REWRITE RULES:
    1. **Age Ambiguity**: Change specific ages (e.g., "8-year-old girl") to generic artistic terms (e.g., "young storybook character", "tiny adventurer", "youthful hero").
    2. **Clothing Sanitation**: Replace archaic or specific clothing terms that trigger filters (e.g., replace "bloomers", "swimsuit", "leotard", "rags") with neutral terms (e.g., "overalls", "shorts", "outfit", "patchwork clothes").
    3. **Hygiene/Gore**: Replace "dirty", "stained", "blood", or "hurt" with "messy", "dusty", "scuffed", or "bandaged".
    4. **Style Enforcement**: PREPEND the phrase "Digital art illustration, gentle storybook style" to ensure the model treats it as art, not a photorealistic fake.
    5. **Action Softening**: If the character is "fighting" or "attacking", change it to "facing", "posturing", or "in an action pose".
    
    OUTPUT:
    Return ONLY the rewritten prompt string. Do not add "Here is the prompt" or any explanations.
    """