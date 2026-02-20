"""
为绿色认定任务创建工作流实例和任务（使用原始SQL）
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
from datetime import datetime

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def create_workflow_tasks():
    """创建工作流实例和任务"""
    db = SessionLocal()
    try:
        # 1. 获取所有待办的绿色认定任务
        identifications = db.execute(text("""
            SELECT id, loan_code, customer_name, initiator_id
            FROM green_identifications
            WHERE status = '待办'
            ORDER BY id
        """)).fetchall()
        
        print(f"找到 {len(identifications)} 条待办的绿色认定任务")
        
        # 2. 获取流程定义（使用第一个启用的流程定义）
        definition = db.execute(text("""
            SELECT id, name, version
            FROM process_definitions
            WHERE status = 'active'
            ORDER BY id
            LIMIT 1
        """)).fetchone()
        
        if not definition:
            print("✗ 未找到启用的流程定义")
            return
        
        print(f"使用流程定义: {definition[1]} (ID: {definition[0]}, 版本: {definition[2]})")
        
        # 3. 为每个绿色认定创建工作流实例和任务
        created_count = 0
        for ident in identifications:
            ident_id = ident[0]  # ID
            loan_code = ident[1]  # loan_code
            initiator_id = ident[3]  # initiator_id (索引3，不是2)
            
            # 创建工作流实例
            case_id = f"CASE_{loan_code}"
            
            # 检查是否已存在工作流实例
            existing = db.execute(text(f"""
                SELECT id FROM workflow_instances 
                WHERE identification_id = {ident_id}
            """)).fetchone()
            
            if existing:
                print(f"  跳过 ID {ident_id}: 已存在工作流实例")
                continue
            
            # 插入工作流实例
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            db.execute(text(f"""
                INSERT INTO workflow_instances 
                (case_id, process_key, business_key, status, started_at, identification_id)
                VALUES 
                ('{case_id}', 'green_identification_process', '{loan_code}', '审批中', 
                 '{now}', {ident_id})
            """))
            
            instance_id = db.execute(text("SELECT LAST_INSERT_ID()")).fetchone()[0]
            
            # 创建工作流任务（客户经理提交）
            db.execute(text(f"""
                INSERT INTO workflow_tasks 
                (task_key, task_name, node_id, assignee_id, status, 
                 started_at, workflow_instance_id, identification_id)
                VALUES 
                ('manager_identification', '客户经理认定', 'Task_1', {initiator_id}, 
                 '待处理', '{now}', {instance_id}, {ident_id})
            """))
            
            created_count += 1
            print(f"  ✓ 创建工作流: {loan_code} (实例ID: {instance_id})")
        
        db.commit()
        print(f"\n✓ 成功创建 {created_count} 个工作流实例和任务")
        
        # 4. 验证结果
        print(f"\n=== 验证结果 ===")
        tasks = db.execute(text(f"""
            SELECT wt.id, wt.task_name, wt.assignee_id, wt.status, 
                   gi.loan_code, gi.customer_name
            FROM workflow_tasks wt
            JOIN workflow_instances wi ON wt.workflow_instance_id = wi.id
            JOIN green_identifications gi ON wi.identification_id = gi.id
            WHERE wt.assignee_id = 5
            ORDER BY wt.id DESC
            LIMIT 10
        """)).fetchall()
        
        if not tasks:
            print("用户 tyyzy 没有待办任务")
        else:
            print(f"{'ID':<5} {'任务名称':<15} {'状态':<10} {'贷款编号':<20} {'客户名称':<25}")
            print("-" * 85)
            for task in tasks:
                print(f"{task[0]:<5} {task[1]:<15} {task[2]:<10} {task[3]:<20} {task[4]:<25}")
            
            print(f"\n总计: {len(tasks)} 条待办任务")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_workflow_tasks()
