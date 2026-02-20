"""
检查所有任务的关联关系
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def check_all_relations():
    """检查所有任务的关联关系"""
    db = SessionLocal()
    try:
        print("=== 检查 workflow_tasks 和 green_identifications 的关联 ===")
        
        # 查询所有 workflow_tasks
        tasks = db.execute(text("""
            SELECT wt.id, wt.task_name, wt.assignee_id, wt.identification_id,
                   gi.id as gi_id, gi.loan_code
            FROM workflow_tasks wt
            LEFT JOIN green_identifications gi ON wt.identification_id = gi.id
            ORDER BY wt.id
            LIMIT 10
        """)).fetchall()
        
        print(f"{'Task ID':<10} {'任务名称':<20} {'处理人ID':<10} {'认定ID':<10} {'关联的认定ID':<15} {'贷款编号':<20}")
        print("-" * 95)
        
        for task in tasks:
            match = "✓" if task[4] else "✗"
            print(f"{task[0]:<10} {task[1]:<20} {task[2]:<10} {task[3]:<10} {match} {str(task[4]):<15} {task[5]:<20}")
        
        # 查询所有 green_identifications
        print(f"\n=== 所有 green_identifications ===")
        identifications = db.execute(text("""
            SELECT id, loan_code, customer_name, initiator_id, status
            FROM green_identifications
            ORDER BY id
            LIMIT 10
        """)).fetchall()
        
        print(f"{'ID':<5} {'贷款编号':<20} {'客户名称':<25} {'发起人ID':<10} {'状态':<10}")
        print("-" * 80)
        for ident in identifications:
            print(f"{ident[0]:<5} {ident[1]:<20} {ident[2]:<25} {ident[3]:<10} {ident[4]:<10}")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_all_relations()
