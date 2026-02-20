"""
调试待办任务
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def debug_tasks():
    """调试待办任务"""
    db = SessionLocal()
    try:
        # 1. 查看 tyyzy 用户信息
        user = db.execute(text("""
            SELECT id, username, real_name, employee_id, role_id
            FROM users 
            WHERE username = 'tyyzy'
        """)).fetchone()
        
        if not user:
            print("✗ 未找到用户 tyyzy")
            return
        
        print(f"=== 用户信息 ===")
        print(f"ID: {user[0]}, 用户名: {user[1]}, 姓名: {user[2]}, 工号: {user[3]}, 角色ID: {user[4]}")
        
        # 2. 查看所有绿色认定任务
        print(f"\n=== 所有绿色认定任务 ===")
        tasks = db.execute(text("""
            SELECT id, loan_code, customer_name, initiator_id, status
            FROM green_identifications
            ORDER BY id DESC
            LIMIT 10
        """)).fetchall()
        
        print(f"{'ID':<5} {'贷款编号':<20} {'客户名称':<25} {'发起人ID':<10} {'状态':<10}")
        print("-" * 80)
        for task in tasks:
            print(f"{task[0]:<5} {task[1]:<20} {task[2]:<25} {task[3]:<10} {task[4]:<10}")
        
        # 3. 查看工作流任务
        print(f"\n=== 工作流任务 ===")
        workflow_tasks = db.execute(text("""
            SELECT id, task_name, assignee_id, status, identification_id
            FROM workflow_tasks
            ORDER BY id DESC
            LIMIT 10
        """)).fetchall()
        
        if not workflow_tasks:
            print("没有工作流任务记录")
        else:
            print(f"{'ID':<5} {'任务名称':<20} {'处理人ID':<10} {'状态':<10} {'认定ID':<10}")
            print("-" * 70)
            for task in workflow_tasks:
                print(f"{task[0]:<5} {task[1]:<20} {task[2]:<10} {task[3]:<10} {task[4]:<10}")
        
        # 4. 检查工作流实例
        print(f"\n=== 工作流实例 ===")
        instances = db.execute(text("""
            SELECT id, business_key, status, started_at
            FROM workflow_instances
            ORDER BY id DESC
            LIMIT 10
        """)).fetchall()
        
        if not instances:
            print("没有工作流实例记录")
        else:
            print(f"{'ID':<5} {'业务键':<20} {'状态':<10} {'开始时间':<20}")
            print("-" * 55)
            for inst in instances:
                print(f"{inst[0]:<5} {inst[1]:<20} {inst[2]:<10} {inst[3]}")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_tasks()