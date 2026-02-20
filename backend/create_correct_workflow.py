"""
为申磊的10笔待办任务创建正确的工作流任务和工作流实例
"""
from sqlalchemy.orm import sessionmaker
from app.config import settings
from sqlalchemy import create_engine, text
from datetime import datetime

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def create_workflow_for_tasks():
    """为申磊的待办任务创建工作流"""
    db = SessionLocal()
    try:
        # 查询申磊用户
        user = db.execute(text("SELECT id, username, real_name FROM users WHERE username = 'fzxsl'")).fetchone()
        if not user:
            print("✗ 用户 fzxsl 不存在")
            return
        
        user_id = user[0]
        print(f"找到用户: {user[1]} ({user[2]}), ID: {user_id}")
        
        # 查询申磊发起的所有待办任务
        pending_tasks = db.execute(text('''
            SELECT id, loan_code, customer_name, loan_amount 
            FROM green_identifications 
            WHERE initiator_id = :user_id AND status = "待办"
            ORDER BY created_at DESC
        '''), {"user_id": user_id}).fetchall()
        
        print(f"\n找到 {len(pending_tasks)} 笔待办任务，需要创建工作流...")
        
        # 查询工作流实例（看看是否有现有实例）
        existing_instances = db.execute(text('''
            SELECT id, identification_id, status 
            FROM workflow_instances 
            WHERE identification_id IN (
                SELECT id FROM green_identifications WHERE initiator_id = :user_id AND status = "待办"
            )
        '''), {"user_id": user_id}).fetchall()
        
        if existing_instances:
            print(f"\\n注意：已有 {len(existing_instances)} 个工作流实例，将复用这些实例")
        
        # 为每个任务创建工作流任务
        for task in pending_tasks:
            identification_id = task[0]
            
            # 检查是否已有工作流实例
            existing_instance = db.execute(text('''
                SELECT id, status 
                FROM workflow_instances 
                WHERE identification_id = :identification_id
            '''), {"identification_id": identification_id}).fetchone()
            
            if existing_instance:
                instance_id = existing_instance[0]
                print(f"  ✓ 使用现有工作流实例 ID: {instance_id}")
            else:
                # 创建新的工作流实例
                instance_result = db.execute(text('''
                    INSERT INTO workflow_instances 
                    (identification_id, case_id, process_key, business_key, current_node, status, started_at)
                    VALUES 
                    (:identification_id, :case_id, :process_key, :business_key, :current_node, :status, :started_at)
                '''), {
                    "identification_id": identification_id,
                    "case_id": f"CASE{identification_id:06d}",
                    "process_key": "green_identification",
                    "business_key": task[1],  # loan_code
                    "current_node": "manager_identification",
                    "status": "进行中",
                    "started_at": datetime.now()
                })
                
                instance_id = instance_result.lastrowid
                print(f"  ✓ 创建工作流实例 ID: {instance_id}")
            
            # 创建工作流任务（客户经理认定节点）
            task_result = db.execute(text('''
                INSERT INTO workflow_tasks 
                (workflow_instance_id, identification_id, task_key, task_name, assignee_id, status, started_at)
                VALUES 
                (:workflow_instance_id, :identification_id, :task_key, :task_name, :assignee_id, :status, :started_at)
            '''), {
                "workflow_instance_id": instance_id,
                "identification_id": identification_id,
                "task_key": "manager_identification",
                "task_name": "客户经理认定",
                "assignee_id": user_id,  # 分配给申磊
                "status": "待处理",
                "started_at": datetime.now()
            })
            
            task_id = task_result.lastrowid
            print(f"    ✓ 创建工作流任务 ID: {task_id}, 分配给: {user[2]}")
        
        db.commit()
        print(f"\n✓ 成功为 {len(pending_tasks)} 笔任务创建工作流")
        
        # 验证创建的工作流任务
        print("\n验证创建的工作流任务...")
        workflow_tasks = db.execute(text('''
            SELECT wt.id, wt.task_key, wt.status, u.real_name as assignee_name, gi.customer_name
            FROM workflow_tasks wt
            JOIN users u ON wt.assignee_id = u.id
            JOIN green_identifications gi ON wt.identification_id = gi.id
            WHERE wt.assignee_id = :user_id AND wt.status = "待处理"
            AND wt.started_at >= "2026-02-16 13:00:00"
            ORDER BY wt.started_at DESC
        '''), {"user_id": user_id}).fetchall()
        
        print(f"\n申磊的待办工作流任务（共 {len(workflow_tasks)} 笔）:")
        for task in workflow_tasks:
            print(f"  - {task[4]}: {task[1]} ({task[2]})")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_workflow_for_tasks()
    print("\n工作流创建完成！")