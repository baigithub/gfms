"""
绿色金融管理系统 - 数据库初始化脚本
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.user import User, Role, Organization
from app.models.green_finance import GreenLoanIndicator
from app.services.auth import get_password_hash
from datetime import datetime
from decimal import Decimal

# 创建数据库引擎
engine = create_engine(settings.DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

# 创建表
from app.database import Base
Base.metadata.create_all(bind=engine)

def init_roles():
    """初始化角色"""
    db = SessionLocal()
    try:
        roles = [
            Role(name="超级管理员", description="系统超级管理员，拥有所有权限"),
            Role(name="客户经理", description="负责绿色贷款认定的发起"),
            Role(name="绿色金融管理岗", description="负责绿色贷款审核"),
            Role(name="绿色金融复核岗", description="负责绿色贷款最终审批"),
            Role(name="普通用户", description="普通系统用户")
        ]
        
        for role in roles:
            existing = db.query(Role).filter(Role.name == role.name).first()
            if not existing:
                db.add(role)
        
        db.commit()
        print("角色初始化完成")
    finally:
        db.close()

def init_organizations():
    """初始化机构"""
    db = SessionLocal()
    try:
        # 创建总行
        hq = Organization(
            name="总行",
            code="HQ",
            level=1,
            address="北京市",
            is_active=True
        )
        db.add(hq)
        db.flush()
        
        # 创建一级分行
        branches = [
            {"name": "一级分行A", "code": "BRANCH_A", "level": 2},
            {"name": "一级分行B", "code": "BRANCH_B", "level": 2},
            {"name": "一级分行C", "code": "BRANCH_C", "level": 2}
        ]
        
        for branch in branches:
            org = Organization(
                name=branch["name"],
                code=branch["code"],
                level=branch["level"],
                parent_id=hq.id,
                is_active=True
            )
            db.add(org)
            db.flush()
            
            # 创建二级支行
            for i in range(1, 3):
                sub_branch = Organization(
                    name=f"{branch['name']}_支行{i}",
                    code=f"{branch['code']}_SUB{i}",
                    level=3,
                    parent_id=org.id,
                    is_active=True
                )
                db.add(sub_branch)
        
        db.commit()
        print("机构初始化完成")
    finally:
        db.close()

def init_users():
    """初始化用户"""
    db = SessionLocal()
    try:
        # 获取角色和机构
        admin_role = db.query(Role).filter(Role.name == "超级管理员").first()
        manager_role = db.query(Role).filter(Role.name == "客户经理").first()
        review_role = db.query(Role).filter(Role.name == "绿色金融管理岗").first()
        audit_role = db.query(Role).filter(Role.name == "绿色金融复核岗").first()
        
        hq = db.query(Organization).filter(Organization.code == "HQ").first()
        
        # 创建超级管理员
        admin = User(
            username="admin",
            password_hash=get_password_hash("admin123"),
            real_name="系统管理员",
            employee_id="ADMIN001",
            email="admin@greenfinance.com",
            phone="13800138000",
            role_id=admin_role.id,
            org_id=hq.id,
            is_superuser=True,
            is_active=True
        )
        db.add(admin)
        
        # 创建测试用户
        users = [
            {
                "username": "manager1",
                "password": "manager123",
                "real_name": "张经理",
                "employee_id": "MGR001",
                "role": manager_role,
                "role_name": "客户经理"
            },
            {
                "username": "reviewer1",
                "password": "reviewer123",
                "real_name": "李审核",
                "employee_id": "REV001",
                "role": review_role,
                "role_name": "绿色金融管理岗"
            },
            {
                "username": "auditor1",
                "password": "auditor123",
                "real_name": "王审批",
                "employee_id": "AUD001",
                "role": audit_role,
                "role_name": "绿色金融复核岗"
            }
        ]
        
        for user_data in users:
            existing = db.query(User).filter(User.username == user_data["username"]).first()
            if not existing:
                user = User(
                    username=user_data["username"],
                    password_hash=get_password_hash(user_data["password"]),
                    real_name=user_data["real_name"],
                    employee_id=user_data["employee_id"],
                    email=f"{user_data['username']}@greenfinance.com",
                    phone=f"139{user_data['employee_id'][3:]}",
                    role_id=user_data["role"].id,
                    org_id=hq.id,
                    is_superuser=False,
                    is_active=True
                )
                db.add(user)
                print(f"创建用户: {user_data['real_name']} ({user_data['role_name']}) - 账号: {user_data['username']} / 密码: {user_data['password']}")
        
        db.commit()
        print("用户初始化完成")
    finally:
        db.close()

def init_indicators():
    """初始化绿色贷款指标数据"""
    db = SessionLocal()
    try:
        hq = db.query(Organization).filter(Organization.code == "HQ").first()
        
        # 创建示例指标数据
        indicator = GreenLoanIndicator(
            stat_date=datetime(2025, 11, 1),
            org_id=hq.id,
            green_loan_balance=Decimal("1000000000.00"),  # 10亿元
            green_loan_ratio=Decimal("15.50"),
            customer_count=552,
            growth_rate=Decimal("-78.26"),
            green_investment=Decimal("123000000.00"),  # 1.23亿元
            green_leasing=Decimal("100000000.00"),  # 1亿元
            green_wealth_management=Decimal("100000000.00"),  # 1亿元
            green_underwriting=Decimal("1111000000.00")  # 11.11亿元
        )
        db.add(indicator)
        
        db.commit()
        print("指标数据初始化完成")
    finally:
        db.close()

if __name__ == "__main__":
    print("开始初始化数据库...")
    print("=" * 50)
    
    init_roles()
    init_organizations()
    init_users()
    init_indicators()
    
    print("=" * 50)
    print("数据库初始化完成！")
    print("\n默认登录账号:")
    print("  超级管理员: admin / admin123")
    print("  客户经理: manager1 / manager123")
    print("  绿色金融管理岗: reviewer1 / reviewer123")
    print("  绿色金融复核岗: auditor1 / auditor123")
