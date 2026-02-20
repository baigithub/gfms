#!/usr/bin/env python3
"""
性能测试脚本 - 并发用户登录和审批任务
模拟100个并发用户，自动登录并审批任务
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import asyncio
import aiohttp
import time
import statistics
from datetime import datetime
import random
from typing import List, Dict
import json

# 配置
BASE_URL = "http://localhost:8000"
CONCURRENT_USERS = 5
TEST_DURATION = 300  # 测试持续时间（秒）
MAX_RETRIES = 3

# 统计数据
performance_stats = {
    'login_times': [],
    'task_load_times': [],
    'task_complete_times': [],
    'errors': [],
    'throughput': 0,
    'concurrent_users': 0,
    'start_time': None,
    'end_time': None
}

class PerformanceTester:
    def __init__(self, user_id: int, username: str, password: str):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.token = None
        self.session = None
        self.tasks_completed = 0
    
    async def login(self, session: aiohttp.ClientSession) -> bool:
        """用户登录"""
        start_time = time.time()
        try:
            async with session.post(
                f"{BASE_URL}/api/auth/login",
                json={"username": self.username, "password": self.password},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.token = data.get("access_token")
                    elapsed = time.time() - start_time
                    performance_stats['login_times'].append(elapsed)
                    print(f"[用户{self.user_id}] 登录成功，耗时: {elapsed:.3f}秒")
                    return True
                else:
                    error_msg = await response.text()
                    performance_stats['errors'].append(f"登录失败: {response.status} - {error_msg}")
                    print(f"[用户{self.user_id}] 登录失败: {response.status}")
                    return False
        except Exception as e:
            performance_stats['errors'].append(f"登录异常: {str(e)}")
            print(f"[用户{self.user_id}] 登录异常: {str(e)}")
            return False
    
    async def get_pending_tasks(self, session: aiohttp.ClientSession) -> List[Dict]:
        """获取待办任务"""
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            async with session.get(
                f"{BASE_URL}/api/tasks/pending?page=1&page_size=1",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    elapsed = time.time() - start_time
                    performance_stats['task_load_times'].append(elapsed)
                    return data.get('items', [])
                else:
                    error_msg = await response.text()
                    performance_stats['errors'].append(f"获取任务失败: {response.status} - {error_msg}")
                    return []
        except Exception as e:
            performance_stats['errors'].append(f"获取任务异常: {str(e)}")
            return []
    
    async def complete_task(self, session: aiohttp.ClientSession, task_id: int) -> bool:
        """完成任务"""
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            task_data = {
                "approval_result": "同意",
                "comment": f"性能测试自动审批 - 用户{self.user_id}"
            }
            
            async with session.post(
                f"{BASE_URL}/api/tasks/{task_id}/complete",
                headers=headers,
                json=task_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    elapsed = time.time() - start_time
                    performance_stats['task_complete_times'].append(elapsed)
                    self.tasks_completed += 1
                    print(f"[用户{self.user_id}] 完成任务 {task_id}，耗时: {elapsed:.3f}秒")
                    return True
                else:
                    error_msg = await response.text()
                    performance_stats['errors'].append(f"完成任务失败: {response.status} - {error_msg}")
                    print(f"[用户{self.user_id}] 完成任务 {task_id} 失败: {response.status}")
                    return False
        except Exception as e:
            performance_stats['errors'].append(f"完成任务异常: {str(e)}")
            print(f"[用户{self.user_id}] 完成任务 {task_id} 异常: {str(e)}")
            return False
    
    async def worker(self, session: aiohttp.ClientSession, stop_event: asyncio.Event):
        """工作线程 - 持续登录并处理任务"""
        retry_count = 0
        
        while not stop_event.is_set() and retry_count < MAX_RETRIES:
            # 登录
            if not self.token:
                login_success = await self.login(session)
                if not login_success:
                    retry_count += 1
                    await asyncio.sleep(5)
                    continue
            
            # 获取待办任务
            tasks = await self.get_pending_tasks(session)
            if tasks and len(tasks) > 0:
                task = tasks[0]
                task_id = task.get('task_id')
                
                if task_id:
                    # 完成任务
                    await self.complete_task(session, task_id)
                    
                    # 重置token，模拟新用户登录
                    self.token = None
                    await asyncio.sleep(random.uniform(1, 3))  # 随机延迟
                else:
                    # 任务没有task_id，尝试下一个任务
                    await asyncio.sleep(1)
            else:
                # 没有待办任务，等待
                await asyncio.sleep(2)
    
    async def run(self, stop_event: asyncio.Event):
        """运行单个用户的测试"""
        async with aiohttp.ClientSession() as session:
            await self.worker(session, stop_event)

def print_statistics():
    """打印性能统计数据"""
    print("\n" + "="*60)
    print("性能测试统计数据")
    print("="*60)
    
    if performance_stats['start_time'] and performance_stats['end_time']:
        total_time = performance_stats['end_time'] - performance_stats['start_time']
        print(f"测试持续时间: {total_time:.2f}秒")
    
    print(f"并发用户数: {performance_stats['concurrent_users']}")
    
    # 登录时间统计
    if performance_stats['login_times']:
        login_times = performance_stats['login_times']
        print(f"\n【登录性能】")
        print(f"  总登录次数: {len(login_times)}")
        print(f"  平均响应时间: {statistics.mean(login_times):.3f}秒")
        print(f"  最小响应时间: {min(login_times):.3f}秒")
        print(f"  最大响应时间: {max(login_times):.3f}秒")
        if len(login_times) > 1:
            print(f"  标准差: {statistics.stdev(login_times):.3f}秒")
            print(f"  P50 (中位数): {statistics.median(login_times):.3f}秒")
            print(f"  P95: {sorted(login_times)[int(len(login_times) * 0.95)]:.3f}秒")
            print(f"  P99: {sorted(login_times)[int(len(login_times) * 0.99)]:.3f}秒")
    
    # 任务加载时间统计
    if performance_stats['task_load_times']:
        load_times = performance_stats['task_load_times']
        print(f"\n【任务加载性能】")
        print(f"  总加载次数: {len(load_times)}")
        print(f"  平均响应时间: {statistics.mean(load_times):.3f}秒")
        print(f"  最小响应时间: {min(load_times):.3f}秒")
        print(f"  最大响应时间: {max(load_times):.3f}秒")
        if len(load_times) > 1:
            print(f"  标准差: {statistics.stdev(load_times):.3f}秒")
            print(f"  P50: {statistics.median(load_times):.3f}秒")
            print(f"  P95: {sorted(load_times)[int(len(load_times) * 0.95)]:.3f}秒")
    
    # 任务完成时间统计
    if performance_stats['task_complete_times']:
        complete_times = performance_stats['task_complete_times']
        print(f"\n【任务审批性能】")
        print(f"  总审批次数: {len(complete_times)}")
        print(f"  平均响应时间: {statistics.mean(complete_times):.3f}秒")
        print(f"  最小响应时间: {min(complete_times):.3f}秒")
        print(f"  最大响应时间: {max(complete_times):.3f}秒")
        if len(complete_times) > 1:
            print(f"  标准差: {statistics.stdev(complete_times):.3f}秒")
            print(f"  P50: {statistics.median(complete_times):.3f}秒")
            print(f"  P95: {sorted(complete_times)[int(len(complete_times) * 0.95)]:.3f}秒")
            print(f"  P99: {sorted(complete_times)[int(len(complete_times) * 0.99)]:.3f}秒")
    
    # 吞吐量统计
    if performance_stats['task_complete_times']:
        total_tasks = len(performance_stats['task_complete_times'])
        if performance_stats['start_time'] and performance_stats['end_time']:
            total_time = performance_stats['end_time'] - performance_stats['start_time']
            tps = total_tasks / total_time if total_time > 0 else 0
            print(f"\n【系统吞吐量】")
            print(f"  总完成任务数: {total_tasks}")
            print(f"  吞吐量(TPS): {tps:.2f} 任务/秒")
    
    # 错误统计
    if performance_stats['errors']:
        print(f"\n【错误统计】")
        print(f"  总错误数: {len(performance_stats['errors'])}")
        print(f"  错误率: {len(performance_stats['errors']) / (len(performance_stats['task_complete_times']) + len(performance_stats['errors'])) * 100:.2f}%")
        
        # 错误分类统计
        error_types = {}
        for error in performance_stats['errors']:
            error_type = error.split(':')[0]
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        print(f"  错误分类:")
        for error_type, count in error_types.items():
            print(f"    {error_type}: {count} 次")
    
    print("="*60)

async def run_performance_test():
    """运行性能测试"""
    print("="*60)
    print("绿色金融管理系统性能测试")
    print("="*60)
    print(f"并发用户数: {CONCURRENT_USERS}")
    print(f"测试持续时间: {TEST_DURATION}秒")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    print()
    
    # 首先创建测试用户
    print("准备测试用户...")
    print("使用现有的测试用户（testuser_19_0 到 testuser_20_9）")
    print()
    
    testers = []
    
    # 创建测试用户 - 望京支行
    print("检查望京支行测试用户...")
    wangjing_users = []
    for i in range(3):
        username = f'testuser_21_{i}'
        testers.append(PerformanceTester(i, username, '123456'))
        wangjing_users.append(i)
    
    # 创建测试用户 - 副中心支行
    print("检查副中心支行测试用户...")
    fuzhongxin_users = []
    for i in range(3, 5):
        username = f'testuser_20_{i-3}'
        testers.append(PerformanceTester(i, username, '123456'))
        fuzhongxin_users.append(i)
    
    print(f"已准备 {len(testers)} 个测试用户:")
    print(f"  望京支行: 3 个用户")
    print(f"  副中心支行: 2 个用户")
    print()
    
    # 开始测试
    performance_stats['start_time'] = time.time()
    performance_stats['concurrent_users'] = CONCURRENT_USERS
    
    stop_event = asyncio.Event()
    
    # 设置停止时间
    async def stop_after_duration():
        await asyncio.sleep(TEST_DURATION)
        stop_event.set()
    
    # 运行测试
    print("开始性能测试...")
    tasks = [asyncio.create_task(tester.run(stop_event)) for tester in testers]
    
    # 监控任务
    monitor_task = asyncio.create_task(stop_after_duration())
    
    # 等待测试完成
    await asyncio.gather(*tasks, monitor_task)
    
    performance_stats['end_time'] = time.time()
    
    print()
    print("性能测试完成！")
    
    # 打印统计结果
    print_statistics()
    
    # 保存测试报告
    report = {
        'test_time': datetime.now().isoformat(),
        'concurrent_users': CONCURRENT_USERS,
        'test_duration': TEST_DURATION,
        'statistics': performance_stats
    }
    
    report_file = f"performance_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n测试报告已保存到: {report_file}")

if __name__ == '__main__':
    try:
        asyncio.run(run_performance_test())
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试异常: {e}")
        import traceback
        traceback.print_exc()