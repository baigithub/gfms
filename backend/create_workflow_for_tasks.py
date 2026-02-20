"""
为申磊的10笔待办任务创建工作流任务和工作流实例
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
        
        # 获取流程定义ID（绿色认定流程）
        process_def = db.execute(text('''
            SELECT id, name 
            FROM process_definitions 
            WHERE name LIKE "%绿色认定%" OR name LIKE "%绿色金融%"
            LIMIT 1
        ''')).fetchone()
        
        if not process_def:
            print("✗ 未找到绿色认定流程定义")
            return
        
        process_def_id = process_def[0]
        print(f"使用流程定义: {process_def[1]} (ID: {process_def_id})")
        
        # 为每个任务创建流程实例和任务
        for task in pending_tasks:
            identification_id = task[0]
            
            # 创建流程实例
            instance_key = f"GI{identification_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            instance_result = db.execute(text('''
                INSERT INTO process_instances 
                (instance_key, definition_id, business_key, status, current_node, started_by, started_at)
                VALUES 
                (:instance_key, :definition_id, :business_key, :status, :current_node, :started_by, :started_at)
            '''), {
                "instance_key": instance_key,
                "definition_id": process_def_id,
                "business_key": f"GI{identification_id}",
                "status": "running",
                "current_node": "manager_identification",
                "started_by": user_id,
                "started_at": datetime.now()
            })
            
            instance_id = instance_result.lastrowid
            print(f"  ✓ 创建流程实例 ID: {instance_id}")
            
            # 创建流程任务（客户经理认定节点）
            task_result = db.execute(text('''
                INSERT INTO process_tasks 
                (instance_id, task_key, task_name, assignee_id, status, started_at)
                VALUES 
                (:instance_id, :task_key, :task_name, :assignee_id, :status, :started_at)
            '''), {
                "instance_id": instance_id,
                "task_key": "manager_identification",
                "task_name": "客户经理认定",
                "assignee_id": user_id,  # 分配给申磊
                "status": "pending",
                "started_at": datetime.now()
            })
            
            task_id = task_result.lastrowid
            print(f"    ✓ 创建流程任务 ID: {task_id}, 分配给: {user[2]}")
        
        db.commit()
        print(f"\n✓ 成功为 {len(pending_tasks)} 笔任务创建流程")
        
        # 验证创建的流程任务
        print("\n验证创建的流程任务...")
        process_tasks = db.execute(text('''
            SELECT pt.id, pt.task_key, pt.status, u.real_name as assignee_name, gi.customer_name
            FROM process_tasks pt
            JOIN users u ON pt.assignee_id = u.id
            JOIN green_identifications gi ON gi.loan_code = (
                SELECT business_key FROM process_instances pi WHERE pi.id = pt.instance_id
            )
            WHERE pt.assignee_id = :user_id AND pt.status = "pending"
            ORDER BY pt.created_at DESC
        '''), {"user_id": user_id}).fetchall()
        
        print(f"\n申磊的待办流程任务（共 {len(process_tasks)} 笔）:")
        for task in process_tasks:
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
