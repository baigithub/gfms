#!/bin/bash

# 绿色金融管理系统性能测试执行脚本

echo "========================================================"
echo "  绿色金融管理系统性能测试"
echo "========================================================"
echo ""

# 检查Python环境
echo "检查Python环境..."
python3 --version
echo ""

# 安装依赖
echo "安装测试依赖..."
cd /Users/bryant/workbench/gfms/backend
pip3 install -r tests/requirements.txt
echo ""

# 检查后端服务状态
echo "检查后端服务..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✓ 后端服务运行正常"
else
    echo "✗ 后端服务未运行，请先启动后端服务"
    exit 1
fi
echo ""

# 询问是否生成测试数据
read -p "是否需要生成测试数据? (100万笔任务) [y/N]: " generate_data

if [ "$generate_data" = "y" ] || [ "$generate_data" = "Y" ]; then
    echo ""
    echo "========================================================"
    echo "  开始生成测试数据"
    echo "========================================================"
    echo ""
    
    # 预估时间：生成100万笔数据大约需要1-2小时
    echo "预计耗时: 1-2小时"
    echo ""
    read -p "确认开始生成数据? [y/N]: " confirm
    
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        python3 tests/generate_test_data.py
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✓ 测试数据生成完成"
        else
            echo ""
            echo "✗ 测试数据生成失败"
            exit 1
        fi
    else
        echo "已取消数据生成"
    fi
else
    echo "跳过数据生成步骤"
fi

echo ""

# 配置测试参数
read -p "并发用户数 [100]: " concurrent_users
concurrent_users=${concurrent_users:-100}

read -p "测试持续时间（秒）[300]: " test_duration
test_duration=${test_duration:-300}

echo ""
echo "========================================================"
echo "  性能测试配置"
echo "========================================================"
echo "并发用户数: $concurrent_users"
echo "测试持续时间: $test_duration 秒"
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================================"
echo ""

read -p "确认开始性能测试? [y/N]: " confirm

if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
    echo ""
    echo "开始性能测试..."
    echo ""
    
    # 启动性能测试
    python3 tests/performance_test.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "========================================================"
        echo "  ✓ 性能测试完成"
        echo "========================================================"
    else
        echo ""
        echo "========================================================"
        echo "  ✗ 性能测试失败"
        echo "========================================================"
        exit 1
    fi
else
    echo "已取消性能测试"
fi

echo ""
echo "测试脚本执行完成"