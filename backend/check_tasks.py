"""
检查生成的任务
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def check_tasks():
    """检查任务"""
    db = SessionLocal()
    try:
        # 查询所有绿色认定任务
        tasks = db.execute(text("""
            SELECT id, loan_code, customer_name, business_type, 
                   loan_amount, status, initiator_id, created_at
            FROM green_identifications
            ORDER BY id DESC
            LIMIT 10
        """)).fetchall()
        
        print("=== 生成的绿色认定任务 ===")
        print(f"{'ID':<5} {'贷款编号':<20} {'客户名称':<25} {'金额(元)':<15} {'状态':<10} {'发起人ID':<10}")
        print("-" * 100)
        
        for task in tasks:
            print(f"{task[0]:<5} {task[1]:<20} {task[2]:<25} {task[4]:<15,} {task[5]:<10} {task[6]:<10}")
        
        print(f"\n总计: {len(tasks)} 条任务")
        
        # 查询发起人信息
        initiator = db.execute(text("SELECT id, username, real_name FROM users WHERE id = 1001")).fetchone()
        if initiator:
            print(f"\n发起人: {initiator[2]} ({initiator[1]}) - ID: {initiator[0]}")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_tasks()