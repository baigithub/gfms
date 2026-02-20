#!/bin/bash

# 绿色金融管理系统 - Docker启动脚本

echo "======================================"
echo "绿色金融管理系统 - Docker启动脚本"
echo "======================================"

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "错误: Docker未运行，请先启动Docker"
    exit 1
fi

# 停止并删除旧容器
echo "停止旧容器..."
docker-compose down

# 启动MySQL容器
echo "启动MySQL容器..."
docker-compose up -d mysql

# 等待MySQL启动
echo "等待MySQL启动..."
sleep 10

# 检查MySQL是否就绪
echo "检查MySQL连接..."
until docker exec gfms-mysql mysqladmin ping -h"localhost" --silent; do
    echo "等待MySQL就绪..."
    sleep 2
done

echo "======================================"
echo "MySQL已启动并就绪！"
echo "======================================"
echo ""
echo "数据库连接信息："
echo "  主机: localhost"
echo "  端口: 3306"
echo "  数据库: green_finance"
echo "  用户: gfms_user"
echo "  密码: gfms_password"
echo "  Root密码: root123456"
echo ""
echo "默认用户账号："
echo "  admin / 123456 (超级管理员)"
echo "  manager1 / 123456 (客户经理)"
echo "  reviewer1 / 123456 (绿色金融管理岗)"
echo "  auditor1 / 123456 (绿色金融复核岗)"
echo ""
echo "======================================"
echo "请启动后端服务："
echo "  cd backend"
echo "  export IS_DOCKER=true"
echo "  pip install -r requirements.txt"
echo "  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "请启动前端服务："
echo "  cd frontend"
echo "  npm install"
echo "  npm run dev"
echo "======================================"