# 绿色金融管理系统测试方案

## 目录
1. [压力测试](#压力测试)
2. [渗透测试](#渗透测试)
3. [测试报告](#测试报告)

---

## 压力测试

### 目的
评估系统在高并发情况下的性能表现，发现性能瓶颈。

### 测试工具
- Apache Bench (ab)
- Python requests + threading

### 测试脚本

#### 1. 使用 Apache Bench

```bash
cd /Users/bryant/workbench/gfms/tests
chmod +x load_test.sh
./load_test.sh
```

#### 2. 使用 Python 脚本

```bash
cd /Users/bryant/workbench/gfms/tests
python3 load_test.py
```

### 测试指标

| 指标 | 说明 | 目标值 |
|------|------|--------|
| 响应时间 | 请求到响应的时间 | < 500ms (P95) |
| 成功率 | 成功请求数 / 总请求数 | > 99% |
| RPS | 每秒请求数 | > 50 |
| 错误率 | 失败请求数 / 总请求数 | < 1% |

### 测试场景

1. **登录接口压力测试**
   - 请求次数: 1000
   - 并发数: 100
   - 预期: 能处理高并发登录请求

2. **工作台接口压力测试**
   - 请求次数: 500
   - 并发数: 50
   - 预期: 快速加载工作台数据

3. **待办任务接口压力测试**
   - 请求次数: 500
   - 并发数: 50
   - 预期: 快速查询待办任务

4. **在线报表接口压力测试**
   - 请求次数: 200
   - 并发数: 20
   - 预期: 正常加载报表数据

---

## 渗透测试

### 目的
发现系统中的安全漏洞，确保系统安全。

### 测试脚本

```bash
cd /Users/bryant/workbench/gfms/tests
python3 security_test.py
```

### 测试项目

| 编号 | 测试项目 | 风险等级 | 描述 |
|------|----------|----------|------|
| 1 | SQL 注入 | 高 | 测试输入字段是否可以被注入 SQL 语句 |
| 2 | XSS 跨站脚本 | 中 | 测试输入字段是否可以被注入恶意脚本 |
| 3 | 认证绕过 | 严重 | 测试是否可以在没有认证的情况下访问受保护的接口 |
| 4 | 权限提升 | 高 | 测试普通用户是否可以访问管理员功能 |
| 5 | 敏感信息泄露 | 低 | 测试响应中是否包含敏感信息 |
| 6 | 速率限制 | 中 | 测试登录接口是否有速率限制 |
| 7 | HTTP 方法 | 低 | 测试是否启用了不安全的 HTTP 方法 |
| 8 | CORS 配置 | 中 | 测试 CORS 配置是否安全 |
| 9 | 会话管理 | 中 | 测试 token 过期时间是否合理 |
| 10 | 输入验证 | 中 | 测试输入验证是否完善 |

### 测试工具
- Python requests
- 手动测试配合 Burp Suite（可选）

---

## 测试报告

### 报告位置
- 压力测试报告: 控制台输出
- 渗透测试报告: `/Users/bryant/workbench/gfms/tests/security_report_YYYYMMDD_HHMMSS.json`

### 报告内容

#### 压力测试报告
```
==================================================
测试登录接口 - 100 请求
==================================================
✓ 登录接口 结果:
  总请求数: 100
  成功请求: 100
  失败请求: 0
  成功率: 100.00%
  平均响应时间: 245.32 ms
  中位数响应时间: 238.15 ms
  最小响应时间: 198.45 ms
  最大响应时间: 456.78 ms
  P95 响应时间: 398.23 ms
```

#### 渗透测试报告
```json
[
  {
    "severity": "HIGH",
    "title": "认证绕过漏洞",
    "description": "接口 /api/dashboard 可以在没有认证的情况下访问",
    "evidence": "状态码: 200",
    "timestamp": "2026-02-19 22:30:00"
  }
]
```

---

## 测试准备

### 1. 环境准备
```bash
# 确保服务正在运行
cd /Users/bryant/workbench/gfms/backend
python3.9 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

cd /Users/bryant/workbench/gfms/frontend
npm run dev -- --host
```

### 2. 安装依赖
```bash
# 安装 Apache Bench (macOS)
brew install apache2

# 安装 Python 依赖（应该已安装）
pip3 install requests
```

### 3. 准备测试数据
- 确保数据库中有测试数据
- 创建测试用户账号
- 准备测试用的绿色认定记录

---

## 安全建议

### 压力测试优化建议

1. **数据库优化**
   - 添加适当的索引
   - 优化慢查询
   - 使用连接池

2. **缓存策略**
   - 实现接口缓存
   - 使用 Redis 缓存热点数据

3. **异步处理**
   - 使用 Celery 处理耗时任务
   - 实现消息队列

### 渗透测试修复建议

1. **SQL 注入防护**
   - 使用参数化查询
   - 使用 ORM（已使用 SQLAlchemy）
   - 输入验证和过滤

2. **XSS 防护**
   - 对输出进行 HTML 转义
   - 使用 CSP (Content Security Policy)
   - 验证和过滤用户输入

3. **认证安全**
   - 实施 JWT token 过期机制
   - 实现 token 刷新机制
   - 使用 HTTPS

4. **速率限制**
   - 实施登录速率限制
   - 使用 Redis 存储请求计数
   - 设置合理的限制阈值

5. **输入验证**
   - 验证所有用户输入
   - 限制输入长度
   - 使用白名单验证

---

## 测试执行流程

### 1. 开始测试
```bash
# 确保服务正常运行
# 运行压力测试
cd /Users/bryant/workbench/gfms/tests
python3 load_test.py

# 运行渗透测试
python3 security_test.py
```

### 2. 分析结果
- 查看压力测试输出，分析性能瓶颈
- 查看渗透测试报告，评估安全风险

### 3. 修复问题
- 根据测试结果修复性能问题
- 根据安全报告修复安全漏洞

### 4. 重新测试
- 修复后重新运行测试
- 确认问题已解决

---

## 注意事项

1. **测试环境**
   - 建议在测试环境进行测试
   - 不要在生产环境进行破坏性测试

2. **数据备份**
   - 测试前备份数据库
   - 测试后恢复数据

3. **监控**
   - 测试时监控系统资源
   - 注意 CPU、内存、磁盘使用情况

4. **授权**
   - 确保有授权进行渗透测试
   - 不要对未授权的系统进行测试

---

## 附录

### 快速命令参考

```bash
# 启动后端服务
cd /Users/bryant/workbench/gfms/backend
python3.9 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 启动前端服务
cd /Users/bryant/workbench/gfms/frontend
npm run dev -- --host

# 运行压力测试
cd /Users/bryant/workbench/gfms/tests
python3 load_test.py

# 运行渗透测试
python3 security_test.py

# 查看后端日志
tail -f /tmp/backend.log

# 查看前端日志
tail -f /tmp/frontend.log

# 重启服务
pkill -f "uvicorn.*app.main"
pkill -f "vite"
```

### 联系方式
如有问题，请联系开发团队。