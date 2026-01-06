import sys
import os
import random
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

supabase: Client = create_client(url, key)

# Database helper functions
def get_random_questions(limit: int = 10):
    """Fetches random questions from the database."""
    try:
        response = supabase.table("questions").select("id").execute()
        all_ids_data = response.data
        all_ids = [item['id'] for item in all_ids_data]

        if not all_ids:
            return []

        sample_size = min(len(all_ids), limit)
        selected_ids = random.sample(all_ids, sample_size)
        
        response = supabase.table("questions").select("*").in_("id", selected_ids).execute()
        return response.data

    except Exception as e:
        print(f"Error fetching random questions: {e}")
        return []

def get_question_by_id(question_id: str):
    """Fetch a single question by its ID."""
    try:
        response = supabase.table("questions").select("*").eq("id", question_id).single().execute()
        return response.data
    except Exception as e:
        print(f"Error fetching question {question_id}: {e}")
        return None

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/api/start_quiz")
def start_quiz():
    """Start a new quiz by fetching random question IDs from the database."""
    questions = get_random_questions(limit=10)
    if not questions:
        raise HTTPException(status_code=500, detail="No questions loaded or available")
    
    return [q["id"] for q in questions]

@app.get("/api/question/{question_id}")
def get_question_details(question_id: str):
    """Get details for a specific question by ID."""
    question = get_question_by_id(question_id)
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    formatted_question = {
        "id": question["id"],
        "question": question["Question"],
        "options": {
            "A": question["Option A"],
            "B": question["Option B"],
            "C": question["Option C"]
        },
        "correctAnswer": question["Correct Answer"].strip(),
        "explanation": question["Explanation"]
    }
    
    return formatted_question

@app.get("/health")
def health_check():
    return {"status": "ok", "mode": "database"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
