from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from database import get_random_questions, get_question_by_id
from mangum import Mangum

app = FastAPI()
handler = Mangum(app)

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
    """
    Start a new quiz by fetching random question IDs from the database.
    """
    questions = get_random_questions(limit=10)
    if not questions:
        raise HTTPException(status_code=500, detail="No questions loaded or available")
    
    # Return list of IDs
    return [q["id"] for q in questions]

@app.get("/api/question/{question_id}")
def get_question_details(question_id: str):
    """
    Get details for a specific question by ID.
    """
    question = get_question_by_id(question_id)
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Map database keys to frontend expectation if necessary
    # The frontend expects camelCase or specific keys? 
    # Let's check the previous main.py structure.
    # Previous structure:
    # "id": ..., "question": ..., "options": {"A": ..., "B": ..., "C": ...}, "correctAnswer": ..., "explanation": ...
    
    # Database columns (based on plan schema):
    # id, question, option_a, option_b, option_c, correct_answer, explanation
    
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
