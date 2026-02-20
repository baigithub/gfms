# 快速开始指南

## 一键运行测试

```bash
cd /Users/bryant/workbench/gfms/tests
./run_tests.sh
```

## 手动运行测试

### 1. 压力测试

```bash
cd /Users/bryant/workbench/gfms/tests
python3 load_test.py
```

### 2. 渗透测试

```bash
cd /Users/bryant/workbench/gfms/tests
python3 security_test.py
```

## 测试前准备

### 确保服务运行

```bash
# 后端服务
cd /Users/bryant/workbench/gfms/backend
python3.9 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 前端服务（可选）
cd /Users/bryant/workbench/gfms/frontend
npm run dev -- --host
```

### 检查服务状态

```bash
# 检查后端
curl http://localhost:8000/api/health

# 检查前端
curl http://localhost:5173
```

## 测试结果

### 压力测试结果
- 控制台直接输出
- 自动保存到 `tests/reports/load_test_YYYYMMDD_HHMMSS.log`

### 渗透测试结果
- 控制台输出摘要
- 详细报告保存到 `tests/security_report_YYYYMMDD_HHMMSS.json`

## 测试说明

⚠️ **重要提示**:
1. 在测试环境进行测试
2. 测试前备份数据库
3. 不要在生产环境运行破坏性测试

📋 **测试内容**:
- 压力测试: 评估系统性能
- 渗透测试: 发现安全漏洞

📖 **详细文档**: 查看 `tests/README.md`