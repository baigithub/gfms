#!/usr/bin/env python3
"""
生成性能测试数据
生成100万笔待认定任务，50万笔在望京支行下，50万笔在副中心支行下
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import sessionmaker
from app.config import settings
from sqlalchemy import create_engine, text
import random
import time
from datetime import datetime, timedelta
from faker import Faker

# 初始化Faker
fake = Faker('zh_CN')

# 数据库连接
engine = create_engine(settings.DATABASE_URL, pool_size=20, max_overflow=40)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def get_or_create_organizations():
    """获取或创建测试用的机构"""
    # 望京支行
    wangjing = db.execute(text('''
        SELECT id FROM organizations WHERE name = '望京支行'
    ''')).fetchone()
    
    if not wangjing:
        print('创建望京支行...')
        db.execute(text('''
            INSERT INTO organizations (name, code, level, parent_id, is_active, created_at, updated_at)
            VALUES ("望京支行", "WJ001", 3, 
                (SELECT id FROM organizations WHERE name = "北京分行" LIMIT 1), 
                1, NOW(), NOW())
        '''))
        db.commit()
        wangjing = db.execute(text('SELECT id FROM organizations WHERE name = "望京支行"')).fetchone()
    
    wangjing_id = wangjing[0]
    print(f'望京支行 ID: {wangjing_id}')
    
    # 副中心支行
    fuzhongxin = db.execute(text('''
        SELECT id FROM organizations WHERE name = "副中心支行"
    ''')).fetchone()
    
    if not fuzhongxin:
        print('创建副中心支行...')
        db.execute(text('''
            INSERT INTO organizations (name, code, level, parent_id, is_active, created_at, updated_at)
            VALUES ("副中心支行", "FZX001", 3, 
                (SELECT id FROM organizations WHERE name = "北京分行" LIMIT 1), 
                1, NOW(), NOW())
        '''))
        db.commit()
        fuzhongxin = db.execute(text('SELECT id FROM organizations WHERE name = "副中心支行"')).fetchone()
    
    fuzhongxin_id = fuzhongxin[0]
    print(f'副中心支行 ID: {fuzhongxin_id}')
    
    return wangjing_id, fuzhongxin_id

def create_test_users(org_id, count=10):
    """创建测试用户"""
    print(f'为机构 {org_id} 创建 {count} 个测试用户...')
    
    users = []
    for i in range(count):
        username = f'testuser_{org_id}_{i}'
        real_name = f'测试用户{i}'
        employee_id = f'TEST{org_id:04d}{i:03d}'
        
        user = db.execute(text('''
            SELECT id FROM users WHERE username = :username
        '''), {'username': username}).fetchone()
        
        if not user:
            # 生成密码hash (123456)
            import bcrypt
            password_hash = bcrypt.hashpw('123456'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            result = db.execute(text('''
                INSERT INTO users (username, password, real_name, employee_id, email, phone, 
                                   org_id, role_id, is_active, created_at, updated_at)
                VALUES (:username, :password, :real_name, :employee_id, :email, :phone,
                        :org_id, 2, 1, NOW(), NOW())
                RETURNING id
            '''), {
                'username': username,
                'password': password_hash,
                'real_name': real_name,
                'employee_id': employee_id,
                'email': f'{username}@test.com',
                'phone': f'138{random.randint(10000000, 99999999)}',
                'org_id': org_id
            }).fetchone()
            
            users.append(result[0])
            print(f'  创建用户: {username} (ID: {result[0]})')
        else:
            users.append(user[0])
    
    db.commit()
    return users

def generate_test_identifications(org_id, user_ids, count=500000, batch_size=1000, start_index=0):
    """批量生成待认定任务"""
    print(f'开始为机构 {org_id} 生成 {count} 笔待认定任务...')
    
    business_types = ['一般性固定资产贷款', '法人账户透支', '流动资金贷款']
    loan_amounts = [1000000 * i for i in range(1, 21)]  # 100万到2000万
    
    total_batches = count // batch_size
    start_time = time.time()
    
    for batch in range(total_batches + 1):
        batch_start = batch * batch_size
        batch_end = min(batch_start + batch_size, count)
        
        if batch_start >= count:
            break
        
        print(f'  处理批次 {batch + 1}/{total_batches + 1} ({batch_start + 1}-{batch_end})...')
        
        # 生成批量数据
        identification_values = []
        for i in range(batch_start, batch_end):
            user_id = random.choice(user_ids)
            business_type = random.choice(business_types)
            loan_amount = random.choice(loan_amounts)
            disbursement_date = fake.date_between(start_date='-365d', end_date='today')
            
            identification_values.append({
                'loan_code': f'GL{datetime.now().strftime("%Y%m%d")}{start_index + i:08d}',
                'customer_name': fake.company(),
                'business_type': business_type,
                'loan_account': f'6222{random.randint(100000000000, 999999999999)}',
                'loan_amount': loan_amount,
                'disbursement_date': disbursement_date.strftime('%Y-%m-%d'),
                'deadline': (disbursement_date + timedelta(days=90)).strftime('%Y-%m-%d'),
                'initiator_id': user_id,
                'org_id': org_id,
                'status': '待处理',
                'project_category_large': None,
                'project_category_medium': None,
                'project_category_small': None,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
        
        # 批量插入
        if identification_values:
            db.execute(text('''
                INSERT INTO green_identifications 
                (loan_code, customer_name, business_type, loan_account, loan_amount, 
                 disbursement_date, deadline, initiator_id, org_id, status,
                 project_category_large, project_category_medium, project_category_small,
                 created_at, updated_at)
                VALUES 
                (:loan_code, :customer_name, :business_type, :loan_account, :loan_amount,
                 :disbursement_date, :deadline, :initiator_id, :org_id, :status,
                 :project_category_large, :project_category_medium, :project_category_small,
                 :created_at, :updated_at)
            '''), identification_values)
            
            db.commit()
            
            # 获取刚插入的ID，创建工作流实例和任务
            identification_ids = db.execute(text('''
                SELECT id FROM green_identifications 
                WHERE loan_code IN :loan_codes
                ORDER BY id DESC
                LIMIT :limit
            '''), {
                'loan_codes': [v['loan_code'] for v in identification_values],
                'limit': len(identification_values)
            }).fetchall()
            
            # 创建工作流实例和任务
            workflow_values = []
            for identification_id in identification_ids:
                workflow_values.append({
                    'case_id': f'CASE{identification_id[0]}',
                    'process_key': 'green_identification',
                    'business_key': str(identification_id[0]),
                    'current_node': 'manager_identification',
                    'status': '进行中',
                    'started_at': datetime.now(),
                    'identification_id': identification_id[0]
                })
            
            # 批量插入工作流实例
            db.execute(text('''
                INSERT INTO workflow_instances 
                (case_id, process_key, business_key, current_node, status, started_at, identification_id)
                VALUES 
                (:case_id, :process_key, :business_key, :current_node, :status, :started_at, :identification_id)
            '''), workflow_values)
            
            db.commit()
            
            # 获取工作流实例ID，创建工作流任务
            workflow_instances = db.execute(text('''
                SELECT id, identification_id FROM workflow_instances 
                WHERE case_id IN :case_ids
                ORDER BY id DESC
                LIMIT :limit
            '''), {
                'case_ids': [v['case_id'] for v in workflow_values],
                'limit': len(workflow_values)
            }).fetchall()
            
            # 创建工作流任务
            task_values = []
            for wi in workflow_instances:
                user_id = random.choice(user_ids)
                task_values.append({
                    'task_key': 'manager_identification',
                    'task_name': '客户经理认定',
                    'node_id': 'UserTask_manager_identification',
                    'assignee_id': user_id,
                    'status': '待处理',
                    'started_at': datetime.now(),
                    'workflow_instance_id': wi[0],
                    'identification_id': wi[1],
                    'project_category_large': None,
                    'project_category_medium': None,
                    'project_category_small': None
                })
            
            # 批量插入工作流任务
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
            
            db.commit()
            
            elapsed = time.time() - start_time
            progress = (batch_end / count) * 100
            print(f'    进度: {progress:.2f}%, 已处理: {batch_end}/{count}, 耗时: {elapsed:.2f}秒')
    
    total_time = time.time() - start_time
    print(f'✓ 完成！生成 {count} 笔任务，总耗时: {total_time:.2f}秒')
    print(f'  平均速度: {count/total_time:.2f} 笔/秒')

def main():
    print('=== 绿色金融管理系统性能测试数据生成 ===')
    print()
    
    try:
        # 1. 获取或创建机构
        wangjing_id, fuzhongxin_id = get_or_create_organizations()
        print()
        
        # 2. 为每个机构创建测试用户
        print('创建测试用户...')
        wangjing_users = create_test_users(wangjing_id, count=10)
        fuzhongxin_users = create_test_users(fuzhongxin_id, count=10)
        print()
        
        # 3. 生成测试数据
        print('开始生成测试数据...')
        print()
        
        # 望京支行50万笔
        print('【望京支行】生成50万笔待认定任务...')
        # 检查已存在的数据量
        existing_wangjing = db.execute(text('SELECT COUNT(*) FROM green_identifications WHERE org_id = :org_id'), 
                                       {'org_id': wangjing_id}).fetchone()[0]
        if existing_wangjing >= 500000:
            print(f'  望京支行已有 {existing_wangjing} 笔数据，跳过生成')
        else:
            generate_test_identifications(wangjing_id, wangjing_users, count=500000, batch_size=1000)
        print()
        
        # 副中心支行50万笔
        print('【副中心支行】生成50万笔待认定任务...')
        # 检查已存在的数据量
        existing_fuzhongxin = db.execute(text('SELECT COUNT(*) FROM green_identifications WHERE org_id = :org_id'), 
                                         {'org_id': fuzhongxin_id}).fetchone()[0]
        if existing_fuzhongxin >= 500000:
            print(f'  副中心支行已有 {existing_fuzhongxin} 笔数据，跳过生成')
        else:
            generate_test_identifications(fuzhongxin_id, fuzhongxin_users, count=500000, batch_size=1000, start_index=500000)
        print()
        
        # 4. 验证数据
        print('验证数据...')
        wangjing_count = db.execute(text('''
            SELECT COUNT(*) FROM green_identifications WHERE org_id = :org_id
        '''), {'org_id': wangjing_id}).fetchone()[0]
        
        fuzhongxin_count = db.execute(text('''
            SELECT COUNT(*) FROM green_identifications WHERE org_id = :org_id
        '''), {'org_id': fuzhongxin_id}).fetchone()[0]
        
        total_count = db.execute(text('''
            SELECT COUNT(*) FROM green_identifications WHERE status = '待处理'
        ''')).fetchone()[0]
        
        print(f'  望京支行: {wangjing_count} 笔')
        print(f'  副中心支行: {fuzhongxin_count} 笔')
        print(f'  总计: {total_count} 笔')
        print()
        
        print('✓ 数据生成完成！')
        
    except Exception as e:
        print(f'✗ 错误: {e}')
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    main()