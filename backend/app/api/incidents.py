from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.incident import Incident
from app.models.user import User
from app.schemas.incident import IncidentResponse, IncidentUpdate
from app.services.upload import upload_file

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    project: str = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    status: str = Form(default="open"),
    image: Optional[UploadFile] = File(None),
    video: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new incident report with optional image and video files.
    """
    # Validate status
    if status not in ["open", "in_progress", "resolved"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be one of: open, in_progress, resolved"
        )
    
    # Upload files if provided
    image_url = None
    video_url = None
    
    try:
        if image:
            image_url = await upload_file(image)
        if video:
            video_url = await upload_file(video)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload files: {str(e)}"
        )
    
    # Create incident
    new_incident = Incident(
        project=project,
        category=category,
        description=description,
        status=status,
        image_url=image_url,
        video_url=video_url
    )
    
    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)
    
    return new_incident


@router.get("", response_model=List[IncidentResponse])
async def get_incidents(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    project: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a list of incidents with optional filtering.
    """
    query = db.query(Incident)
    
    if status:
        query = query.filter(Incident.status == status)
    if project:
        query = query.filter(Incident.project == project)
    
    incidents = query.order_by(Incident.created_at.desc()).offset(skip).limit(limit).all()
    return incidents


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific incident by ID.
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    return incident


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: uuid.UUID,
    incident_update: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing incident. Validates incident existence before updating.
    """
    # Find incident
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    # Update fields if provided
    update_data = incident_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(incident, field, value)
    
    # Auto-set resolved_at if status changes to resolved
    if incident_update.status == "resolved" and not incident.resolved_at:
        incident.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(incident)
    
    return incident
