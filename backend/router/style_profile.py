import json
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User, StyleProfile
from schemas import StyleProfileResponse
from auth import get_current_user

from service.document_parser import extract_text_from_file
from service.style_analyzer import StyleAnalyzer, normalize_subject
from service.pattern_analyzer import PatternAnalyzer
from service.dna_generator import DNAGenerator

router = APIRouter(prefix="/style", tags=["Style Profile"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "jpg", "jpeg", "png"}


@router.post("/upload", response_model=StyleProfileResponse)
async def upload_and_analyze(
    subject: str = Form(...),
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    subject = normalize_subject(subject)

    if not subject:
        raise HTTPException(status_code=400, detail="Subject is required.")

    saved_paths = []
    combined_text = ""

    try:
        for file in files:

            if not file.filename:
                raise HTTPException(status_code=400, detail="File name is missing")

            extension = file.filename.split(".")[-1].lower()

            if extension not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail="Unsupported file type. Allowed: PDF, DOCX, TXT, JPG, JPEG, PNG"
                )

            destination = UPLOAD_DIR / f"user_{current_user.id}_{file.filename}"

            with open(destination, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            saved_paths.append(destination)

            result = extract_text_from_file(str(destination), extension)
            combined_text += "\n" + result["text"]

        if not combined_text.strip():
            raise HTTPException(status_code=400, detail="No readable text found in uploaded files.")

        analyzer = StyleAnalyzer(combined_text)
        pattern_analyzer = PatternAnalyzer(combined_text)

        profile_features = analyzer.build_learning_dna()
        profile_features["common_words"] = analyzer.common_words()
        profile_features["headings"] = pattern_analyzer.detect_sections()

        style_dna = DNAGenerator(profile_features).generate()
        style_dna_json = json.dumps(style_dna, indent=4)

        existing = db.query(StyleProfile).filter(
            StyleProfile.user_id == current_user.id,
            StyleProfile.subject == subject
        ).first()

        if existing:
            existing.style_dna = style_dna_json
            profile = existing
        else:
            profile = StyleProfile(
                user_id=current_user.id,
                subject=subject,
                style_dna=style_dna_json
            )
            db.add(profile)

        db.commit()
        db.refresh(profile)

        return profile

    finally:
        for path in saved_paths:
            if path.exists():
                path.unlink()


@router.get("", response_model=list[StyleProfileResponse])
def get_my_styles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(StyleProfile).filter(
        StyleProfile.user_id == current_user.id
    ).all()


@router.get("/{subject}", response_model=StyleProfileResponse)
def get_subject_style(
    subject: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subject = normalize_subject(subject)

    profile = db.query(StyleProfile).filter(
        StyleProfile.user_id == current_user.id,
        StyleProfile.subject == subject
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail=f"No style profile found for subject '{subject}'.")

    return profile
@router.delete("/{subject}")
def delete_style_profile(
    subject: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subject = normalize_subject(subject)

    profile = db.query(StyleProfile).filter(
        StyleProfile.user_id == current_user.id,
        StyleProfile.subject == subject
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail=f"No style profile found for subject '{subject}'.")

    db.delete(profile)
    db.commit()

    return {"message": f"Style profile for '{subject}' deleted successfully."}