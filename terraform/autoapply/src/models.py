"""Data models for AutoApply."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class ATSPlatform(str, Enum):
    """Supported ATS platforms."""
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    WORKDAY = "workday"
    ASHBY = "ashby"
    SMARTRECRUITERS = "smartrecruiters"
    ICIMS = "icims"
    JOBVITE = "jobvite"
    UNKNOWN = "unknown"


class JobRequirement(BaseModel):
    """A single job requirement with priority."""
    text: str
    priority: str = Field(description="must_have, preferred, or nice_to_have")
    matched: bool = Field(default=False)
    match_evidence: Optional[str] = Field(default=None)


class JobDescription(BaseModel):
    """Parsed job description."""
    url: HttpUrl
    ats_platform: ATSPlatform
    company_name: str
    job_title: str
    location: Optional[str] = None
    salary_range: Optional[str] = None
    responsibilities: list[str] = Field(default_factory=list)
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    requirements: list[JobRequirement] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    raw_text: str = Field(description="Raw job description text")


class BaseResume(BaseModel):
    """Base resume data structure."""
    full_name: str
    email: str
    phone: str
    location: str
    linkedin: Optional[str] = None
    website: Optional[str] = None
    summary: str
    skills: list[str] = Field(default_factory=list)
    experience: list[dict] = Field(default_factory=list)
    education: list[dict] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)


class TailoredResume(BaseModel):
    """AI-generated tailored resume."""
    job_url: HttpUrl
    company_name: str
    job_title: str
    summary: str
    skills_section: str
    experience_section: str
    achievements_section: str
    education_section: str
    full_text: str
    keywords_used: list[str] = Field(default_factory=list)
    match_score: float = Field(ge=0, le=100)


class CoverLetter(BaseModel):
    """AI-generated cover letter."""
    job_url: HttpUrl
    company_name: str
    job_title: str
    content: str
    word_count: int


class ApplicationStatus(str, Enum):
    """Status of a job application."""
    PENDING = "pending"
    JD_FETCHED = "jd_fetched"
    RESUME_GENERATED = "resume_generated"
    COVER_LETTER_GENERATED = "cover_letter_generated"
    PDF_GENERATED = "pdf_generated"
    FORM_OPENED = "form_opened"
    FORM_FILLED = "form_filled"
    SUBMITTED = "submitted"
    FAILED = "failed"
    MANUAL_REQUIRED = "manual_required"


class Application(BaseModel):
    """Complete job application record."""
    id: str
    job_url: HttpUrl
    status: ApplicationStatus = ApplicationStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    job_description: Optional[JobDescription] = None
    tailored_resume: Optional[TailoredResume] = None
    cover_letter: Optional[CoverLetter] = None
    output_dir: Optional[Path] = None
    resume_pdf_path: Optional[Path] = None
    cover_letter_pdf_path: Optional[Path] = None
    error_message: Optional[str] = None
    notes: Optional[str] = None
