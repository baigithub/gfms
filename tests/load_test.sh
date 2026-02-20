#!/bin/bash

# 压力测试脚本 - 使用 Apache Bench
# 测试目标：绿色金融管理系统

BASE_URL="http://localhost:8000"
TOKEN=""  # 需要先登录获取 token

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== 绿色金融管理系统压力测试 ===${NC}"
echo ""

# 检查是否安装了 ab
if ! command -v ab &> /dev/null; then
    echo -e "${RED}错误: Apache Bench (ab) 未安装${NC}"
    echo "请先安装: brew install apache2"
    exit 1
fi

# 1. 登录获取 token
echo -e "${YELLOW}1. 登录获取 token...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "tyyzy", "password": "123456"}')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}登录失败，无法获取 token${NC}"
    exit 1
fi

echo -e "${GREEN}Token 获取成功${NC}"
echo ""

# 2. 测试登录接口
echo -e "${YELLOW}2. 测试登录接口 (1000 请求, 100 并发)...${NC}"
ab -n 1000 -c 100 -T "application/json" \
  -p login_data.json \
  "${BASE_URL}/api/auth/login"
echo ""

# 3. 测试工作台接口
echo -e "${YELLOW}3. 测试工作台接口 (500 请求, 50 并发)...${NC}"
ab -n 500 -c 50 -H "Authorization: Bearer ${TOKEN}" \
  "${BASE_URL}/api/dashboard"
echo ""

# 4. 测试待办任务接口
echo -e "${YELLOW}4. 测试待办任务接口 (500 请求, 50 并发)...${NC}"
ab -n 500 -c 50 -H "Authorization: Bearer ${TOKEN}" \
  "${BASE_URL}/api/tasks/pending?page=1&page_size=10"
echo ""

# 5. 测试绿色认定列表接口
echo -e "${YELLOW}5. 测试绿色认定列表接口 (500 请求, 50 并发)...${NC}"
ab -n 500 -c 50 -H "Authorization: Bearer ${TOKEN}" \
  "${BASE_URL}/api/identifications?page=1&page_size=10"
echo ""

# 6. 测试在线报表接口
echo -e "${YELLOW}6. 测试在线报表接口 (200 请求, 20 并发)...${NC}"
ab -n 200 -c 20 -H "Authorization: Bearer ${TOKEN}" \
  "${BASE_URL}/api/tasks/online-report?page=1&page_size=20"
echo ""

echo -e "${GREEN}=== 压力测试完成 ===${NC}"