#!/usr/bin/env python3
"""
压力测试脚本 - 使用 requests
测试目标：绿色金融管理系统
"""

import requests
import time
import threading
import statistics
from datetime import datetime

BASE_URL = "http://localhost:8000"
USERNAME = "tyyzy"
PASSWORD = "123456"

class LoadTester:
    def __init__(self):
        self.token = None
        self.results = {
            'login': [],
            'dashboard': [],
            'pending_tasks': [],
            'identifications': [],
            'online_report': []
        }

    def login(self):
        """登录获取 token"""
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"username": USERNAME, "password": PASSWORD},
                timeout=10
            )
            if response.status_code == 200:
                self.token = response.json().get('access_token')
                print(f"✓ 登录成功")
                return True
            else:
                print(f"✗ 登录失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ 登录异常: {e}")
            return False

    def test_login(self, num_requests=100):
        """测试登录接口"""
        print(f"\n{'='*50}")
        print(f"测试登录接口 - {num_requests} 请求")
        print(f"{'='*50}")

        times = []
        errors = 0

        for i in range(num_requests):
            start = time.time()
            try:
                response = requests.post(
                    f"{BASE_URL}/api/auth/login",
                    json={"username": USERNAME, "password": PASSWORD},
                    timeout=10
                )
                end = time.time()
                elapsed = (end - start) * 1000
                times.append(elapsed)

                if response.status_code != 200:
                    errors += 1
            except Exception as e:
                errors += 1

        self.results['login'] = times
        self.print_stats('登录接口', times, errors, num_requests)

    def test_dashboard(self, num_requests=100, concurrency=10):
        """测试工作台接口"""
        print(f"\n{'='*50}")
        print(f"测试工作台接口 - {num_requests} 请求, {concurrency} 并发")
        print(f"{'='*50}")

        times = []
        errors = 0

        def worker():
            nonlocal errors
            for i in range(num_requests // concurrency):
                start = time.time()
                try:
                    response = requests.get(
                        f"{BASE_URL}/api/dashboard",
                        headers={"Authorization": f"Bearer {self.token}"},
                        timeout=10
                    )
                    end = time.time()
                    elapsed = (end - start) * 1000
                    times.append(elapsed)

                    if response.status_code != 200:
                        errors += 1
                except Exception as e:
                    errors += 1

        threads = []
        start_time = time.time()
        for i in range(concurrency):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        total_time = (time.time() - start_time) * 1000
        self.results['dashboard'] = times
        self.print_stats('工作台接口', times, errors, num_requests, total_time)

    def test_pending_tasks(self, num_requests=100, concurrency=10):
        """测试待办任务接口"""
        print(f"\n{'='*50}")
        print(f"测试待办任务接口 - {num_requests} 请求, {concurrency} 并发")
        print(f"{'='*50}")

        times = []
        errors = 0

        def worker():
            nonlocal errors
            for i in range(num_requests // concurrency):
                start = time.time()
                try:
                    response = requests.get(
                        f"{BASE_URL}/api/tasks/pending?page=1&page_size=10",
                        headers={"Authorization": f"Bearer {self.token}"},
                        timeout=10
                    )
                    end = time.time()
                    elapsed = (end - start) * 1000
                    times.append(elapsed)

                    if response.status_code != 200:
                        errors += 1
                except Exception as e:
                    errors += 1

        threads = []
        start_time = time.time()
        for i in range(concurrency):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        total_time = (time.time() - start_time) * 1000
        self.results['pending_tasks'] = times
        self.print_stats('待办任务接口', times, errors, num_requests, total_time)

    def test_online_report(self, num_requests=50, concurrency=5):
        """测试在线报表接口"""
        print(f"\n{'='*50}")
        print(f"测试在线报表接口 - {num_requests} 请求, {concurrency} 并发")
        print(f"{'='*50}")

        times = []
        errors = 0

        def worker():
            nonlocal errors
            for i in range(num_requests // concurrency):
                start = time.time()
                try:
                    response = requests.get(
                        f"{BASE_URL}/api/tasks/online-report?page=1&page_size=20",
                        headers={"Authorization": f"Bearer {self.token}"},
                        timeout=10
                    )
                    end = time.time()
                    elapsed = (end - start) * 1000
                    times.append(elapsed)

                    if response.status_code != 200:
                        errors += 1
                except Exception as e:
                    errors += 1

        threads = []
        start_time = time.time()
        for i in range(concurrency):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        total_time = (time.time() - start_time) * 1000
        self.results['online_report'] = times
        self.print_stats('在线报表接口', times, errors, num_requests, total_time)

    def print_stats(self, name, times, errors, total_requests, total_time=None):
        """打印统计信息"""
        if not times:
            print(f"✗ {name}: 无数据")
            return

        success_rate = ((total_requests - errors) / total_requests) * 100
        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        min_time = min(times)
        max_time = max(times)
        p95_time = statistics.quantiles(times, n=20)[18] if len(times) >= 20 else max_time

        print(f"✓ {name} 结果:")
        print(f"  总请求数: {total_requests}")
        print(f"  成功请求: {total_requests - errors}")
        print(f"  失败请求: {errors}")
        print(f"  成功率: {success_rate:.2f}%")
        print(f"  平均响应时间: {avg_time:.2f} ms")
        print(f"  中位数响应时间: {median_time:.2f} ms")
        print(f"  最小响应时间: {min_time:.2f} ms")
        print(f"  最大响应时间: {max_time:.2f} ms")
        print(f"  P95 响应时间: {p95_time:.2f} ms")

        if total_time:
            rps = (total_requests / total_time) * 1000
            print(f"  总耗时: {total_time:.2f} ms")
            print(f"  RPS (每秒请求数): {rps:.2f}")

    def run_all_tests(self):
        """运行所有测试"""
        print(f"\n{'#'*50}")
        print(f"# 绿色金融管理系统压力测试")
        print(f"# 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"# 测试目标: {BASE_URL}")
        print(f"{'#'*50}")

        # 登录
        if not self.login():
            return

        # 顺序测试（避免并发压力过大）
        self.test_login(num_requests=100)
        self.test_dashboard(num_requests=100, concurrency=10)
        self.test_pending_tasks(num_requests=100, concurrency=10)
        self.test_online_report(num_requests=50, concurrency=5)

        # 汇总报告
        print(f"\n{'='*50}")
        print(f"测试汇总")
        print(f"{'='*50}")
        for api, times in self.results.items():
            if times:
                print(f"{api}: {len(times)} 个请求, 平均 {statistics.mean(times):.2f} ms")

if __name__ == "__main__":
    tester = LoadTester()
    tester.run_all_tests()