from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from datetime import datetime

from app.database import get_db
from app.models.announcement import Announcement
from app.schemas.announcement import AnnouncementCreate, AnnouncementUpdate, Announcement as AnnouncementSchema
from app.routers.auth import get_current_user
from app.schemas.user import User

router = APIRouter(prefix="/api/announcements", tags=["announcements"])

# 上传目录
UPLOAD_DIR = "uploads/announcements"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/", response_model=List[AnnouncementSchema])
async def get_announcements(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """获取公告列表"""
    query = db.query(Announcement)
    if is_active is not None:
        query = query.filter(Announcement.is_active == is_active)
    announcements = query.order_by(Announcement.display_order, Announcement.created_at.desc()).offset(skip).limit(limit).all()
    return announcements


@router.get("/{announcement_id}", response_model=AnnouncementSchema)
async def get_announcement(announcement_id: int, db: Session = Depends(get_db)):
    """获取公告详情"""
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="公告不存在")
    return announcement


@router.post("/", response_model=AnnouncementSchema)
async def create_announcement(
    announcement: AnnouncementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建公告"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权访问")
    
    db_announcement = Announcement(
        **announcement.dict(),
        created_by=current_user.id
    )
    db.add(db_announcement)
    db.commit()
    db.refresh(db_announcement)
    return db_announcement


@router.put("/{announcement_id}", response_model=AnnouncementSchema)
async def update_announcement(
    announcement_id: int,
    announcement: AnnouncementUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新公告"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权访问")
    
    db_announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not db_announcement:
        raise HTTPException(status_code=404, detail="公告不存在")
    
    update_data = announcement.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_announcement, key, value)
    
    db.commit()
    db.refresh(db_announcement)
    return db_announcement


@router.delete("/{announcement_id}")
async def delete_announcement(
    announcement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除公告"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权访问")
    
    db_announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not db_announcement:
        raise HTTPException(status_code=404, detail="公告不存在")
    
    # 删除封面图片
    if db_announcement.cover_image:
        image_path = db_announcement.cover_image.replace("/uploads/announcements/", UPLOAD_DIR + "/")
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.delete(db_announcement)
    db.commit()
    return {"message": "删除成功"}


@router.get("/scroll/active", response_model=List[AnnouncementSchema])
async def get_scroll_announcements(db: Session = Depends(get_db)):
    """获取启用的公告用于滚动展示"""
    announcements = db.query(Announcement).filter(
        Announcement.is_active == True
    ).order_by(Announcement.display_order, Announcement.created_at.desc()).all()
    return announcements


@router.post("/upload")
async def upload_cover_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传封面图片"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权访问")
    
    # 生成唯一文件名
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # 返回访问URL
    return {"url": f"/uploads/announcements/{unique_filename}"}