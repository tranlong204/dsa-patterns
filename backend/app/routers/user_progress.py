from fastapi import APIRouter, HTTPException
from app.database import get_supabase
from app.models import UserProgress, ProgressStats, CalendarData
from typing import List
from datetime import date, timedelta
import json

router = APIRouter()

@router.get("/{user_id}/solved", response_model=List[int])
async def get_solved_problems(user_id: str):
    """Get list of solved problem IDs for a user"""
    try:
        supabase = get_supabase()
        response = supabase.table("user_progress").select("problem_id").eq("user_id", user_id).eq("solved", True).execute()
        return [row['problem_id'] for row in response.data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}/solved/{problem_id}")
async def mark_problem_solved(user_id: str, problem_id: int):
    """Mark a problem as solved for a user"""
    try:
        supabase = get_supabase()
        
        # Check if entry exists
        existing = supabase.table("user_progress").select("*").eq("user_id", user_id).eq("problem_id", problem_id).execute()
        
        if existing.data:
            # Update existing entry
            response = supabase.table("user_progress").update({
                "solved": True,
                "solved_at": date.today().isoformat()
            }).eq("user_id", user_id).eq("problem_id", problem_id).execute()
        else:
            # Insert new entry
            response = supabase.table("user_progress").insert({
                "user_id": user_id,
                "problem_id": problem_id,
                "solved": True,
                "solved_at": date.today().isoformat()
            }).execute()
        
        return {"message": "Problem marked as solved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}/solved/{problem_id}")
async def mark_problem_unsolved(user_id: str, problem_id: int):
    """Mark a problem as unsolved for a user by setting solved to False"""
    try:
        supabase = get_supabase()
        # Ensure row exists; if not, create one with solved False (idempotent)
        existing = supabase.table("user_progress").select("*").eq("user_id", user_id).eq("problem_id", problem_id).execute()
        if existing.data:
            supabase.table("user_progress").update({
                "solved": False,
                "solved_at": None
            }).eq("user_id", user_id).eq("problem_id", problem_id).execute()
        else:
            supabase.table("user_progress").insert({
                "user_id": user_id,
                "problem_id": problem_id,
                "solved": False,
                "solved_at": None
            }).execute()
        return {"message": "Problem marked as unsolved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Revision endpoints
@router.get("/{user_id}/revision", response_model=List[int])
async def get_revision_list(user_id: str):
    try:
        supabase = get_supabase()
        response = supabase.table("user_progress").select("problem_id").eq("user_id", user_id).eq("in_revision", True).execute()
        return [row['problem_id'] for row in response.data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}/revision/{problem_id}")
async def add_to_revision(user_id: str, problem_id: int):
    try:
        supabase = get_supabase()
        existing = supabase.table("user_progress").select("*").eq("user_id", user_id).eq("problem_id", problem_id).execute()
        if existing.data:
            supabase.table("user_progress").update({"in_revision": True}).eq("user_id", user_id).eq("problem_id", problem_id).execute()
        else:
            supabase.table("user_progress").insert({
                "user_id": user_id,
                "problem_id": problem_id,
                "in_revision": True
            }).execute()
        return {"message": "Added to revision"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}/revision/{problem_id}")
async def remove_from_revision(user_id: str, problem_id: int):
    try:
        supabase = get_supabase()
        supabase.table("user_progress").update({"in_revision": False}).eq("user_id", user_id).eq("problem_id", problem_id).execute()
        return {"message": "Removed from revision"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/stats", response_model=ProgressStats)
async def get_user_stats(user_id: str):
    """Get progress statistics for a user"""
    try:
        supabase = get_supabase()
        
        # Get all problems
        problems_response = supabase.table("problems").select("*").execute()
        all_problems = problems_response.data
        
        # Get solved problems for user
        solved_response = supabase.table("user_progress").select("problem_id").eq("user_id", user_id).eq("solved", True).execute()
        solved_ids = {row['problem_id'] for row in solved_response.data}
        
        # Calculate stats
        total = len(all_problems)
        solved = len(solved_ids)
        
        easy_solved = 0
        medium_solved = 0
        hard_solved = 0
        easy_total = 0
        medium_total = 0
        hard_total = 0
        
        for problem in all_problems:
            if problem['difficulty'] == 'Easy':
                easy_total += 1
                if problem['id'] in solved_ids:
                    easy_solved += 1
            elif problem['difficulty'] == 'Medium':
                medium_total += 1
                if problem['id'] in solved_ids:
                    medium_solved += 1
            elif problem['difficulty'] == 'Hard':
                hard_total += 1
                if problem['id'] in solved_ids:
                    hard_solved += 1
        
        return ProgressStats(
            total_problems=total,
            solved_problems=solved,
            easy_solved=easy_solved,
            easy_total=easy_total,
            medium_solved=medium_solved,
            medium_total=medium_total,
            hard_solved=hard_solved,
            hard_total=hard_total
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/calendar", response_model=List[CalendarData])
async def get_calendar_data(user_id: str, days: int = 371):
    """Get calendar data for activity tracking"""
    try:
        supabase = get_supabase()
        
        # Get all solved problems with their solved dates
        response = supabase.table("user_progress").select("*").eq("user_id", user_id).eq("solved", True).not_.is_("solved_at", "null").execute()
        
        # Group by date
        calendar_map = {}
        for row in response.data:
            solved_date = row.get('solved_at')
            if solved_date:
                calendar_map[solved_date] = calendar_map.get(solved_date, 0) + 1
        
        # Return list of calendar data
        return [CalendarData(date=date_key, problem_count=count) 
                for date_key, count in calendar_map.items()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

