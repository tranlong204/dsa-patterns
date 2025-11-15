from fastapi import APIRouter, HTTPException
from typing import List
from app.database import get_supabase
from app.models import CompanyTag, CompanyTagCreate, CompanyTagUpdate

router = APIRouter()

@router.get("/", response_model=List[CompanyTag])
async def list_company_tags():
    try:
        supabase = get_supabase()
        resp = supabase.table("company_tags").select("*").order("name").execute()
        return resp.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=CompanyTag)
async def create_company_tag(payload: CompanyTagCreate):
    try:
        supabase = get_supabase()
        resp = supabase.table("company_tags").insert({"name": payload.name}).execute()
        return resp.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{tag_id}", response_model=CompanyTag)
async def update_company_tag(tag_id: int, payload: CompanyTagUpdate):
    try:
        supabase = get_supabase()
        data = {k: v for k, v in payload.dict().items() if v is not None}
        resp = supabase.table("company_tags").update(data).eq("id", tag_id).execute()
        if not resp.data:
            raise HTTPException(status_code=404, detail="Tag not found")
        return resp.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{tag_id}")
async def delete_company_tag(tag_id: int):
    try:
        supabase = get_supabase()
        # delete relations first
        supabase.table("problem_company_tags").delete().eq("tag_id", tag_id).execute()
        resp = supabase.table("company_tags").delete().eq("id", tag_id).execute()
        if not resp.data:
            raise HTTPException(status_code=404, detail="Tag not found")
        return {"message": "Tag deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/problem/{problem_id}", response_model=List[int])
async def get_problem_tags(problem_id: int):
    try:
        supabase = get_supabase()
        resp = supabase.table("problem_company_tags").select("tag_id").eq("problem_id", problem_id).execute()
        return [row["tag_id"] for row in resp.data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/problem/{problem_id}")
async def set_problem_tags(problem_id: int, tag_ids: List[int]):
    try:
        supabase = get_supabase()
        # fetch existing
        current_resp = supabase.table("problem_company_tags").select("tag_id").eq("problem_id", problem_id).execute()
        current = {row["tag_id"] for row in current_resp.data}
        desired = set(tag_ids)
        to_add = desired - current
        to_remove = current - desired
        if to_remove:
            supabase.table("problem_company_tags").delete().eq("problem_id", problem_id).in_("tag_id", list(to_remove)).execute()
        for tid in to_add:
            supabase.table("problem_company_tags").insert({"problem_id": problem_id, "tag_id": tid}).execute()
        return {"message": "Tags updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all-problem-tags")
async def get_all_problem_tags():
    """Return mapping of problem_id -> list[tag_id]"""
    try:
        supabase = get_supabase()
        resp = supabase.table("problem_company_tags").select("problem_id, tag_id").execute()
        mapping = {}
        for row in resp.data:
            pid = row["problem_id"]
            tid = row["tag_id"]
            mapping.setdefault(pid, []).append(tid)
        return mapping
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


