"""
查看工号10001的用户信息和任务
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def check_user_10001():
    """查看工号10001的用户"""
    db = SessionLocal()
    try:
        # 查找工号为10001的用户
        user = db.execute(text("""
            SELECT id, username, real_name, employee_id, 
                   role_id, is_active, created_at
            FROM users 
            WHERE employee_id = '10001'
        """)).fetchone()
        
        if not user:
            print("✗ 未找到工号为10001的用户")
            return
        
        print("=== 工号10001的用户信息 ===")
        print(f"ID: {user[0]}")
        print(f"用户名: {user[1]}")
        print(f"姓名: {user[2]}")
        print(f"工号: {user[3]}")
        print(f"角色ID: {user[4]}")
        print(f"是否激活: {'是' if user[5] else '否'}")
        print(f"创建时间: {user[6]}")
        
        # 查找角色名称
        role = db.execute(text("SELECT name FROM roles WHERE id = :role_id"), {"role_id": user[4]}).fetchone()
        if role:
            print(f"角色: {role[0]}")
        
        # 查询该用户的任务
        print("\n=== 该用户的任务 ===")
        tasks = db.execute(text("""
            SELECT id, loan_code, customer_name, business_type, 
                   loan_amount, status, created_at
            FROM green_identifications
            WHERE initiator_id = :user_id
            ORDER BY id DESC
        """), {"user_id": user[0]}).fetchall()
        
        if not tasks:
            print("无任务")
        else:
            print(f"{'ID':<5} {'贷款编号':<20} {'客户名称':<25} {'金额(元)':<15} {'状态':<10}")
            print("-" * 85)
            
            for task in tasks:
                print(f"{task[0]:<5} {task[1]:<20} {task[2]:<25} {task[4]:<15,} {task[5]:<10}")
            
            print(f"\n总计: {len(tasks)} 条任务")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_user_10001()
