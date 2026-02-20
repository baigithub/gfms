"""
为绿色认定任务创建工作流实例和任务
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
        
        # 打印前几条记录，确保数据正确
        print("\n绿色认定任务样例:")
        for ident in identifications[:3]:
            print(f"  ID: {ident[0]}, 贷款编号: {ident[1]}, 客户名称: {ident[2]}, 发起人ID: {ident[3]}")
        
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
            ident_id = ident[0]
            loan_code = ident[1]
            initiator_id = ident[2]
            
            # 创建工作流实例
            case_id = f"CASE_{loan_code}"
            
            # 检查是否已存在工作流实例
            existing = db.execute(text("""
                SELECT id FROM workflow_instances 
                WHERE identification_id = :ident_id
            """), {"ident_id": ident_id}).fetchone()
            
            if existing:
                print(f"  跳过 ID {ident_id}: 已存在工作流实例")
                continue
            
            # 插入工作流实例
            db.execute(text("""
                INSERT INTO workflow_instances 
                (case_id, process_key, business_key, status, started_at, identification_id)
                VALUES 
                (:case_id, 'green_identification_process', :business_key, '审批中', 
                 :started_at, :identification_id)
            """), {
                "case_id": case_id,
                "business_key": loan_code,
                "started_at": datetime.now(),
                "identification_id": ident_id
            })
            
            instance_id = db.execute(text("SELECT LAST_INSERT_ID()")).fetchone()[0]
            
            # 创建工作流任务（客户经理提交）
            db.execute(text("""
                INSERT INTO workflow_tasks 
                (task_key, task_name, node_id, assignee_id, status, 
                 started_at, workflow_instance_id, identification_id)
                VALUES 
                ('manager_identification', '客户经理认定', 'Task_1', %s, 
                 '待处理', %s, %s, %s)
            """), (
                initiator_id,
                datetime.now(),
                instance_id,
                ident_id
            ))
            
            created_count += 1
            print(f"  ✓ 创建工作流: {loan_code} (实例ID: {instance_id})")
        
        db.commit()
        print(f"\n✓ 成功创建 {created_count} 个工作流实例和任务")
        
        # 4. 验证结果
        print(f"\n=== 验证结果 ===")
        tasks = db.execute(text("""
            SELECT wt.id, wt.task_name, wt.assignee_id, wt.status, 
                   gi.loan_code, gi.customer_name
            FROM workflow_tasks wt
            JOIN workflow_instances wi ON wt.workflow_instance_id = wi.id
            JOIN green_identifications gi ON wi.identification_id = gi.id
            WHERE wt.assignee_id = :user_id
            ORDER BY wt.id DESC
            LIMIT 10
        """), {"user_id": 5}).fetchall()
        
        if not tasks:
            print("用户 tyyzy 没有待办任务")
        else:
            print(f"{'ID':<5} {'任务名称':<15} {'状态':<10} {'贷款编号':<20} {'客户名称':<25}")
            print("-" * 85)
            for task in tasks:
                print(f"{task[0]:<5} {task[1]:<15} {task[2]:<10} {task[4]:<20} {task[5]:<25}")
            
            print(f"\n总计: {len(tasks)} 条待办任务")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_workflow_tasks()
