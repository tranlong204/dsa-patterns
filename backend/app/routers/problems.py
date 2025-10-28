from fastapi import APIRouter, HTTPException
from app.database import get_supabase
from app.models import Problem, ProblemCreate, ProblemUpdate
from typing import List, Optional
import json

router = APIRouter()

@router.get("/", response_model=List[Problem])
async def get_all_problems():
    """Get all problems"""
    try:
        supabase = get_supabase()
        response = supabase.table("problems").select("*").execute()
        return [Problem(**problem) for problem in response.data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{problem_id}", response_model=Problem)
async def get_problem(problem_id: int):
    """Get a specific problem by ID"""
    try:
        supabase = get_supabase()
        response = supabase.table("problems").select("*").eq("id", problem_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Problem not found")
        return Problem(**response.data[0])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Problem)
async def create_problem(problem: ProblemCreate):
    """Create a new problem"""
    try:
        supabase = get_supabase()
        # Convert topics list to JSON string for Supabase
        data = problem.dict()
        # Remove 'id' if present (Supabase auto-generates it)
        if 'id' in data:
            del data['id']
        data['topics'] = json.dumps(data['topics'])
        
        response = supabase.table("problems").insert(data).execute()
        return Problem(**response.data[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{problem_id}", response_model=Problem)
async def update_problem(problem_id: int, problem: ProblemUpdate):
    """Update an existing problem"""
    try:
        supabase = get_supabase()
        data = problem.dict(exclude_none=True)
        
        # Convert topics to JSON if present
        if 'topics' in data and data['topics']:
            data['topics'] = json.dumps(data['topics'])
        
        response = supabase.table("problems").update(data).eq("id", problem_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Problem not found")
        return Problem(**response.data[0])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{problem_id}")
async def delete_problem(problem_id: int):
    """Delete a problem"""
    try:
        supabase = get_supabase()
        response = supabase.table("problems").delete().eq("id", problem_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Problem not found")
        return {"message": "Problem deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-category/{category}", response_model=List[Problem])
async def get_problems_by_category(category: str):
    """Get problems by category/topic"""
    try:
        supabase = get_supabase()
        # Search in JSON array field
        response = supabase.table("problems").select("*").execute()
        
        # Filter in Python (Supabase JSONB filtering can be complex)
        filtered = []
        for problem in response.data:
            topics = json.loads(problem.get('topics', '[]')) if isinstance(problem.get('topics'), str) else problem.get('topics', [])
            if category in topics:
                filtered.append(Problem(**problem))
        
        return filtered
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

