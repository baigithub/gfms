"""
查看用户密码哈希
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def check_password():
    """查看用户密码哈希"""
    db = SessionLocal()
    try:
        # 查找 tyyzy 用户
        user = db.execute(text("""
            SELECT id, username, real_name, password_hash
            FROM users 
            WHERE username = 'tyyzy'
        """)).fetchone()
        
        if not user:
            print("✗ 未找到用户 tyyzy")
            return
        
        print("=== 用户信息 ===")
        print(f"ID: {user[0]}")
        print(f"用户名: {user[1]}")
        print(f"姓名: {user[2]}")
        print(f"密码哈希: {user[3][:50]}...")  # 只显示前50个字符
        print("\n注意：密码是加密存储的，无法直接查看明文密码。")
        print("如果需要重置密码，可以运行重置密码脚本。")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_password()
