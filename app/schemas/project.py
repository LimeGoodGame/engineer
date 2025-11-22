from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DocumentBase(BaseModel):
    filename: str
    original_filename: str
    file_type: str
    file_size: int


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: int
    project_id: int
    upload_status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    documents: List[DocumentResponse] = []

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_projects: int
    total_checks: int
    recent_projects: List[ProjectResponse]