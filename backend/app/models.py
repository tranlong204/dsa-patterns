from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class Problem(BaseModel):
    id: int
    number: int
    title: str
    difficulty: str
    topics: List[str]
    link: str
    subtopic: Optional[str] = None

class UserProgress(BaseModel):
    problem_id: int
    user_id: str
    solved: bool
    solved_at: Optional[date] = None
    in_revision: Optional[bool] = False

class ProgressStats(BaseModel):
    total_problems: int
    solved_problems: int
    easy_solved: int
    easy_total: int
    medium_solved: int
    medium_total: int
    hard_solved: int
    hard_total: int

class CalendarData(BaseModel):
    date: str
    problem_count: int

class ProblemCreate(BaseModel):
    number: int
    title: str
    difficulty: str
    topics: List[str]
    link: str
    subtopic: Optional[str] = None

class ProblemUpdate(BaseModel):
    title: Optional[str] = None
    difficulty: Optional[str] = None
    topics: Optional[List[str]] = None
    link: Optional[str] = None
    subtopic: Optional[str] = None

