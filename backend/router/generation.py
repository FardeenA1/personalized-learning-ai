import json

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from database import get_db
from models import User, StyleProfile
from schemas import NoteGenerationResponse
from service.prompt_builder import PromptBuilder, build_plain_prompt
from service.style_analyzer import normalize_subject
from service.ai_service import generate_ai_notes
from service.document_parser import extract_text_from_file
from service.style_matcher import compute_style_match
from auth import get_current_user

router = APIRouter(prefix="/generate", tags=["AI Note Generation"])

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "jpg", "jpeg", "png"}


@router.post("/notes", response_model=NoteGenerationResponse)
async def generate_notes(
    subject: str = Form(...),
    topic: str = Form(...),
    mode: str = Form("my_style"),
    source_content: str = Form(None),
    file: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subject = normalize_subject(subject)

    style_profile = db.query(StyleProfile).filter(
        StyleProfile.user_id == current_user.id,
        StyleProfile.subject == subject
    ).first()

    if not style_profile:
        raise HTTPException(
            status_code=404,
            detail=f"No style profile found for {subject}. Upload and analyze your {subject} notes first."
        )

    if file is not None:

        if not file.filename:
            raise HTTPException(status_code=400, detail="File name is missing")

        extension = file.filename.split(".")[-1].lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Allowed: PDF, DOCX, TXT, JPG, JPEG, PNG"
            )

        temp_path = f"temp_{current_user.id}_{file.filename}"

        try:
            with open(temp_path, "wb") as buffer:
                buffer.write(await file.read())

            result = extract_text_from_file(temp_path, extension)
            resolved_content = result["text"]
            has_source = True

        finally:
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path)

        if not resolved_content.strip():
            raise HTTPException(status_code=400, detail="No readable text found in uploaded file.")

    elif source_content:
        resolved_content = source_content
        has_source = True

    else:
        resolved_content = topic
        has_source = False

    learning_dna = json.loads(style_profile.style_dna)
    prompt_mode = "exam" if mode == "exam_board" else "normal"

    styled_prompt = PromptBuilder(
        learning_dna=learning_dna,
        textbook_text=resolved_content,
        mode=prompt_mode,
        has_source=has_source
    ).generate_prompt()

    plain_prompt = build_plain_prompt(
        topic=topic,
        textbook_text=resolved_content,
        has_source=has_source
    )

    styled_notes = generate_ai_notes(styled_prompt)
    raw_notes = generate_ai_notes(plain_prompt)

    style_match = compute_style_match(learning_dna, styled_notes)

    return {
        "subject": subject,
        "topic": topic,
        "mode": mode,
        "generated_notes": styled_notes,
        "raw_notes": raw_notes,
        "style_match": style_match
    }