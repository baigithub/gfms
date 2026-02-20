"""
检查任务数据完整性
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def check_data():
    """检查数据完整性"""
    db = SessionLocal()
    try:
        print("=== 检查任务 31 ===")
        
        # 检查 workflow_task
        task = db.execute(text("""
            SELECT id, task_name, assignee_id, identification_id, status
            FROM workflow_tasks
            WHERE id = 31
        """)).fetchone()
        
        if not task:
            print("✗ workflow_task 中不存在 ID=31 的任务")
            return
        
        print(f"工作流任务: ID={task[0]}, 名称={task[1]}, 处理人ID={task[2]}, 认定ID={task[3]}, 状态={task[4]}")
        
        # 检查 green_identification
        identification = db.execute(text("""
            SELECT id, loan_code, customer_name, initiator_id, status
            FROM green_identifications
            WHERE id = 31
        """)).fetchone()
        
        if not identification:
            print("✗ green_identifications 中不存在 ID=31 的记录")
            return
        
        print(f"绿色认定: ID={identification[0]}, 贷款编号={identification[1]}, 客户={identification[2]}, 发起人ID={identification[3]}, 状态={identification[4]}")
        
        # 检查 workflow_instance
        instance = db.execute(text("""
            SELECT id, case_id, status, identification_id
            FROM workflow_instances
            WHERE identification_id = 31
        """)).fetchone()
        
        if not instance:
            print("✗ workflow_instances 中不存在 identification_id=31 的记录")
        else:
            print(f"工作流实例: ID={instance[0]}, case_id={instance[1]}, 状态={instance[2]}")
        
        # 检查用户
        user = db.execute(text("""
            SELECT id, username, real_name
            FROM users
            WHERE id = :user_id
        """), {"user_id": task[2]}).fetchone()
        
        if not user:
            print(f"✗ 用户 ID={task[2]} 不存在")
        else:
            print(f"处理人: {user[2]} ({user[1]})")
        
        # 检查角色
        if user:
            role = db.execute(text("""
                SELECT id, name
                FROM roles
                WHERE id = :role_id
            """), {"role_id": 17}).fetchone()  # 客户经理角色ID是17
            
            if role:
                print(f"角色: {role[1]}")
            else:
                print(f"✗ 客户经理角色不存在")
        
        # 检查机构
        org = db.execute(text("""
            SELECT id, name
            FROM organizations
            WHERE id = :org_id
        """), {"org_id": identification[3]}).fetchone()
        
        if org:
            print(f"机构: {org[1]}")
        else:
            print(f"✗ 机构不存在 (ID={identification[3]})")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_data()