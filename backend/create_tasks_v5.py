#!/usr/bin/env python3
"""
创建10条绿色认定任务，使用正确的WorkflowEngine启动流程（绑定v5版本）
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import sessionmaker
from app.config import settings
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

# 数据库连接
engine = create_engine(settings.DATABASE_URL, pool_size=20, max_overflow=40)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# 《少年歌行》武力排行前10名人物
customers = [
    {'name': '百里东君', 'id': 'CUST000001', 'loan_code': 'LD20250220001', 'org_id': 17},
    {'name': '李寒衣', 'id': 'CUST000002', 'loan_code': 'LD20250220002', 'org_id': 17},
    {'name': '司空长风', 'id': 'CUST000003', 'loan_code': 'LD20250220003', 'org_id': 18},
    {'name': '无心', 'id': 'CUST000004', 'loan_code': 'LD20250220004', 'org_id': 18},
    {'name': '唐怜月', 'id': 'CUST000005', 'loan_code': 'LD20250220005', 'org_id': 19},
    {'name': '月姬', 'id': 'CUST000006', 'loan_code': 'LD20250220006', 'org_id': 19},
    {'name': '赵玉真', 'id': 'CUST000007', 'loan_code': 'LD20250220007', 'org_id': 20},
    {'name': '莫山山', 'id': 'CUST000008', 'loan_code': 'LD20250220008', 'org_id': 20},
    {'name': '叶红鱼', 'id': 'CUST000009', 'loan_code': 'LD20250220009', 'org_id': 21},
    {'name': '萧瑟', 'id': 'CUST000010', 'loan_code': 'LD20250220010', 'org_id': 21},
]

# 业务类型和项目分类映射
business_types = [
    '绿色流动资金贷款',
    '绿色固定资产贷款',
    '绿色项目融资',
]

project_categories = [
    {'large': '节能环保产业', 'medium': '高效节能装备制造', 'small': '工业节能技术与装备'},
    {'large': '清洁能源产业', 'medium': '新能源与可再生能源', 'small': '风力发电装备制造'},
    {'large': '清洁能源产业', 'medium': '新能源与可再生能源', 'small': '太阳能光伏发电'},
    {'large': '节能环保产业', 'medium': '节能环保服务', 'small': '节能服务'},
    {'large': '清洁生产产业', 'medium': '清洁生产技术与装备', 'small': '工业清洁生产技术'},
    {'large': '节能环保产业', 'medium': '高效节能装备制造', 'small': '建筑节能技术与装备'},
    {'large': '清洁能源产业', 'medium': '新能源与可再生能源', 'small': '生物质能利用'},
    {'large': '清洁生产产业', 'medium': '清洁生产技术与装备', 'small': '农业清洁生产技术'},
    {'large': '节能环保产业', 'medium': '节能环保服务', 'small': '环保服务'},
    {'large': '清洁能源产业', 'medium': '新能源与可再生能源', 'small': '储能技术与装备'},
]

def create_tasks():
    """创建绿色认定任务"""
    print('开始创建10条绿色认定任务...')
    
    # 获取tyyzy用户
    tyyzy = db.execute(text('''
        SELECT id, username, real_name FROM users WHERE username = 'tyyzy'
    ''')).fetchone()
    
    if not tyyzy:
        print('错误: 找不到用户 tyyzy')
        return
    
    tyyzy_id = tyyzy[0]
    print(f'用户: {tyyzy[1]} ({tyyzy[2]}), ID: {tyyzy_id}')
    
    from app.services.workflow import WorkflowEngine
    from app.models.green_finance import GreenIdentification, TaskStatus
    from app.models.user import User
    
    # 获取tyyzy用户对象
    user = db.query(User).filter(User.id == tyyzy_id).first()
    
    for i, customer in enumerate(customers):
        print(f'\n创建第 {i+1} 条任务: {customer["name"]}')
        
        # 创建绿色认定记录
        identification = GreenIdentification(
            loan_code=customer['loan_code'],
            customer_name=customer['name'],
            customer_id=customer['id'],
            business_type=business_types[i % len(business_types)],
            loan_account=f'LNA{customer["loan_code"]}',
            loan_amount=5000000.00 + i * 1000000.00,
            disbursement_date=datetime.now() - timedelta(days=random.randint(1, 20)),
            maturity_date=datetime.now() + timedelta(days=365),
            interest_rate=4.3500 + i * 0.01,
            green_percentage=100.00 - (i % 3) * 5.00,
            green_loan_balance=5000000.00 + i * 1000000.00,
            project_category_large=project_categories[i]['large'],
            project_category_medium=project_categories[i]['medium'],
            project_category_small=project_categories[i]['small'],
            esg_risk_level='低' if i % 3 == 0 else '中',
            esg_performance_level='优秀' if i % 3 == 0 else '良好',
            status=TaskStatus.PENDING.value,
            initiator_id=tyyzy_id,
            org_id=customer['org_id'],
            deadline=datetime.now() + timedelta(days=7)
        )
        
        db.add(identification)
        db.commit()
        db.refresh(identification)
        
        print(f'  ✓ 绿色认定记录创建成功, ID: {identification.id}')
        
        # 使用WorkflowEngine启动工作流（这会自动绑定到启用的流程版本v5）
        try:
            workflow = WorkflowEngine.start_process(db, identification, user)
            print(f'  ✓ 工作流实例创建成功, Case ID: {workflow.case_id}')
            print(f'  ✓ 当前节点: {workflow.current_node}')
            
            # 获取当前任务
            from app.models.green_finance import WorkflowTask
            task = db.query(WorkflowTask).filter(
                WorkflowTask.workflow_instance_id == workflow.id,
                WorkflowTask.status == '待处理'
            ).first()
            
            if task:
                print(f'  ✓ 待办任务创建成功, Task ID: {task.id}, 处理人: tyyzy')
            else:
                print(f'  ⚠ 警告: 未找到待办任务')
                
        except Exception as e:
            print(f'  ✗ 错误: {str(e)}')
            db.rollback()
            continue
    
    print('\n✓ 完成！已创建10条绿色认定任务，均绑定到流程版本v5')

if __name__ == '__main__':
    import random
    create_tasks()