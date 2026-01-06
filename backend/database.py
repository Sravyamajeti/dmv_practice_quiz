import os
import random
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")

supabase: Client = create_client(url, key)

def get_random_questions(limit: int = 10):
    """
    Fetches random questions from the database.
    Strategy: Fetch all IDs, sample 'limit' random IDs, then fetch those specific questions.
    This avoids complex stored procedures for now.
    """
    try:
        # 1. Fetch all IDs (lightweight)
        response = supabase.table("questions").select("id").execute()
        all_ids_data = response.data
        all_ids = [item['id'] for item in all_ids_data]

        if not all_ids:
            return []

        # 2. Sample random IDs
        # If we have fewer questions than the limit, take all of them
        sample_size = min(len(all_ids), limit)
        selected_ids = random.sample(all_ids, sample_size)

        # 3. Fetch the actual question data for these IDs
        # We can't easily do "WHERE id IN (...)" with a simple list in one go efficiently without exact syntax
        # But Supabase-py 'in_' filter works well.
        
        response = supabase.table("questions").select("*").in_("id", selected_ids).execute()
        return response.data

    except Exception as e:
        print(f"Error fetching random questions: {e}")
        return []

def get_question_by_id(question_id: str):
    """
    Fetch a single question by its ID.
    """
    try:
        response = supabase.table("questions").select("*").eq("id", question_id).single().execute()
        return response.data
    except Exception as e:
        print(f"Error fetching question {question_id}: {e}")
        return None
