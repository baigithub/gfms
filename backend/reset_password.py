"""
重置 tyyzy 用户的密码
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.services.auth import get_password_hash

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def reset_password():
    """重置用户密码"""
    db = SessionLocal()
    try:
        # 查找 tyyzy 用户
        user = db.execute(text("""
            SELECT id, username, real_name
            FROM users 
            WHERE username = 'tyyzy'
        """)).fetchone()
        
        if not user:
            print("✗ 未找到用户 tyyzy")
            return
        
        # 重置密码为 123456
        new_password = "123456"
        password_hash = get_password_hash(new_password)
        
        db.execute(text("""
            UPDATE users 
            SET password_hash = :password_hash
            WHERE username = 'tyyzy'
        """), {"password_hash": password_hash})
        
        db.commit()
        
        print("✓ 密码重置成功")
        print(f"\n用户: {user[2]} ({user[1]})")
        print(f"新密码: {new_password}")
        print("\n请使用以下信息登录：")
        print(f"  用户名: {user[1]}")
        print(f"  密码: {new_password}")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_password()