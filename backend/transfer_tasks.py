"""
将任务转移到工号1001的用户名下，并删除刚创建的用户
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def transfer_and_cleanup():
    """转移任务并清理用户"""
    db = SessionLocal()
    try:
        # 1. 查找工号为10001的用户
        user = db.execute(text("SELECT id, username, real_name, employee_id FROM users WHERE employee_id = '10001'")).fetchone()
        
        if not user:
            print("✗ 未找到工号为10001的用户")
            return
        
        user_id = user[0]
        print(f"找到工号为10001的用户: {user[2]} ({user[1]}) - ID: {user_id}")
        
        # 2. 将所有任务的发起人ID改为工号10001的用户ID
        result = db.execute(text("""
            UPDATE green_identifications 
            SET initiator_id = :user_id
            WHERE initiator_id = 1001
        """), {"user_id": user_id})
        
        updated_count = result.rowcount
        print(f"✓ 已将 {updated_count} 条任务的发起人改为工号10001的用户")
        
        # 3. 删除刚创建的用户（ID=1001）
        db.execute(text("DELETE FROM users WHERE id = 1001"))
        print("✓ 已删除刚创建的用户（ID=1001）")
        
        db.commit()
        print("\n✓ 操作完成")
        
        # 4. 验证结果
        print("\n=== 验证结果 ===")
        tasks = db.execute(text("""
            SELECT id, loan_code, customer_name, initiator_id
            FROM green_identifications
            ORDER BY id DESC
            LIMIT 10
        """)).fetchall()
        
        print(f"{'ID':<5} {'贷款编号':<20} {'客户名称':<25} {'发起人ID':<10}")
        print("-" * 70)
        for task in tasks:
            print(f"{task[0]:<5} {task[1]:<20} {task[2]:<25} {task[3]:<10}")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    transfer_and_cleanup()