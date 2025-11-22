from sqlalchemy.orm import Session
from app.models_user.project import Project, Document
from app.schemas.project import ProjectCreate, DocumentCreate
from typing import List


def get_user_projects(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    return db.query(Project).filter(Project.user_id == user_id).offset(skip).limit(limit).all()

def get_project_by_id(db: Session, project_id: int, user_id: int):
    return db.query(Project).filter(Project.id == project_id, Project.user_id == user_id).first()

def create_project(db: Session, project: ProjectCreate, user_id: int):
    db_project = Project(**project.dict(), user_id=user_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def create_document(db: Session, document: DocumentCreate, project_id: int):
    db_document = Document(**document.dict(), project_id=project_id)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def get_recent_projects(db: Session, user_id: int, limit: int = 5):
    return db.query(Project).filter(Project.user_id == user_id).order_by(Project.created_at.desc()).limit(limit).all()

def get_dashboard_stats(db: Session, user_id: int):
    total_projects = db.query(Project).filter(Project.user_id == user_id).count()
    total_checks = total_projects
    recent_projects = get_recent_projects(db, user_id)
    return {
        "total_projects": total_projects,
        "total_checks": total_checks,
        "recent_projects": recent_projects
    }