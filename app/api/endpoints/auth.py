from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.core.config import settings
from app.crud import user as user_crud
from app.schemas.user import UserCreate, UserResponse, Token, PasswordResetRequest, PasswordReset
from app.auth.utils import create_access_token, get_password_hash

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return user_crud.create_user(db=db, user=user)


@router.post("/login", response_model=Token)
def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user = user_crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/password-reset-request")
def password_reset_request(request: PasswordResetRequest, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_email(db, email=request.email)
    if user:
        # In production, send email with reset link
        token = user_crud.create_password_reset_token(db, request.email)
        # Here you would typically send an email with the reset token
        return {"message": "If the email exists, a reset link has been sent"}
    # For security, don't reveal if email exists or not
    return {"message": "If the email exists, a reset link has been sent"}

@router.post("/password-reset")
def password_reset(reset_data: PasswordReset, db: Session = Depends(get_db)):
    email = user_crud.verify_password_reset_token(db, reset_data.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    user = user_crud.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    user.hashed_password = get_password_hash(reset_data.new_password)
    user_crud.delete_password_reset_token(db, reset_data.token)
    db.commit()

    return {"message": "Password reset successfully"}