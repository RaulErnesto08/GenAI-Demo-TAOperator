from pydantic import BaseModel
from typing import List

class Candidate(BaseModel):
    """Pydantic model for a LinkedIn candidate entry"""
    name: str
    match_score: float
    matched_skills: List[str]
    non_matched_skills: List[str]
    location: str
    profile_url: str
