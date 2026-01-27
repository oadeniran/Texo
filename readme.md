# Texo: Weaving Voices into Legacy

**Texo** (Latin for *"to weave"*) is an autonomous AI agent that functions as a real-time publisher. It preserves oral history and democratizes personalized education by transforming raw voice recordings into fully illustrated, professional-grade children's books in seconds.

Built for the **Gemini 3 Hackathon**, Texo leverages a multi-agent architecture to listen, reason, illustrate, and publish stories without human intervention.

---

## 🚀 Key Features

* **🗣️ Deep Listening (Gemini Flash):** Bypasses traditional speech-to-text. Texo natively understands raw audio files, capturing tone, emotion, and hesitation to inform the narrative mood.
* **🧠 Orchestrator Agent (Gemini Pro):** A reasoning engine that creates a "Story Bible" for every project, ensuring character consistency and plot coherence across pages.
* **🛡️ Self-Correction Loop:** Features an "Antifragile" workflow. If an illustration request triggers a safety filter, the agent autonomously rewrites its own prompt to be compliant while preserving the artistic intent—no user intervention required.
* **🎨 Consistent Illustration (Imagen 3):** Uses a "Visual Signature" injection technique to ensure the main character looks the same on Page 1 as they do on Page 10.
* **⚡ Real-Time Production:** Parallelized worker threads generate text and images simultaneously, reducing production time from hours to seconds.

---

## 🏗️ Architecture & Tech Stack

The project is structured as a Monorepo containing a Next.js frontend and a FastAPI backend.

### Backend (`/backend`)

* **Framework:** Python FastAPI
* **AI Intelligence:** Google Vertex AI (Gemini 2.5 Flash, Gemini 3 Pro, Imagen 3)
* **Database:** MongoDB (via Motor)
* **Storage:** Azure Blob Storage (for serving generated assets)

### Frontend (`/frontend`)

* **Framework:** Next.js 14 (App Router)
* **Styling:** CSS Modules with responsive design
* **State Management:** React Hooks for polling and audio recording
* **Animations:** Framer Motion

---

## 📂 Project Structure

```bash
.
├── backend/                # Python FastAPI Server
│   ├── llm_client.py       # Wrapper for Google Vertex AI & Gemini
│   ├── orchestrator.py     # The "Brain" - manages agent state & parallelization
│   ├── database.py         # MongoDB connection logic
│   ├── main.py             # API Endpoints
│   ├── models.py           # Pydantic data models
│   └── PROMPTS.py          # System instructions & Chain-of-Thought prompts
│
├── frontend/               # Next.js Client
│   ├── src/app/            # App Router pages (Home, Story Viewer, History)
│   ├── src/components/     # Reusable UI (VoiceRecorder, Navbar)
│   └── public/             # Static assets
│
└── docker-compose.yml      # (Optional) Container orchestration

```

---

## 🛠️ Getting Started

### Prerequisites

* Node.js 18+
* Python 3.10+
* Google Cloud Project with Vertex AI enabled
* MongoDB Instance (Local or Atlas)
* Azure Storage Account (or alternative blob storage)

### 1. Backend Setup

Navigate to the backend folder:

```bash
cd backend

```

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

```

Configure Environment Variables:
Create a `.env` file in `/backend`:

```env
GOOGLE_API_KEY=your_google_cloud_api_key
GOOGLE_PROJECT_ID=your_project_id
GOOGLE_LOCATION=us-central1

MONGODB_URI=mongodb://localhost:27017
DB_NAME=texo_db

AZURE_STORAGE_CONNECTION_STRING=your_azure_connection_string
AZURE_CONTAINER_NAME=stories

```

Run the Server:

```bash
uvicorn main:app --reload --port 8000

```

### 2. Frontend Setup

Navigate to the frontend folder:

```bash
cd ../frontend

```

Install dependencies:

```bash
npm install
# or
yarn install

```

Configure Environment Variables:
Create a `.env.local` file in `/frontend`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api

```

Run the Development Server:

```bash
npm run dev

```

Open [http://localhost:3000](https://www.google.com/search?q=http://localhost:3000) in your browser.

---

## 🧪 How It Works (The Agentic Loop)

1. **Input:** User records a voice note: *"Tell a story about a brave toaster who is afraid of bread."*
2. **Transcription & Analysis:** Gemini Flash transcribes the audio and extracts the "Story Bible" (Character: Silver Toaster, Setting: Kitchen, Style: Pixar 3D).
3. **Storyboarding:** The Orchestrator splits the narrative into 5 pages of text and image prompts.
4. **Parallel Generation:** * **Text:** Generated instantly.
* **Images:** Sent to Imagen 3.
* *Self-Correction:* If a prompt like "burning bread" triggers a safety filter, the backend catches the error, rewrites the prompt to "toasted bread," and retries automatically.


5. **Assembly:** The frontend polls for status updates and assembles the flipbook in real-time.

---

## 🤝 Contributing

Contributions are welcome! Details soon, hopefully after a win in the hack😅

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.