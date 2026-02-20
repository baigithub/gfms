"""
修复工作流任务的关联关系
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def fix_relations():
    """修复关联关系"""
    db = SessionLocal()
    try:
        # 首先删除所有错误的工作流任务
        db.execute(text("DELETE FROM workflow_tasks"))
        db.execute(text("DELETE FROM workflow_instances"))
        db.commit()
        print("✓ 清理了旧的工作流任务和实例")
        
        # 重新创建正确的工作流实例和任务
        # 1. 获取所有绿色认定任务
        identifications = db.execute(text("""
            SELECT id, loan_code, initiator_id
            FROM green_identifications
            WHERE status = '待办'
            ORDER BY id
        """)).fetchall()
        
        print(f"找到 {len(identifications)} 条绿色认定任务")
        
        # 2. 获取流程定义
        definition = db.execute(text("""
            SELECT id, name
            FROM process_definitions
            WHERE status = 'active'
            ORDER BY id
            LIMIT 1
        """)).fetchone()
        
        if not definition:
            print("✗ 未找到启用的流程定义")
            return
        
        print(f"使用流程定义: {definition[1]}")
        
        # 3. 为每个绿色认定创建工作流实例和任务
        created_count = 0
        for ident in identifications:
            ident_id = ident[0]  # identification ID
            loan_code = ident[1]
            initiator_id = ident[2]
            
            # 创建工作流实例
            case_id = f"CASE_{loan_code}"
            
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
            
            # 创建工作流任务 - 注意：这里 identification_id 必须和 green_identifications 的 ID 一致
            db.execute(text(f"""
                INSERT INTO workflow_tasks 
                (task_key, task_name, node_id, assignee_id, status, 
                 started_at, workflow_instance_id, identification_id)
                VALUES 
                ('manager_identification', '客户经理认定', 'Task_1', {initiator_id}, 
                 '待处理', '{now}', {instance_id}, {ident_id})
            """))
            
            created_count += 1
            print(f"  ✓ 创建工作流: {loan_code} (实例ID: {instance_id}, 认定ID: {ident_id})")
        
        db.commit()
        print(f"\n✓ 成功创建 {created_count} 个工作流实例和任务")
        
        # 4. 验证结果
        print(f"\n=== 验证结果 ===")
        tasks = db.execute(text("""
            SELECT wt.id, wt.task_name, wt.assignee_id, wt.identification_id,
                   gi.loan_code, gi.customer_name
            FROM workflow_tasks wt
            JOIN workflow_instances wi ON wt.workflow_instance_id = wi.id
            JOIN green_identifications gi ON wt.identification_id = gi.id
            WHERE wt.assignee_id = 5
            ORDER BY wt.id
            LIMIT 10
        """)).fetchall()
        
        if not tasks:
            print("用户 tyyzy 没有待办任务")
        else:
            print(f"{'Task ID':<10} {'任务名称':<15} {'认定ID':<10} {'贷款编号':<20} {'客户名称':<25}")
            print("-" * 90)
            for task in tasks:
                print(f"{task[0]:<10} {task[1]:<15} {task[2]:<10} {task[3]:<20} {task[4]:<25}")
            
            print(f"\n总计: {len(tasks)} 条待办任务")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    from datetime import datetime
    fix_relations()