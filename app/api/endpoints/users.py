from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.schemas import user as user_schemas
from app.models_user import user as user_models
router = APIRouter()

@router.get("/me", response_model=user_schemas.UserResponse)
def read_users_me(current_user: user_models.User = Depends(get_current_user)):
    return current_user