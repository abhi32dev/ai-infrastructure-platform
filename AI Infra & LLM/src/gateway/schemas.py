from pydantic import BaseModel, Field
from typing import List

class CandidateEvaluationRequest(BaseModel):
    candidate_id: str = Field(..., description="Unique ID of the candidate resume.")
    job_description: str = Field(..., description="Target job requirements context.")
    resume_text: str = Field(..., description="Full text of candidate profile.")

class CandidateEvaluation(BaseModel):
    candidate_id: str = Field(..., description="The unique ID of the candidate evaluated.")
    fit_score: float = Field(..., description="Matching percentile fit between 0.0 and 1.0.")
    key_strengths: List[str] = Field(..., description="List of primary core strengths aligned to requirements.")
    growth_areas: List[str] = Field(..., description="Areas needing improvement or validation.")
    source_citations: List[str] = Field(..., description="Explicit text excerpts cited from context resume.")
    confidence_score: float = Field(..., description="Confidence rating between 0.0 and 1.0.")

class CoverLetterRequest(BaseModel):
    candidate_name: str = Field(..., description="Candidate name.")
    job_title: str = Field(..., description="Target job role title.")
    company_name: str = Field(..., description="Target employer name.")
    job_description: str = Field(..., description="Job requirements details.")
    resume_context: str = Field(..., description="Brief candidate achievements profile.")
