from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User, Role as RoleModel, Organization as OrganizationModel
from app.schemas.user import UserCreate, UserUpdate, User as UserSchema, RoleCreate, Role as RoleSchema, OrganizationCreate, Organization
from app.services.auth import get_current_user, get_password_hash

router = APIRouter(prefix="/api/system", tags=["系统管理"])


@router.get("/users", response_model=List[UserSchema])
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权访问")
    
    query = db.query(User)
    total = query.count()
    users = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return users


@router.post("/users", response_model=UserSchema)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建用户"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权访问")
    
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 验证邮箱格式（如果提供了邮箱）
    if user_data.email and user_data.email.strip():
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, user_data.email.strip()):
            raise HTTPException(status_code=400, detail="邮箱格式不正确")
    
    # 创建用户
    user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        real_name=user_data.real_name,
        employee_id=user_data.employee_id.strip() if user_data.employee_id else None,
        email=user_data.email.strip() if user_data.email else None,
        phone=user_data.phone.strip() if user_data.phone else None,
        role_id=user_data.role_id,
        org_id=user_data.org_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.put("/users/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权访问")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新用户信息
    if user_data.real_name is not None:
        user.real_name = user_data.real_name
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.phone is not None:
        user.phone = user_data.phone
    if user_data.role_id is not None:
        user.role_id = user_data.role_id
    if user_data.org_id is not None:
        user.org_id = user_data.org_id
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除用户"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权访问")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    db.delete(user)
    db.commit()
    
    return {"message": "用户已删除"}


@router.post("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """重置用户密码为123456"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权访问")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 重置密码为123456
    new_password = "123456"
    password_hash = get_password_hash(new_password)
    user.password_hash = password_hash
    
    db.commit()
    
    return {
        "message": "密码重置成功",
        "new_password": new_password
    }


@router.get("/roles", response_model=List[RoleSchema])
async def get_roles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取角色列表"""
    roles = db.query(RoleModel).all()
    return roles


@router.post("/roles", response_model=RoleSchema)
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建角色"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权访问")
    
    # 如果是超级管理员，默认拥有所有菜单权限
    permissions = role_data.permissions
    if role_data.name == '超级管理员':
        permissions = [
            'dashboard',
            'green-identify-pending',
            'green-identify-completed',
            'green-identify-archived',
            'green-identify-query',
            'system-user',
            'system-role',
            'system-org',
            'workflow-management',
            'workflow-instances'
        ]
    
    role = RoleModel(
        name=role_data.name,
        description=role_data.description,
        permissions=permissions
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    
    return role


@router.get("/roles/{role_id}", response_model=RoleSchema)
async def get_role_detail(
    role_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取角色详情"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权访问")
    
    role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    return role


@router.put("/roles/{role_id}", response_model=RoleSchema)
async def update_role(
    role_id: int,
    role_data: RoleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新角色"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权访问")
    
    role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 更新角色信息
    role.name = role_data.name
    role.description = role_data.description
    role.permissions = role_data.permissions
    
    db.commit()
    db.refresh(role)
    
    return role


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除角色"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权访问")
    
    role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 检查是否有用户使用该角色
    user_count = db.query(User).filter(User.role_id == role_id).count()
    if user_count > 0:
        raise HTTPException(status_code=400, detail=f"该角色下还有{user_count}个用户，无法删除")
    
    db.delete(role)
    db.commit()
    
    return {"message": "角色已删除"}


@router.get("/organizations")
async def get_organizations(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000),
    name: Optional[str] = Query(None),
    code: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取机构列表"""
    # 权限检查
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权访问")
    
    from app.models.user import Organization as OrganizationModel
    query = db.query(OrganizationModel)
    
    # 查询条件
    if name:
        query = query.filter(OrganizationModel.name.like(f"%{name}%"))
    if code:
        query = query.filter(OrganizationModel.code.like(f"%{code}%"))
    
    # 获取总数
    total = query.count()
    
    # 分页
    offset = (page - 1) * page_size
    orgs = query.offset(offset).limit(page_size).all()
    
    # 转换为字典列表
    org_list = []
    for org in orgs:
        org_dict = {
            "id": org.id,
            "name": org.name,
            "code": org.code,
            "parent_id": org.parent_id,
            "level": org.level,
            "is_active": bool(org.is_active) if org.is_active is not None else True,
            "created_at": org.created_at.isoformat() if org.created_at else None
        }
        org_list.append(org_dict)
    
    return {
        "data": org_list,
        "total": total
    }


@router.post("/organizations", response_model=Organization)
async def create_organization(
    org_data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建机构"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权访问")
    
    # 检查机构代码是否已存在
    existing_org = db.query(OrganizationModel).filter(OrganizationModel.code == org_data.code).first()
    if existing_org:
        raise HTTPException(
            status_code=400,
            detail=f"机构代码 '{org_data.code}' 已存在"
        )
    
    # 检查父机构是否存在
    if org_data.parent_id:
        parent_org = db.query(OrganizationModel).filter(OrganizationModel.id == org_data.parent_id).first()
        if not parent_org:
            raise HTTPException(
                status_code=400,
                detail=f"父机构不存在"
            )
    
    try:
        org = OrganizationModel(
            name=org_data.name,
            code=org_data.code,
            parent_id=org_data.parent_id,
            level=org_data.level,
            address=org_data.address,
            is_active=True
        )
        db.add(org)
        db.commit()
        db.refresh(org)
        
        return org
    except Exception as e:
        db.rollback()
        if "Duplicate entry" in str(e):
            if "code" in str(e):
                raise HTTPException(
                    status_code=400,
                    detail="机构代码已存在"
                )
        raise HTTPException(
            status_code=500,
            detail=f"创建机构失败: {str(e)}"
        )