#!/usr/bin/env python3
"""
创建10条绿色认定任务（使用旧的workflow_instances表）
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import sessionmaker
from app.config import settings
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import random

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
    
    # 先删除之前创建的记录
    print('\n清理之前的记录...')
    db.execute(text('''
        DELETE FROM workflow_tasks WHERE identification_id IN (
            SELECT id FROM green_identifications WHERE loan_code LIKE 'LD202502200%'
        )
    '''))
    db.execute(text('''
        DELETE FROM workflow_instances WHERE identification_id IN (
            SELECT id FROM green_identifications WHERE loan_code LIKE 'LD202502200%'
        )
    '''))
    db.execute(text('''
        DELETE FROM green_identifications WHERE loan_code LIKE 'LD202502200%'
    '''))
    db.commit()
    print('✓ 清理完成')
    
    for i, customer in enumerate(customers):
        print(f'\n创建第 {i+1} 条任务: {customer["name"]}')
        
        # 创建绿色认定记录
        identification_values = {
            'loan_code': customer['loan_code'],
            'customer_name': customer['name'],
            'customer_id': customer['id'],
            'business_type': business_types[i % len(business_types)],
            'loan_account': f'LNA{customer["loan_code"]}',
            'loan_amount': 5000000.00 + i * 1000000.00,
            'disbursement_date': datetime.now() - timedelta(days=random.randint(1, 20)),
            'maturity_date': datetime.now() + timedelta(days=365),
            'interest_rate': 4.3500 + i * 0.01,
            'green_percentage': 100.00 - (i % 3) * 5.00,
            'green_loan_balance': 5000000.00 + i * 1000000.00,
            'project_category_large': project_categories[i]['large'],
            'project_category_medium': project_categories[i]['medium'],
            'project_category_small': project_categories[i]['small'],
            'esg_risk_level': '低' if i % 3 == 0 else '中',
            'esg_performance_level': '优秀' if i % 3 == 0 else '良好',
            'status': '待办',
            'initiator_id': tyyzy_id,
            'current_handler_id': tyyzy_id,
            'org_id': customer['org_id'],
            'deadline': datetime.now() + timedelta(days=7),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        db.execute(text('''
            INSERT INTO green_identifications 
            (loan_code, customer_name, customer_id, business_type, loan_account, loan_amount, 
             disbursement_date, maturity_date, interest_rate, green_percentage, green_loan_balance,
             project_category_large, project_category_medium, project_category_small,
             esg_risk_level, esg_performance_level, status, initiator_id, current_handler_id, org_id, deadline,
             created_at, updated_at)
            VALUES 
            (:loan_code, :customer_name, :customer_id, :business_type, :loan_account, :loan_amount,
             :disbursement_date, :maturity_date, :interest_rate, :green_percentage, :green_loan_balance,
             :project_category_large, :project_category_medium, :project_category_small,
             :esg_risk_level, :esg_performance_level, :status, :initiator_id, :current_handler_id, :org_id, :deadline,
             :created_at, :updated_at)
        '''), identification_values)
        
        identification_id = db.execute(text('SELECT LAST_INSERT_ID()')).fetchone()[0]
        print(f'  ✓ 绿色认定记录创建成功, ID: {identification_id}')
        
        # 创建工作流实例
        case_id = f'CASE{datetime.now().strftime("%Y%m%d%H%M%S")}_{identification_id}'
        workflow_values = {
            'case_id': case_id,
            'process_key': 'green_identification_process',
            'business_key': customer['loan_code'],
            'current_node': 'manager_identification',
            'status': '进行中',
            'started_at': datetime.now(),
            'identification_id': identification_id
        }
        
        db.execute(text('''
            INSERT INTO workflow_instances 
            (case_id, process_key, business_key, current_node, status, started_at, identification_id)
            VALUES 
            (:case_id, :process_key, :business_key, :current_node, :status, :started_at, :identification_id)
        '''), workflow_values)
        
        workflow_id = db.execute(text('SELECT LAST_INSERT_ID()')).fetchone()[0]
        print(f'  ✓ 工作流实例创建成功, ID: {workflow_id}')
        
        # 创建工作流任务
        task_values = {
            'task_key': f'TASK{customer["loan_code"]}',
            'task_name': f'客户经理认定-{customer["name"]}',
            'node_id': 'customer_manager_node',
            'assignee_id': tyyzy_id,
            'status': '待处理',
            'started_at': datetime.now(),
            'workflow_instance_id': workflow_id,
            'identification_id': identification_id,
            'project_category_large': project_categories[i]['large'],
            'project_category_medium': project_categories[i]['medium'],
            'project_category_small': project_categories[i]['small']
        }
        
        db.execute(text('''
            INSERT INTO workflow_tasks 
            (task_key, task_name, node_id, assignee_id, status, started_at, 
             workflow_instance_id, identification_id,
             project_category_large, project_category_medium, project_category_small)
            VALUES 
            (:task_key, :task_name, :node_id, :assignee_id, :status, :started_at,
             :workflow_instance_id, :identification_id,
             :project_category_large, :project_category_medium, :project_category_small)
        '''), task_values)
        
        print(f'  ✓ 待办任务创建成功, 处理人: tyyzy')
        
        db.commit()
    
    print('\n✓ 完成！已创建10条绿色认定任务')

if __name__ == '__main__':
    create_tasks()