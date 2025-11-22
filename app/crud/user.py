from sqlalchemy.orm import Session
from app.models_user.user import User, PasswordResetToken
from app.schemas.user import UserCreate
from app.auth.utils import get_password_hash, verify_password
from datetime import datetime, timedelta
import secrets


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserCreate):
    # hashed_password = get_password_hash(user.password)

    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=user.password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    # if not verify_password(password, user.hashed_password):
    if user.hashed_password != password:
        return False
    return user


def create_password_reset_token(db: Session, email: str):
    # Delete any existing tokens for this email
    db.query(PasswordResetToken).filter(PasswordResetToken.email == email).delete()

    # Create new token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=24)

    db_token = PasswordResetToken(
        email=email,
        token=token,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    return token


def verify_password_reset_token(db: Session, token: str):
    db_token = db.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()
    if not db_token or db_token.expires_at < datetime.utcnow():
        return None
    return db_token.email


def delete_password_reset_token(db: Session, token: str):
    db.query(PasswordResetToken).filter(PasswordResetToken.token == token).delete()
    db.commit()