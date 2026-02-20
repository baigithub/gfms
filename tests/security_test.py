#!/usr/bin/env python3
"""
渗透测试脚本 - 绿色金融管理系统
用于发现安全漏洞（防御性安全测试）
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"
USERNAME = "tyyzy"
PASSWORD = "123456"

class SecurityTester:
    def __init__(self):
        self.token = None
        self.session = requests.Session()
        self.vulnerabilities = []

    def log_vulnerability(self, severity, title, description, evidence=None):
        """记录漏洞"""
        vulnerability = {
            'severity': severity,
            'title': title,
            'description': description,
            'evidence': evidence,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.vulnerabilities.append(vulnerability)
        print(f"\n[{'!'*10}] 发现漏洞!")
        print(f"严重程度: {severity}")
        print(f"标题: {title}")
        print(f"描述: {description}")
        if evidence:
            print(f"证据: {evidence}")

    def test_login_sql_injection(self):
        """测试登录接口的 SQL 注入"""
        print(f"\n{'='*50}")
        print(f"测试 1: 登录接口 SQL 注入")
        print(f"{'='*50}")

        # 常见的 SQL 注入 payload
        payloads = [
            "' OR '1'='1",
            "' OR '1'='1' --",
            "admin' --",
            "' UNION SELECT 1,2,3 --",
            "1' OR '1'='1",
            "admin')#"
        ]

        for payload in payloads:
            try:
                response = self.session.post(
                    f"{BASE_URL}/api/auth/login",
                    json={"username": payload, "password": "test"},
                    timeout=5
                )

                if response.status_code == 200:
                    data = response.json()
                    if 'access_token' in data:
                        self.log_vulnerability(
                            severity="HIGH",
                            title="登录接口存在 SQL 注入漏洞",
                            description=f"使用 payload '{payload}' 成功登录",
                            evidence=f"Payload: {payload}"
                        )
            except Exception as e:
                pass

        print("✓ SQL 注入测试完成")

    def test_xss_in_identifications(self):
        """测试绿色认定接口的 XSS"""
        print(f"\n{'='*50}")
        print(f"测试 2: XSS 跨站脚本测试")
        print(f"{'='*50}")

        # 登录获取 token
        if not self.login():
            return

        # XSS payload
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "'><script>alert('XSS')</script>",
            "<script>document.cookie</script>"
        ]

        for payload in xss_payloads:
            try:
                # 尝试在客户名称中注入 XSS
                response = self.session.get(
                    f"{BASE_URL}/api/identifications?customer_name={payload}",
                    headers={"Authorization": f"Bearer {self.token}"},
                    timeout=5
                )

                if payload in response.text:
                    self.log_vulnerability(
                        severity="MEDIUM",
                        title="XSS 跨站脚本漏洞",
                        description=f"XSS payload 被反射到响应中",
                        evidence=f"Payload: {payload}"
                    )
            except Exception as e:
                pass

        print("✓ XSS 测试完成")

    def test_authentication_bypass(self):
        """测试认证绕过"""
        print(f"\n{'='*50}")
        print(f"测试 3: 认证绕过测试")
        print(f"{'='*50}")

        # 尝试不使用 token 访问受保护的接口
        protected_endpoints = [
            "/api/dashboard",
            "/api/identifications",
            "/api/tasks/pending",
            "/api/tasks/online-report"
        ]

        for endpoint in protected_endpoints:
            try:
                # 不带 token 访问
                response = self.session.get(f"{BASE_URL}{endpoint}", timeout=5)

                # 检查是否返回 401 Unauthorized
                if response.status_code != 401 and response.status_code != 403:
                    self.log_vulnerability(
                        severity="CRITICAL",
                        title="认证绕过漏洞",
                        description=f"接口 {endpoint} 可以在没有认证的情况下访问",
                        evidence=f"状态码: {response.status_code}"
                    )
            except Exception as e:
                pass

        # 尝试使用伪造的 token
        fake_tokens = [
            "fake_token_12345",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.fake",
            "Bearer invalid_token"
        ]

        for fake_token in fake_tokens:
            for endpoint in protected_endpoints:
                try:
                    response = self.session.get(
                        f"{BASE_URL}{endpoint}",
                        headers={"Authorization": fake_token},
                        timeout=5
                    )

                    if response.status_code == 200:
                        self.log_vulnerability(
                            severity="HIGH",
                            title="认证绕过 - 伪造 Token",
                            description=f"使用伪造 token 成功访问 {endpoint}",
                            evidence=f"Fake token: {fake_token}"
                        )
                except Exception as e:
                    pass

        print("✓ 认证绕过测试完成")

    def test_privilege_escalation(self):
        """测试权限提升"""
        print(f"\n{'='*50}")
        print(f"测试 4: 权限提升测试")
        print(f"{'='*50}")

        if not self.login():
            return

        # 尝试访问管理员接口
        admin_endpoints = [
            "/api/users",
            "/api/organizations",
            "/api/system/config"
        ]

        for endpoint in admin_endpoints:
            try:
                response = self.session.get(
                    f"{BASE_URL}{endpoint}",
                    headers={"Authorization": f"Bearer {self.token}"},
                    timeout=5
                )

                if response.status_code == 200:
                    self.log_vulnerability(
                        severity="HIGH",
                        title="权限提升漏洞",
                        description=f"普通用户可以访问管理员接口 {endpoint}",
                        evidence=f"状态码: {response.status_code}"
                    )
            except Exception as e:
                pass

        print("✓ 权限提升测试完成")

    def test_information_disclosure(self):
        """测试敏感信息泄露"""
        print(f"\n{'='*50}")
        print(f"测试 5: 敏感信息泄露测试")
        print(f"{'='*50}")

        sensitive_keywords = [
            "password",
            "secret",
            "token",
            "api_key",
            "database",
            "sql",
            "error"
        ]

        endpoints_to_test = [
            "/api/identifications",
            "/api/tasks/pending",
            "/api/dashboard"
        ]

        if not self.login():
            return

        for endpoint in endpoints_to_test:
            try:
                response = self.session.get(
                    f"{BASE_URL}{endpoint}",
                    headers={"Authorization": f"Bearer {self.token}"},
                    timeout=5
                )

                response_text = response.text.lower()
                for keyword in sensitive_keywords:
                    if keyword in response_text:
                        # 检查是否是正常的关键词（如 "token" 在响应中可能是正常的）
                        # 这里简化处理，实际需要更细致的判断
                        if keyword in ["error", "sql"]:
                            self.log_vulnerability(
                                severity="LOW",
                                title="敏感信息泄露",
                                description=f"接口 {endpoint} 响应中包含关键词 '{keyword}'",
                                evidence=f"Keyword: {keyword}"
                            )
            except Exception as e:
                pass

        print("✓ 敏感信息泄露测试完成")

    def test_rate_limiting(self):
        """测试速率限制"""
        print(f"\n{'='*50}")
        print(f"测试 6: 速率限制测试")
        print(f"{'='*50}")

        # 快速发送大量登录请求
        success_count = 0
        for i in range(100):
            try:
                response = self.session.post(
                    f"{BASE_URL}/api/auth/login",
                    json={"username": "invalid", "password": "invalid"},
                    timeout=1
                )
                if response.status_code != 429:  # 429 Too Many Requests
                    success_count += 1
            except Exception as e:
                pass

        if success_count > 50:  # 如果超过 50 个请求都没有被限流
            self.log_vulnerability(
                severity="MEDIUM",
                title="缺少速率限制",
                description="登录接口没有实施速率限制，容易受到暴力破解攻击",
                evidence=f"100 个请求中有 {success_count} 个未被限流"
            )

        print("✓ 速率限制测试完成")

    def test_http_methods(self):
        """测试不安全的 HTTP 方法"""
        print(f"\n{'='*50}")
        print(f"测试 7: 不安全的 HTTP 方法测试")
        print(f"{'='*50}")

        methods_to_test = ["PUT", "DELETE", "OPTIONS", "TRACE"]
        endpoint = "/api/identifications"

        for method in methods_to_test:
            try:
                response = self.session.request(
                    method,
                    f"{BASE_URL}{endpoint}",
                    headers={"Authorization": f"Bearer {self.token}"},
                    timeout=5
                )

                # OPTIONS 和 TRACE 方法通常应该被禁用
                if method in ["OPTIONS", "TRACE"] and response.status_code != 405:
                    self.log_vulnerability(
                        severity="LOW",
                        title="不安全的 HTTP 方法",
                        description=f"接口 {endpoint} 允许 {method} 方法",
                        evidence=f"状态码: {response.status_code}"
                    )
            except Exception as e:
                pass

        print("✓ HTTP 方法测试完成")

    def test_cors_misconfiguration(self):
        """测试 CORS 配置"""
        print(f"\n{'='*50}")
        print(f"测试 8: CORS 配置测试")
        print(f"{'='*50}")

        headers = {
            "Origin": "http://evil.com",
            "Access-Control-Request-Method": "GET"
        }

        try:
            response = self.session.options(
                f"{BASE_URL}/api/identifications",
                headers=headers,
                timeout=5
            )

            cors_headers = response.headers
            if "Access-Control-Allow-Origin" in cors_headers:
                allowed_origin = cors_headers["Access-Control-Allow-Origin"]
                if allowed_origin == "*" or allowed_origin == "http://evil.com":
                    self.log_vulnerability(
                        severity="MEDIUM",
                        title="CORS 配置不当",
                        description="CORS 配置允许任意源访问",
                        evidence=f"Allowed-Origin: {allowed_origin}"
                    )
        except Exception as e:
            pass

        print("✓ CORS 配置测试完成")

    def test_session_management(self):
        """测试会话管理"""
        print(f"\n{'='*50}")
        print(f"测试 9: 会话管理测试")
        print(f"{'='*50}")

        if not self.login():
            return

        # 检查 token 是否有合理的过期时间
        # 这个测试需要分析 token 本身，这里简化处理
        print("  提示: 检查 token 的过期时间设置")
        print("  建议: Token 应该有合理的过期时间（如 1-8 小时）")

        print("✓ 会话管理测试完成")

    def test_input_validation(self):
        """测试输入验证"""
        print(f"\n{'='*50}")
        print(f"测试 10: 输入验证测试")
        print(f"{'='*50}")

        if not self.login():
            return

        # 测试超长输入
        long_string = "A" * 10000
        endpoints = [
            ("/api/identifications?customer_name=", long_string),
            ("/api/tasks/pending?status=", long_string)
        ]

        for endpoint, param in endpoints:
            try:
                response = self.session.get(
                    f"{BASE_URL}{endpoint}{param}",
                    headers={"Authorization": f"Bearer {self.token}"},
                    timeout=5
                )

                if response.status_code == 200:
                    print(f"  接口 {endpoint} 接受了超长输入（可能存在缓冲区溢出风险）")
                elif response.status_code == 413:  # Payload Too Large
                    print(f"  ✓ 接口 {endpoint} 正确拒绝了超长输入")
            except Exception as e:
                pass

        print("✓ 输入验证测试完成")

    def login(self):
        """登录获取 token"""
        try:
            response = self.session.post(
                f"{BASE_URL}/api/auth/login",
                json={"username": USERNAME, "password": PASSWORD},
                timeout=10
            )
            if response.status_code == 200:
                self.token = response.json().get('access_token')
                return True
        except Exception as e:
            return False
        return False

    def generate_report(self):
        """生成测试报告"""
        print(f"\n{'#'*50}")
        print(f"# 渗透测试报告")
        print(f"# 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"# 测试目标: {BASE_URL}")
        print(f"{'#'*50}")

        if not self.vulnerabilities:
            print("\n✓ 未发现明显的安全漏洞")
            print("\n建议:")
            print("1. 定期进行安全审计")
            print("2. 保持依赖库更新")
            print("3. 实施代码安全审查")
            print("4. 使用 Web 应用防火墙 (WAF)")
            return

        print(f"\n发现 {len(self.vulnerabilities)} 个漏洞:\n")

        # 按严重程度分类
        severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        for severity in severity_order:
            vulns = [v for v in self.vulnerabilities if v['severity'] == severity]
            if vulns:
                print(f"\n{'='*50}")
                print(f"{severity} 严重程度 ({len(vulns)} 个)")
                print(f"{'='*50}")
                for vuln in vulns:
                    print(f"\n标题: {vuln['title']}")
                    print(f"描述: {vuln['description']}")
                    if vuln['evidence']:
                        print(f"证据: {vuln['evidence']}")
                    print(f"时间: {vuln['timestamp']}")

        # 保存报告到文件
        report_file = f"/Users/bryant/workbench/gfms/tests/security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.vulnerabilities, f, ensure_ascii=False, indent=2)
        print(f"\n\n详细报告已保存到: {report_file}")

    def run_all_tests(self):
        """运行所有测试"""
        print(f"\n{'#'*50}")
        print(f"# 绿色金融管理系统渗透测试")
        print(f"# 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"# 测试目标: {BASE_URL}")
        print(f"{'#'*50}")

        # 运行各项测试
        self.test_login_sql_injection()
        self.test_xss_in_identifications()
        self.test_authentication_bypass()
        self.test_privilege_escalation()
        self.test_information_disclosure()
        self.test_rate_limiting()
        self.test_http_methods()
        self.test_cors_misconfiguration()
        self.test_session_management()
        self.test_input_validation()

        # 生成报告
        self.generate_report()

if __name__ == "__main__":
    print("警告: 此脚本仅用于授权的安全测试")
    print("使用此脚本前，请确保您有授权进行渗透测试\n")

    tester = SecurityTester()
    tester.run_all_tests()