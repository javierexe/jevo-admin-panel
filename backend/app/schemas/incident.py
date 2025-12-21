from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid


class IncidentBase(BaseModel):
    project: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    status: Optional[str] = Field(default="open", pattern="^(open|in_progress|resolved)$")


class IncidentCreate(IncidentBase):
    image_url: Optional[str] = None
    video_url: Optional[str] = None


class IncidentUpdate(BaseModel):
    project: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    status: Optional[str] = Field(None, pattern="^(open|in_progress|resolved)$")
    internal_comment: Optional[str] = None
    resolved_at: Optional[datetime] = None


class IncidentResponse(IncidentBase):
    id: uuid.UUID
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    internal_comment: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
