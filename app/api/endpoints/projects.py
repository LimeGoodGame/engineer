from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from app.database import get_db
from app.auth.dependencies import get_current_user
# from app import models_user, crud
from app.crud import project as crud_project
from app.models_user import user as models_user
from app.schemas import project as schemas_project
from app.core.config import settings

router = APIRouter()


@router.get("/dashboard", response_model=schemas_project.DashboardStats)
def get_dashboard(
        current_user: models_user.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    return crud_project.get_dashboard_stats(db, current_user.id)


@router.get("/projects", response_model=List[schemas_project.ProjectResponse])
def get_projects(
        skip: int = 0,
        limit: int = 10,
        current_user: models_user.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    return crud_project.get_user_projects(db, current_user.id, skip, limit)


@router.post("/projects", response_model=schemas_project.ProjectResponse)
def create_project(
        project: schemas_project.ProjectCreate,
        current_user: models_user.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    return crud_project.create_project(db, project, current_user.id)


@router.post("/projects/{project_id}/documents")
async def upload_document(
        project_id: int,
        files: List[UploadFile] = File(...),
        current_user: models_user.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # Check if project exists and belongs to user
    project = crud_project.get_project_by_id(db, project_id, current_user.id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Validate file count
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 files allowed per upload"
        )

    uploaded_documents = []

    for file in files:
        # Validate file size (50MB max)
        content = await file.read()
        if len(content) > 50 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {file.filename} exceeds 50MB limit"
            )

        # Validate file type
        allowed_extensions = {'.dwg', '.dxf', '.3d', '.pdf', '.step', '.stp', '.iges', '.igs'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_extension} not supported"
            )

        # Generate unique filename
        file_uid = str(uuid.uuid4())
        filename = f"{file_uid}{file_extension}"
        file_path = f"uploads/{filename}"

        # Save file (in production, use cloud storage)
        os.makedirs("uploads", exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(content)

        # Create document record
        document_data = schemas_project.DocumentCreate(
            filename=filename,
            original_filename=file.filename,
            file_type=file_extension[1:],  # Remove dot
            file_size=len(content)
        )

        document = crud_project.create_document(db, document_data, project_id)
        uploaded_documents.append(document)

    return {"message": f"Successfully uploaded {len(uploaded_documents)} files", "documents": uploaded_documents}