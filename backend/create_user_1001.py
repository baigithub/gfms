"""
创建用户1001（客户经理）
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.services.auth import get_password_hash

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def create_user_1001():
    """创建用户1001"""
    db = SessionLocal()
    try:
        # 检查用户是否已存在
        existing = db.execute(text("SELECT id FROM users WHERE id = 1001")).fetchone()
        if existing:
            print("用户1001已存在")
            return
        
        # 获取客户经理角色
        role = db.execute(text("SELECT id FROM roles WHERE name LIKE '%客户经理%'")).fetchone()
        if not role:
            print("未找到客户经理角色")
            return
        
        role_id = role[0]
        
        # 获取总行机构
        org = db.execute(text("SELECT id FROM organizations WHERE code = 'HQ'")).fetchone()
        if not org:
            print("未找到总行机构")
            return
        
        org_id = org[0]
        
        # 创建用户
        password_hash = get_password_hash("user123")
        db.execute(text("""
            INSERT INTO users 
            (id, username, password_hash, real_name, employee_id, email, phone, 
             role_id, org_id, is_superuser, is_active, created_at)
            VALUES 
            (1001, 'manager1001', :password_hash, '客户经理1001', 'EMP1001', 
             'manager1001@greenfinance.com', '13900001001', :role_id, :org_id, 
             0, 1, NOW())
        """), {
            "password_hash": password_hash,
            "role_id": role_id,
            "org_id": org_id
        })
        
        db.commit()
        print("✓ 成功创建用户1001")
        print("  用户名: manager1001")
        print("  密码: user123")
        print("  角色: 客户经理")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_user_1001()