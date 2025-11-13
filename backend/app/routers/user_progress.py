from fastapi import APIRouter, HTTPException, Depends, Body
from app.database import get_supabase
from app.models import UserProgress, ProgressStats, CalendarData, MarkSolvedRequest
from typing import List, Optional
from datetime import date, timedelta
import json
from app.auth import get_current_username

router = APIRouter()

@router.get("/{user_id}/solved", response_model=List[int])
async def get_solved_problems(user_id: str, current_user: str = Depends(get_current_username)):
    """Get list of solved problem IDs for a user"""
    try:
        supabase = get_supabase()
        # Use auth identity as the user id, ignore client-sent user_id to prevent mismatches
        uid = current_user
        response = supabase.table("user_progress").select("problem_id").eq("user_id", uid).eq("solved", True).execute()
        return [row['problem_id'] for row in response.data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}/solved/{problem_id}")
async def mark_problem_solved(
    user_id: str, 
    problem_id: int, 
    current_user: str = Depends(get_current_username),
    request: Optional[MarkSolvedRequest] = None
):
    """Mark a problem as solved for a user"""
    try:
        import logging
        supabase = get_supabase()
        uid = current_user
        
        # Get solved_at from request body (user's local date) or use server date as fallback
        if request and request.solved_at:
            solved_at_str = request.solved_at
            logging.info(f"Using date from request body: {solved_at_str}")
        else:
            # Fallback to server date for backward compatibility
            solved_at_str = date.today().isoformat()
            logging.info(f"No date in request, using server date: {solved_at_str}")
        
        # Validate date format (YYYY-MM-DD)
        try:
            # Validate the date string format
            if len(solved_at_str) == 10 and solved_at_str.count('-') == 2:
                # Try to parse to ensure it's a valid date
                year, month, day = map(int, solved_at_str.split('-'))
                date(year, month, day)  # This will raise ValueError if invalid
            else:
                raise ValueError("Invalid date format")
        except (ValueError, TypeError) as e:
            # If invalid, fall back to server date
            logging.warning(f"Invalid date format {solved_at_str}, falling back to server date: {e}")
            solved_at_str = date.today().isoformat()
        
        logging.info(f"Final solved_at date: {solved_at_str}")
        
        # Check if entry exists
        existing = supabase.table("user_progress").select("*").eq("user_id", uid).eq("problem_id", problem_id).execute()
        
        if existing.data:
            # Update existing entry - always update solved_at when marking as solved
            response = supabase.table("user_progress").update({
                "solved": True,
                "solved_at": solved_at_str
            }).eq("user_id", uid).eq("problem_id", problem_id).execute()
        else:
            # Insert new entry
            response = supabase.table("user_progress").insert({
                "user_id": uid,
                "problem_id": problem_id,
                "solved": True,
                "solved_at": solved_at_str
            }).execute()
        
        return {"message": "Problem marked as solved", "solved_at": solved_at_str}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}/solved/{problem_id}")
async def mark_problem_unsolved(user_id: str, problem_id: int, current_user: str = Depends(get_current_username)):
    """Mark a problem as unsolved for a user by setting solved to False"""
    try:
        supabase = get_supabase()
        uid = current_user
        # Ensure row exists; if not, create one with solved False (idempotent)
        existing = supabase.table("user_progress").select("*").eq("user_id", uid).eq("problem_id", problem_id).execute()
        if existing.data:
            supabase.table("user_progress").update({
                "solved": False,
                "solved_at": None
            }).eq("user_id", uid).eq("problem_id", problem_id).execute()
        else:
            supabase.table("user_progress").insert({
                "user_id": uid,
                "problem_id": problem_id,
                "solved": False,
                "solved_at": None
            }).execute()
        return {"message": "Problem marked as unsolved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Revision endpoints
@router.get("/{user_id}/revision", response_model=List[int])
async def get_revision_list(user_id: str, current_user: str = Depends(get_current_username)):
    try:
        supabase = get_supabase()
        response = supabase.table("user_progress").select("problem_id").eq("user_id", current_user).eq("in_revision", True).execute()
        return [row['problem_id'] for row in response.data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}/revision/{problem_id}")
async def add_to_revision(user_id: str, problem_id: int, current_user: str = Depends(get_current_username)):
    try:
        supabase = get_supabase()
        existing = supabase.table("user_progress").select("*").eq("user_id", current_user).eq("problem_id", problem_id).execute()
        if existing.data:
            supabase.table("user_progress").update({"in_revision": True}).eq("user_id", current_user).eq("problem_id", problem_id).execute()
        else:
            supabase.table("user_progress").insert({
                "user_id": current_user,
                "problem_id": problem_id,
                "in_revision": True
            }).execute()
        return {"message": "Added to revision"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}/revision/{problem_id}")
async def remove_from_revision(user_id: str, problem_id: int, current_user: str = Depends(get_current_username)):
    try:
        supabase = get_supabase()
        supabase.table("user_progress").update({"in_revision": False}).eq("user_id", current_user).eq("problem_id", problem_id).execute()
        return {"message": "Removed from revision"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/stats", response_model=ProgressStats)
async def get_user_stats(user_id: str, current_user: str = Depends(get_current_username)):
    """Get progress statistics for a user"""
    try:
        supabase = get_supabase()
        
        # Get all problems with pagination
        all_problems = []
        offset = 0
        page_size = 1000
        while True:
            problems_response = supabase.table("problems").select("*").range(offset, offset + page_size - 1).execute()
            all_problems.extend(problems_response.data)
            if len(problems_response.data) < page_size:
                break
            offset += page_size
        
        # Get solved problems for user
        solved_ids_set = set()
        offset = 0
        while True:
            solved_response = supabase.table("user_progress").select("problem_id").eq("user_id", current_user).eq("solved", True).range(offset, offset + page_size - 1).execute()
            for row in solved_response.data:
                solved_ids_set.add(row['problem_id'])
            if len(solved_response.data) < page_size:
                break
            offset += page_size
        solved_ids = solved_ids_set
        
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
async def get_calendar_data(user_id: str, days: int = 371, current_user: str = Depends(get_current_username)):
    """Get calendar data for activity tracking"""
    try:
        supabase = get_supabase()
        
        # Get all solved problems with their solved dates
        # Use a simpler query - get all solved=True and filter in Python
        response = supabase.table("user_progress").select("problem_id, solved_at").eq("user_id", current_user).eq("solved", True).execute()
        
        # Group by date - normalize date format to YYYY-MM-DD
        calendar_map = {}
        for row in response.data:
            solved_date = row.get('solved_at')
            if solved_date:
                # Normalize date to YYYY-MM-DD format
                # Handle both string and date/datetime objects
                if isinstance(solved_date, str):
                    # If it's a string, extract just the date part (YYYY-MM-DD)
                    date_str = solved_date.split('T')[0] if 'T' in solved_date else solved_date.split(' ')[0]
                    date_key = date_str[:10] if len(date_str) >= 10 else date_str
                elif hasattr(solved_date, 'isoformat'):
                    # It's a date or datetime object
                    date_key = solved_date.isoformat()[:10]
                elif hasattr(solved_date, 'date'):
                    # It's a datetime object, get the date part
                    date_key = solved_date.date().isoformat()
                else:
                    # Fallback: convert to string and take first 10 chars
                    date_key = str(solved_date)[:10]
                
                # Only count if date_key is valid (YYYY-MM-DD format)
                if len(date_key) == 10 and date_key.count('-') == 2:
                    calendar_map[date_key] = calendar_map.get(date_key, 0) + 1
        
        # Debug: log today's date and calendar data
        import logging
        logging.info(f"Calendar data: {calendar_map}")
        logging.info(f"Today's date: {date.today().isoformat()}")
        
        # Return list of calendar data
        return [CalendarData(date=date_key, problem_count=count) 
                for date_key, count in calendar_map.items()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

