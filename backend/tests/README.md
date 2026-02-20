# 性能测试执行指南

## 快速开始

### 方法1: 使用自动化脚本（推荐）

```bash
cd /Users/bryant/workbench/gfms/backend
./tests/run_performance_test.sh
```

### 方法2: 手动执行

#### 1. 安装依赖
```bash
cd /Users/bryant/workbench/gfms/backend
pip3 install -r tests/requirements.txt
```

#### 2. 生成测试数据（可选）
```bash
python3 tests/generate_test_data.py
```

#### 3. 运行性能测试
```bash
python3 tests/performance_test.py
```

## 测试说明

### 数据生成
- **总量**: 100万笔待认定任务
- **分布**: 50万笔望京支行，50万笔副中心支行
- **并发**: 支持批量插入，每批1000笔
- **耗时**: 约1-2小时

### 性能测试
- **并发用户**: 100个（可配置）
- **测试时长**: 300秒（可配置）
- **测试场景**: 
  - 用户登录
  - 获取待办任务
  - 任务审批（同意）
- **测试方式**: 异步并发，模拟真实用户行为

## 性能指标

### 关键指标
1. **吞吐量 (TPS)**: 每秒处理的任务数
2. **响应时间**: 平均、P50、P95、P99
3. **错误率**: 失败请求占总请求的百分比
4. **并发数**: 同时处理的用户数

### 性能基准建议
- **登录响应时间**: < 2秒
- **任务加载时间**: < 1秒
- **任务审批时间**: < 3秒
- **系统吞吐量**: > 50 TPS
- **错误率**: < 1%

## 测试报告

测试完成后会生成JSON格式的测试报告，包含：
- 测试时间
- 并发用户数
- 测试持续时间
- 详细性能统计数据
- 错误信息

报告文件名: `performance_test_report_YYYYMMDD_HHMMSS.json`

## 监控建议

### 系统资源监控
在测试过程中，建议同时监控系统资源：

```bash
# 监控CPU和内存
top -p $(pgrep -f uvicorn)

# 监控数据库连接
mysql -e "SHOW PROCESSLIST;"

# 监控磁盘IO
iostat -x 1

# 监控网络
netstat -an | grep :8000
```

### 日志监控
```bash
# 实时查看后端日志
tail -f /Users/bryant/backend.log

# 查看错误日志
grep -i "error\|exception" /Users/bryant/backend.log | tail -100
```

## 故障排查

### 问题1: 数据库连接池耗尽
**现象**: 测试脚本报错 "database connection pool exhausted"

**解决方案**:
```python
# 在 app/config.py 中增加连接池大小
DATABASE_URL = "mysql://user:pass@host/db?pool_size=50&max_overflow=100"
```

### 问题2: 内存不足
**现象**: 系统响应变慢，OOM错误

**解决方案**:
- 减少并发用户数
- 减少批量插入批次大小
- 增加系统内存

### 问题3: 响应时间过长
**现象**: P95和P99响应时间超过10秒

**解决方案**:
- 检查数据库索引
- 优化慢查询
- 增加应用服务器实例

## 性能优化建议

### 数据库优化
```sql
-- 添加必要的索引
CREATE INDEX idx_identifications_status ON green_identifications(status);
CREATE INDEX idx_identifications_org_id ON green_identifications(org_id);
CREATE INDEX idx_workflow_tasks_assignee_status ON workflow_tasks(assignee_id, status);
CREATE INDEX idx_workflow_tasks_identification ON workflow_tasks(identification_id);
```

### 应用优化
1. 使用连接池
2. 启用查询缓存
3. 异步处理非关键操作
4. 添加限流机制

### 系统优化
1. 增加应用服务器实例
2. 使用负载均衡
3. 启用CDN
4. 数据库读写分离

## 安全注意事项

⚠️ **重要**: 
- 仅在测试环境执行
- 不要在生产环境运行
- 测试数据可能影响正常业务
- 测试完成后请清理测试数据

### 清理测试数据
```sql
-- 删除测试数据
DELETE FROM workflow_tasks WHERE assignee_id IN (
    SELECT id FROM users WHERE username LIKE 'testuser_%'
);

DELETE FROM workflow_instances WHERE identification_id IN (
    SELECT id FROM green_identifications WHERE initiator_id IN (
        SELECT id FROM users WHERE username LIKE 'testuser_%'
    )
);

DELETE FROM green_identifications WHERE initiator_id IN (
    SELECT id FROM users WHERE username LIKE 'testuser_%'
);

-- 删除测试用户
DELETE FROM users WHERE username LIKE 'testuser_%';
```