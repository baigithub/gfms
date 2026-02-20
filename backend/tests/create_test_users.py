#!/usr/bin/env python3
"""
创建性能测试用户
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import sessionmaker
from app.config import settings
from sqlalchemy import create_engine, text
import bcrypt

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def create_test_users():
    """创建测试用户"""
    print("="*60)
    print("创建性能测试用户")
    print("="*60)
    
    # 获取机构ID
    wangjing_id = db.execute(text('SELECT id FROM organizations WHERE name = "望京支行"')).fetchone()
    fuzhongxin_id = db.execute(text('SELECT id FROM organizations WHERE name = "副中心支行"')).fetchone()
    
    if not wangjing_id:
        print('✗ 未找到望京支行')
        return
    
    if not fuzhongxin_id:
        print('✗ 未找到副中心支行')
        return
    
    wangjing_id = wangjing_id[0]
    fuzhongxin_id = fuzhongxin_id[0]
    
    print(f'望京支行 ID: {wangjing_id}')
    print(f'副中心支行 ID: {fuzhongxin_id}')
    print()
    
    # 删除现有测试用户
    print('清理现有测试用户...')
    db.execute(text('DELETE FROM users WHERE username LIKE "testuser_%"'))
    db.commit()
    
    # 创建测试用户
    print('创建测试用户...')
    
    created_count = 0
    
    # 望京支行10个用户
    for i in range(10):
        username = f'testuser_{wangjing_id}_{i}'
        real_name = f'测试用户{i}'
        employee_id = f'TEST{wangjing_id:04d}{i:03d}'
        password_hash = bcrypt.hashpw('123456'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        db.execute(text('''
            INSERT INTO users (username, password_hash, real_name, employee_id, email, phone, 
                               org_id, role_id, is_active, created_at, updated_at)
            VALUES (:username, :password, :real_name, :employee_id, :email, :phone,
                    :org_id, 2, 1, NOW(), NOW())
        '''), {
            'username': username,
            'password': password_hash,
            'real_name': real_name,
            'employee_id': employee_id,
            'email': f'{username}@test.com',
            'phone': f'138{random.randint(10000000, 99999999)}',
            'org_id': wangjing_id
        })
        
        result = db.execute(text('SELECT id FROM users WHERE username = :username'), {'username': username}).fetchone()
        print(f'  ✓ 创建用户: {username} (ID: {result[0]})')
        created_count += 1
    
    # 副中心支行10个用户
    for i in range(10):
        username = f'testuser_{fuzhongxin_id}_{i}'
        real_name = f'测试用户{i}'
        employee_id = f'TEST{fuzhongxin_id:04d}{i:03d}'
        password_hash = bcrypt.hashpw('123456'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        db.execute(text('''
            INSERT INTO users (username, password_hash, real_name, employee_id, email, phone, 
                               org_id, role_id, is_active, created_at, updated_at)
            VALUES (:username, :password, :real_name, :employee_id, :email, :phone,
                    :org_id, 2, 1, NOW(), NOW())
        '''), {
            'username': username,
            'password': password_hash,
            'real_name': real_name,
            'employee_id': employee_id,
            'email': f'{username}@test.com',
            'phone': f'138{random.randint(10000000, 99999999)}',
            'org_id': fuzhongxin_id
        })
        
        result = db.execute(text('SELECT id FROM users WHERE username = :username'), {'username': username}).fetchone()
        print(f'  ✓ 创建用户: {username} (ID: {result[0]})')
        created_count += 1
    
    db.commit()
    
    print()
    print(f'✓ 成功创建 {created_count} 个测试用户')
    print()
    
    # 验证用户
    result = db.execute(text('SELECT COUNT(*) FROM users WHERE username LIKE "testuser_%"')).fetchone()
    print(f'验证: 共有 {result[0]} 个测试用户')

if __name__ == '__main__':
    import random
    create_test_users()
    db.close()
    print('\n测试用户创建完成！')