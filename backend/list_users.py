"""
列出所有用户
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def list_users():
    """列出所有用户"""
    db = SessionLocal()
    try:
        users = db.execute(text("""
            SELECT id, username, real_name, employee_id, role_id
            FROM users
            ORDER BY id
        """)).fetchall()
        
        print("=== 所有用户 ===")
        print(f"{'ID':<5} {'用户名':<20} {'姓名':<15} {'工号':<10} {'角色ID':<10}")
        print("-" * 70)
        
        for user in users:
            print(f"{user[0]:<5} {user[1]:<20} {user[2]:<15} {user[3]:<10} {user[4]:<10}")
        
        print(f"\n总计: {len(users)} 个用户")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    list_users()