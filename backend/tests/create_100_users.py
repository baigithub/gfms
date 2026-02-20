#!/usr/bin/env python3
"""
创建100个测试用户
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from app.config import settings
import bcrypt

engine = create_engine(settings.DATABASE_URL)
with engine.connect() as conn:
    # 清理现有测试用户
    print('清理现有测试用户...')
    conn.execute(text('DELETE FROM users WHERE username LIKE "testuser_%"'))
    conn.commit()
    
    # 获取机构ID
    wangjing_id = conn.execute(text('SELECT id FROM organizations WHERE name = "望京支行"')).fetchone()[0]
    fuzhongxin_id = conn.execute(text('SELECT id FROM organizations WHERE name = "副中心支行"')).fetchone()[0]
    
    print(f'望京支行 ID: {wangjing_id}')
    print(f'副中心支行 ID: {fuzhongxin_id}')
    print()
    
    # 创建望京支行10个用户
    print('创建望京支行测试用户...')
    for i in range(10):
        username = f'testuser_{wangjing_id}_{i}'
        password_hash = bcrypt.hashpw('123456'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        conn.execute(text('''
            INSERT INTO users (username, password_hash, real_name, employee_id, email, phone, 
                             org_id, role_id, is_active, created_at, updated_at)
            VALUES (:username, :password, :real_name, :employee_id, :email, :phone,
                    :org_id, 2, 1, NOW(), NOW())
        '''), {
            'username': username,
            'password': password_hash,
            'real_name': f'测试用户{i}',
            'employee_id': f'TEST{wangjing_id:04d}{i:03d}',
            'email': f'{username}@test.com',
            'phone': f'138{10000000 + i}',
            'org_id': wangjing_id
        })
        print(f'  创建用户: {username}')
    
    # 创建副中心支行90个用户
    print('创建副中心支行测试用户...')
    for i in range(90):
        username = f'testuser_{fuzhongxin_id}_{i}'
        password_hash = bcrypt.hashpw('123456'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        conn.execute(text('''
            INSERT INTO users (username, password_hash, real_name, employee_id, email, phone, 
                             org_id, role_id, is_active, created_at, updated_at)
            VALUES (:username, :password, :real_name, :employee_id, :email, :phone,
                    :org_id, 2, 1, NOW(), NOW())
        '''), {
            'username': username,
            'password': password_hash,
            'real_name': f'测试用户{i+10}',
            'employee_id': f'TEST{fuzhongxin_id:04d}{i+10:03d}',
            'email': f'{username}@test.com',
            'phone': f'138{20000000 + i}',
            'org_id': fuzhongxin_id
        })
        if i < 5:
            print(f'  创建用户: {username}')
        if i == 89:
            print(f'  ... (共90个用户)')
    
    conn.commit()
    
    # 验证用户数量
    total = conn.execute(text('SELECT COUNT(*) FROM users WHERE username LIKE "testuser_%"')).fetchone()[0]
    print()
    print(f'✓ 成功创建 {total} 个测试用户')