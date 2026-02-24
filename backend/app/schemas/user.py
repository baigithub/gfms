from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    username: str
    real_name: str
    employee_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    wechat_openid: Optional[str] = None
    wechat_unionid: Optional[str] = None
    role_id: Optional[int] = None
    org_id: Optional[int] = None
    
    class Config:
        # 将空字符串转换为None
        str_strip_whitespace = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    real_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    wechat_openid: Optional[str] = None
    wechat_unionid: Optional[str] = None
    role_id: Optional[int] = None
    org_id: Optional[int] = None
    is_active: Optional[bool] = None
    
    class Config:
        str_strip_whitespace = True


class UserInDB(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class User(UserInDB):
    permissions: Optional[List[str]] = []
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str
    captcha: Optional[str] = None  # 临时改为可选，方便性能测试


class Token(BaseModel):
    access_token: str
    token_type: str
    user: User


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: Optional[List[str]] = None


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrganizationBase(BaseModel):
    name: str
    code: str
    parent_id: Optional[int] = None
    level: int = 1
    address: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    pass


class Organization(OrganizationBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True