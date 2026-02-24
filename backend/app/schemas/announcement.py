from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AnnouncementBase(BaseModel):
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    cover_image: Optional[str] = None
    remarks: Optional[str] = None
    is_active: Optional[bool] = True
    display_order: Optional[int] = 0


class AnnouncementCreate(AnnouncementBase):
    pass


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    cover_image: Optional[str] = None
    remarks: Optional[str] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None


class Announcement(AnnouncementBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    
    class Config:
        from_attributes = True