import os
from pymongo import MongoClient
from datetime import datetime, timezone
from init_env import MONGO_URI

# Initialize Client
client = MongoClient(MONGO_URI)
db = client.get_database("storyteller_db")
stories_collection = db.get_collection("stories")

def serialize_story(story: dict) -> dict:
    """Helper to fix MongoDB's _id object for JSON"""
    if story and "_id" in story:
        story["id"] = str(story["_id"])  # Ensure ID is a string
        del story["_id"]
    return story

def save_story(story_id: str, data: dict):
    """Upserts the story (Create or Update)"""
    # We use the UUID as the MongoDB _id
    data["_id"] = story_id
    stories_collection.replace_one({"_id": story_id}, data, upsert=True)

def get_story(story_id: str):
    doc = stories_collection.find_one({"_id": story_id})
    return serialize_story(doc)

def get_all_stories():
    cursor = stories_collection.find().sort("timestamp", -1) # Optional: sort by time
    return [serialize_story(doc) for doc in cursor]

def update_status(story_id: str, stage: str, progress: int, message: str):
    """
    Updates the current status AND pushes a new entry to the history log.
    """
    new_log_entry = {
        "stage": stage,
        "message": message,
        "timestamp": datetime.now(timezone.utc)
    }

    if progress >= 0:
        new_log_entry["progress"] = progress
    else:
        # Fetch current progress if not provided
        story = get_story(story_id)
        new_log_entry["progress"] = story.get("progress", 0)

    data_to_set = {
        "status": stage,
        "current_stage_message": message
    }
    if progress >= 0:
        data_to_set["progress"] = progress

    stories_collection.update_one(
        {"_id": story_id},
        {
            # 1. Update the "Current" view (for the card UI)
            "$set": data_to_set,
            # 2. Append to the "History" list (for the timeline UI)
            "$push": {
                "status_history": new_log_entry
            }
        }
    )