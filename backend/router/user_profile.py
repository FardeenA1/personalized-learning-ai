from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from database import get_db
from models import User, StudentProfile
from schemas import (
    ProfileCreate,
    ProfileResponse
)

from auth import get_current_user


router = APIRouter()


@router.post(
    "/profile",
    response_model=ProfileResponse
)
def create_profile(
    profile_data: ProfileCreate,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    existing_profile = db.query(
        StudentProfile
    ).filter(
        StudentProfile.user_id == current_user.id
    ).first()

    if existing_profile:

        raise HTTPException(
            status_code=400,
            detail="Profile already exists"
        )

    profile = StudentProfile(
        user_id=current_user.id,
        class_name=profile_data.class_name,
        board=profile_data.board,
        preferred_language=profile_data.preferred_language
    )

    db.add(profile)

    db.commit()

    db.refresh(profile)

    return profile


@router.get(
    "/profile",
    response_model=ProfileResponse
)
def get_profile(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    profile = db.query(
        StudentProfile
    ).filter(
        StudentProfile.user_id == current_user.id
    ).first()

    if not profile:

        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    return profile


@router.put(
    "/profile",
    response_model=ProfileResponse
)
def update_profile(
    profile_data: ProfileCreate,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    profile = db.query(
        StudentProfile
    ).filter(
        StudentProfile.user_id == current_user.id
    ).first()

    if not profile:

        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    profile.class_name = (
        profile_data.class_name
    )

    profile.board = (
        profile_data.board
    )

    profile.preferred_language = (
        profile_data.preferred_language
    )

    db.commit()

    db.refresh(profile)

    return profile