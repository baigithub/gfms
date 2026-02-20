from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import uuid
from datetime import datetime
import aiofiles

from app.database import get_db
from app.models.user import User
from app.services.auth import get_current_user
from app.config import settings

router = APIRouter(prefix="/api/files", tags=["文件管理"])

# 上传文件存储目录
UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx', '.xls', '.xlsx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return os.path.splitext(filename)[1].lower()


def is_allowed_file(filename: str) -> bool:
    """检查文件类型是否允许"""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    task_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传文件"""
    try:
        # 检查文件扩展名
        if not is_allowed_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型。允许的类型: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # 读取文件内容
        content = await file.read()
        
        # 检查文件大小
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制。最大允许 {MAX_FILE_SIZE / (1024 * 1024)}MB"
            )
        
        # 创建上传目录
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # 生成唯一文件名
        file_ext = get_file_extension(file.filename)
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # 保存文件
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # 如果提供了 task_id，保存附件信息到数据库
        attachment_id = None
        if task_id:
            from app.models.green_finance import WorkflowTask, TaskAttachment
            
            task = db.query(WorkflowTask).filter(WorkflowTask.id == task_id).first()
            if task:
                attachment = TaskAttachment(
                    task_id=task_id,
                    uploader_id=current_user.id,
                    original_filename=file.filename,
                    stored_filename=unique_filename,
                    file_size=len(content),
                    file_path=file_path,
                    download_url=f"/api/files/download/{unique_filename}",
                    task_key=task.task_key,
                    task_name=task.task_name
                )
                db.add(attachment)
                db.commit()
                db.refresh(attachment)
                attachment_id = attachment.id
        
        # 返回文件信息
        return JSONResponse({
            "code": 0,
            "success": True,
            "message": "文件上传成功",
            "data": {
                "filename": unique_filename,
                "original_filename": file.filename,
                "url": f"/api/files/download/{unique_filename}",
                "size": len(content),
                "upload_time": datetime.now().isoformat(),
                "attachment_id": attachment_id
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"文件上传失败: {str(e)}"
        )


@router.get("/download/{filename}")
async def download_file(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """下载文件"""
    from fastapi.responses import FileResponse
    
    print(f"DEBUG: Download file request - filename={filename}, user={current_user.username}")
    
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="文件不存在"
        )
    
    # 检查文件扩展名是否允许
    if not is_allowed_file(filename):
        raise HTTPException(
            status_code=403,
            detail="不允许访问该文件类型"
        )
    
    return FileResponse(
        file_path,
        media_type='application/octet-stream',
        filename=filename
    )


@router.get("/attachments/identification/{identification_id}")
async def get_attachments_by_identification(
    identification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取某个认定记录的所有附件"""
    from app.models.green_finance import TaskAttachment, WorkflowTask
    
    attachments = db.query(TaskAttachment).join(
        WorkflowTask, TaskAttachment.task_id == WorkflowTask.id
    ).filter(
        WorkflowTask.identification_id == identification_id
    ).order_by(TaskAttachment.created_at).all()
    
    result = []
    for attachment in attachments:
        result.append({
            "id": attachment.id,
            "task_id": attachment.task_id,
            "task_key": attachment.task_key,
            "task_name": attachment.task_name,
            "uploader_id": attachment.uploader_id,
            "uploader_name": attachment.uploader.real_name if attachment.uploader else "",
            "original_filename": attachment.original_filename,
            "stored_filename": attachment.stored_filename,
            "file_size": attachment.file_size,
            "download_url": attachment.download_url,
            "created_at": attachment.created_at.isoformat() if attachment.created_at else None
        })
    
    return JSONResponse({
        "code": 0,
        "success": True,
        "data": result
    })


@router.delete("/delete/{filename}")
async def delete_file(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """删除文件"""
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="文件不存在"
        )
    
    try:
        os.remove(file_path)
        return JSONResponse({
            "code": 0,
            "success": True,
            "message": "文件删除成功"
        })
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"文件删除失败: {str(e)}"
        )