import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
JSON_URL = os.getenv("JSON_URL")
GOOGLE_APP_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "creds.json")
ENVIRONMENT= os.getenv("ENVIRONMENT", "development")
AZ_BLOB_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZ_BLOB_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "storytellingprojbucket")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Download Google vertex Json
response = requests.get(JSON_URL)
if response.status_code == 200:
    os.makedirs(os.path.dirname(GOOGLE_APP_CREDENTIALS), exist_ok=True)
    with open(GOOGLE_APP_CREDENTIALS, "w") as file:
        json_f = response.json()
        json.dump(json_f, file)