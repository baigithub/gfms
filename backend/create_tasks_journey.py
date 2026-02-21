#!/usr/bin/env python3
"""
根据《西游记》中战力排行前10名的人物生成10条待办任务
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from app.config import settings
from datetime import datetime

# 数据库连接
engine = create_engine(settings.DATABASE_URL)

# 西游记战力排行前10名人物
characters = [
    "如来佛祖",
    "菩提祖师",
    "镇元大仙",
    "太上老君",
    "观音菩萨",
    "元始天尊",
    "太白金星",
    "玉皇大帝",
    "太乙救苦天尊",
    "九灵元圣"
]

def main():
    print('开始创建10条绿色认定任务...')
    
    # 获取tyyzy用户信息
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, username, real_name, org_id 
            FROM users 
            WHERE username = 'tyyzy'
        """)).fetchone()
        
        if not result:
            print('错误: 未找到用户tyyzy')
            return
        
        user_id = result[0]
        user_name = result[2]
        org_id = result[3]
        
        print(f'用户: {user_name} (ID: {user_id}, 机构ID: {org_id})')
        
        # 生成10条待办任务
        for i, character in enumerate(characters, 1):
            loan_code = f"LD20260220{i:02d}"
            customer_id = f"CUST{i:06d}"
            loan_account = f"LNA{loan_code}"
            
            # 插入绿色认定记录（不绑定流程版本）
            conn.execute(text("""
                INSERT INTO green_identifications 
                (loan_code, customer_name, customer_id, business_type, loan_account, 
                 loan_amount, disbursement_date, maturity_date, interest_rate, 
                 green_percentage, green_loan_balance, project_category_large, 
                 project_category_medium, project_category_small, esg_risk_level, 
                 esg_performance_level, status, initiator_id, current_handler_id, 
                 org_id, created_at, updated_at, deadline)
                VALUES 
                (:loan_code, :customer_name, :customer_id, '绿色流动资金贷款', 
                 :loan_account, 5000000.00, '2026-02-15', '2027-02-15', 
                 4.3500, 100.00, 5000000.00, '节能环保产业', 
                 '高效节能装备制造', '工业节能技术与装备', '低', 
                 '优秀', '待办', :user_id, :user_id, 
                 :org_id, NOW(), NOW(), DATE_ADD(NOW(), INTERVAL 7 DAY))
            """), {
                'loan_code': loan_code,
                'customer_name': character,
                'customer_id': customer_id,
                'loan_account': loan_account,
                'user_id': user_id,
                'org_id': org_id
            })
            
            # 获取刚插入的green_identifications记录ID
            result = conn.execute(text("""
                SELECT id FROM green_identifications WHERE loan_code = :loan_code
            """), {'loan_code': loan_code}).fetchone()
            identification_id = result[0]
            
            print(f"✓ 第 {i} 条任务: {character}")
            print(f"  ✓ 绿色认定记录创建成功, ID: {identification_id}")
            
            # 创建工作流实例（不绑定流程版本）
            case_id = f"CASE{datetime.now().strftime('%Y%m%d%H%M%S')}_{identification_id}"
            conn.execute(text("""
                INSERT INTO workflow_instances 
                (case_id, process_key, business_key, current_node, status, started_at, 
                 identification_id)
                VALUES 
                (:case_id, 'green_identification_process', :loan_code, 'manager_identification', 
                 '进行中', NOW(), :identification_id)
            """), {
                'case_id': case_id,
                'loan_code': loan_code,
                'identification_id': identification_id
            })
            
            # 获取工作流实例ID
            result = conn.execute(text("""
                SELECT id FROM workflow_instances WHERE case_id = :case_id
            """), {'case_id': case_id}).fetchone()
            workflow_instance_id = result[0]
            
            print(f"  ✓ 工作流实例创建成功, ID: {workflow_instance_id}")
            
            # 创建工作流任务
            conn.execute(text("""
                INSERT INTO workflow_tasks 
                (task_key, task_name, node_id, assignee_id, status, started_at, 
                 workflow_instance_id, identification_id, project_category_large, 
                 project_category_medium, project_category_small)
                VALUES 
                ('manager_identification', '客户经理提交', 'UserTask_manager_identification', 
                 :user_id, '待处理', NOW(), :workflow_instance_id, :identification_id, 
                 '节能环保产业', '高效节能装备制造', '工业节能技术与装备')
            """), {
                'user_id': user_id,
                'workflow_instance_id': workflow_instance_id,
                'identification_id': identification_id
            })
            
            print(f"  ✓ 待办任务创建成功, 处理人: {user_name}")
        
        conn.commit()
    
    print(f'✓ 完成！已创建10条绿色认定任务（未绑定流程版本，将在提交时动态绑定）')

if __name__ == '__main__':
    main()