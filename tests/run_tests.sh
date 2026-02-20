#!/bin/bash

# 测试执行脚本
# 一键运行压力测试和渗透测试

BASE_DIR="/Users/bryant/workbench/gfms/tests"
REPORT_DIR="$BASE_DIR/reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  绿色金融管理系统测试套件${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 创建报告目录
mkdir -p "$REPORT_DIR"

# 检查服务是否运行
echo -e "${YELLOW}检查服务状态...${NC}"
if curl -s http://localhost:8000 > /dev/null; then
    echo -e "${GREEN}✓ 后端服务运行正常${NC}"
else
    echo -e "${RED}✗ 后端服务未运行${NC}"
    echo "请先启动后端服务:"
    echo "cd /Users/bryant/workbench/gfms/backend"
    echo "python3.9 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    exit 1
fi

if curl -s http://localhost:5173 > /dev/null; then
    echo -e "${GREEN}✓ 前端服务运行正常${NC}"
else
    echo -e "${YELLOW}⚠ 前端服务未运行（可选）${NC}"
fi

echo ""
echo -e "${YELLOW}请选择测试类型:${NC}"
echo "1. 压力测试"
echo "2. 渗透测试"
echo "3. 全部测试"
echo "4. 退出"

read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        echo -e "\n${GREEN}开始压力测试...${NC}\n"
        cd "$BASE_DIR"
        python3 load_test.py | tee "$REPORT_DIR/load_test_$TIMESTAMP.log"
        ;;
    2)
        echo -e "\n${GREEN}开始渗透测试...${NC}\n"
        cd "$BASE_DIR"
        python3 security_test.py
        ;;
    3)
        echo -e "\n${GREEN}开始全部测试...${NC}\n"

        echo -e "${BLUE}===== 压力测试 =====${NC}\n"
        cd "$BASE_DIR"
        python3 load_test.py | tee "$REPORT_DIR/load_test_$TIMESTAMP.log"

        echo -e "\n${BLUE}===== 渗透测试 =====${NC}\n"
        python3 security_test.py

        echo -e "\n${GREEN}全部测试完成！${NC}"
        echo "报告保存在: $REPORT_DIR"
        ;;
    4)
        echo "退出"
        exit 0
        ;;
    *)
        echo -e "${RED}无效选项${NC}"
        exit 1
        ;;
esac

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}测试完成${NC}"
echo -e "${BLUE}========================================${NC}"