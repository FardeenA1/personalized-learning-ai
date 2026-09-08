from pydantic import BaseModel, EmailStr
from typing import Optional, Any
from datetime import datetime


# ---------------- AUTH ----------------

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    is_admin: bool

    class Config:
        from_attributes = True


class AdminUserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    is_admin: bool
    created_at: datetime
    subject_count: int
    subjects: list[str]


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------------- STYLE PROFILE ----------------

class StyleProfileResponse(BaseModel):
    id: int
    subject: str
    style_dna: str
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------------- GENERATION ----------------



class StyleMatchBreakdown(BaseModel):
    complexity: float
    paragraph_style: float
    bullets: float
    numbering: float


class StyleMatch(BaseModel):
    overall_match: float
    breakdown: StyleMatchBreakdown


class NoteGenerationResponse(BaseModel):
    subject: str
    topic: str
    mode: str
    generated_notes: str
    raw_notes: str
    style_match: StyleMatch


# ---------------- STUDENT PROFILE ----------------

class ProfileCreate(BaseModel):
    class_name: Optional[str] = None
    board: Optional[str] = None
    preferred_language: Optional[str] = None


class ProfileResponse(BaseModel):
    id: int
    class_name: Optional[str]
    board: Optional[str]
    preferred_language: Optional[str]

    class Config:
        from_attributes = True