#!/usr/bin/env python3
"""生成绿色认定测试数据"""
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from app.models.green_finance import GreenIdentification, WorkflowInstance, WorkflowTask
from app.models.user import User, Role, Organization

# 测试数据
CUSTOMERS = [
    ("绿色能源科技有限公司", "新能源", "6222021200123456789", 5000000.00),
    ("环保产业集团", "节能环保", "6222021200123456790", 3000000.00),
    ("清洁能源股份公司", "新能源", "6222021200123456791", 8000000.00),
    ("绿色建材制造厂", "绿色建筑", "6222021200123456792", 2000000.00),
    ("生态农业发展公司", "生态农业", "6222021200123456793", 1500000.00),
    ("循环经济产业园", "循环经济", "6222021200123456794", 10000000.00),
    ("新能源汽车制造", "新能源", "6222021200123456795", 12000000.00),
    ("污水处理厂", "节能环保", "6222021200123456796", 4000000.00),
    ("太阳能发电站", "新能源", "6222021200123456797", 6000000.00),
    ("绿色物流运输公司", "绿色交通", "6222021200123456798", 2500000.00),
    ("生态旅游开发公司", "生态旅游", "6222021200123456799", 1800000.00),
    ("环保设备制造商", "节能环保", "6222021200123456800", 3500000.00),
    ("绿色食品加工厂", "绿色食品", "6222021200123456801", 2200000.00),
    ("生物质能发电公司", "新能源", "6222021200123456802", 7000000.00),
    ("森林碳汇项目", "碳汇项目", "6222021200123456803", 9000000.00),
]

GREEN_PROJECTS = [
    "太阳能光伏发电项目",
    "风力发电项目",
    "新能源汽车生产线",
    "污水处理与回收利用",
    "绿色建筑材料生产",
    "有机农业种植",
    "生态旅游景区开发",
    "生物质能源利用",
    "工业废气治理",
    "废旧资源回收利用",
]

STATUSES = ["待处理", "审批中", "已完成", "已驳回"]

def generate_test_data():
    """生成测试数据"""
    db = next(get_db())
    
    # 获取第一个用户作为发起人
    creator = db.query(User).first()
    if not creator:
        print("请先创建用户数据")
        return
    
    # 获取审批角色
    approver = db.query(User).filter(User.id != creator.id).first()
    
    print(f"使用发起人: {creator.real_name}")
    if approver:
        print(f"使用审批人: {approver.real_name}")
    
    # 生成15条绿色认定数据
    for i, (customer_name, business_type, loan_account, loan_amount) in enumerate(CUSTOMERS):
        try:
            # 随机生成日期（过去30天内）
            days_ago = i * 2
            created_at = datetime.now() - timedelta(days=days_ago)
            loan_date = created_at - timedelta(days=1)
            
            # 随机状态
            status_idx = i % len(STATUSES)
            status = STATUSES[status_idx]
            
            # 绿色项目目录
            green_project = GREEN_PROJECTS[i % len(GREEN_PROJECTS)]
            
            # 创建绿色认定记录
            identification = GreenIdentification(
                loan_code=f"LN{datetime.now().strftime('%Y%m%d')}{i+1:04d}",
                customer_name=customer_name,
                business_type=business_type,
                loan_account=loan_account,
                loan_amount=loan_amount,
                disbursement_date=created_at,
                project_category_medium=green_project,
                status=status,
                initiator_id=creator.id,
                org_id=1
            )
            db.add(identification)
            db.flush()  # 获取ID
            
            # 创建工作流实例
            workflow = WorkflowInstance(
                identification_id=identification.id,
                case_id=f"WF{datetime.now().strftime('%Y%m%d')}{i+1:04d}",
                business_key=identification.loan_code,
                current_node="submit" if status == "待处理" else "approve",
                status="running" if status in ["待处理", "审批中"] else "completed",
                started_at=created_at,
                ended_at=created_at + timedelta(days=1) if status in ["已完成", "已驳回"] else None
            )
            db.add(workflow)
            db.flush()
            
            # 创建工作流任务
            if status == "待处理":
                # 待处理：只有发起任务
                task = WorkflowTask(
                    identification_id=identification.id,
                    workflow_instance_id=workflow.id,
                    task_key="submit",
                    task_name="提交申请",
                    node_id="submit_node",
                    status="已提交",
                    assignee_id=creator.id,
                    started_at=created_at,
                    completed_at=created_at + timedelta(minutes=10),
                    comment="提交绿色认定申请"
                )
                db.add(task)
            elif status == "审批中":
                # 审批中：已提交，当前在审批中
                task1 = WorkflowTask(
                    identification_id=identification.id,
                    workflow_instance_id=workflow.id,
                    task_key="submit",
                    task_name="提交申请",
                    node_id="submit_node",
                    status="已提交",
                    assignee_id=creator.id,
                    started_at=created_at,
                    completed_at=created_at + timedelta(minutes=10),
                    comment="提交绿色认定申请"
                )
                db.add(task1)
                
                if approver:
                    task2 = WorkflowTask(
                        identification_id=identification.id,
                        workflow_instance_id=workflow.id,
                        task_key="approve",
                        task_name="部门审批",
                        node_id="approve_node",
                        status="待处理",
                        assignee_id=approver.id,
                        started_at=created_at + timedelta(minutes=10),
                        comment="等待部门审批"
                    )
                    db.add(task2)
            elif status in ["已完成", "已驳回"]:
                # 已完成：有完整流程
                task1 = WorkflowTask(
                    identification_id=identification.id,
                    workflow_instance_id=workflow.id,
                    task_key="submit",
                    task_name="提交申请",
                    node_id="submit_node",
                    status="已提交",
                    assignee_id=creator.id,
                    started_at=created_at,
                    completed_at=created_at + timedelta(minutes=10),
                    comment="提交绿色认定申请"
                )
                db.add(task1)
                
                if approver:
                    result = "通过" if status == "已完成" else "驳回"
                    task2 = WorkflowTask(
                        identification_id=identification.id,
                        workflow_instance_id=workflow.id,
                        task_key="approve",
                        task_name="部门审批",
                        node_id="approve_node",
                        status="已完成",
                        approval_result=result,
                        assignee_id=approver.id,
                        started_at=created_at + timedelta(minutes=10),
                        completed_at=created_at + timedelta(hours=1),
                        comment=f"审批{result}，绿色项目符合认定标准"
                    )
                    db.add(task2)
            
            print(f"创建记录 {i+1}/15: {customer_name} - {status}")
            
        except Exception as e:
            print(f"创建记录失败: {e}")
            db.rollback()
            continue
    
    db.commit()
    print(f"\n成功生成 {len(CUSTOMERS)} 条测试数据")

if __name__ == "__main__":
    generate_test_data()