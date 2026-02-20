#!/usr/bin/env python3
"""初始化绿色认定流程模板"""
import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.workflow import ProcessDefinition, TaskNode
from app.models.user import Role

# 绿色认定流程BPMN XML
GREEN_IDENTIFICATION_BPMN = """<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
                 xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
                 xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
                 xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
                 id="Definitions_1"
                 targetNamespace="http://bpmn.io/schema/bpmn">
  <bpmn:process id="green_identification_process" isExecutable="false">
    <bpmn:startEvent id="StartEvent_1" name="开始"/>
    <bpmn:sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="Task_BranchManager"/>
    <bpmn:userTask id="Task_BranchManager" name="支行客户经理"/>
    <bpmn:sequenceFlow id="Flow_2" sourceRef="Task_BranchManager" targetRef="Task_SecondLevelManager"/>
    <bpmn:userTask id="Task_SecondLevelManager" name="二级分行绿色金融管理岗"/>
    <bpmn:sequenceFlow id="Flow_3" sourceRef="Task_SecondLevelManager" targetRef="Task_FirstLevelManager"/>
    <bpmn:userTask id="Task_FirstLevelManager" name="一级分行绿色金融管理岗"/>
    <bpmn:sequenceFlow id="Flow_4" sourceRef="Task_FirstLevelManager" targetRef="Task_FirstLevelReviewer"/>
    <bpmn:userTask id="Task_FirstLevelReviewer" name="一级分行绿色金融复核岗"/>
    <bpmn:sequenceFlow id="Flow_5" sourceRef="Task_FirstLevelReviewer" targetRef="EndEvent_1"/>
    <bpmn:endEvent id="EndEvent_1" name="结束"/>
  </bpmn:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="green_identification_process">
      <bpmndi:BPMNShape id="StartEvent_1_di" bpmnElement="StartEvent_1">
        <dc:Bounds x="100" y="150" width="36" height="36"/>
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task_BranchManager_di" bpmnElement="Task_BranchManager">
        <dc:Bounds x="200" y="128" width="120" height="80"/>
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task_SecondLevelManager_di" bpmnElement="Task_SecondLevelManager">
        <dc:Bounds x="370" y="128" width="120" height="80"/>
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task_FirstLevelManager_di" bpmnElement="Task_FirstLevelManager">
        <dc:Bounds x="540" y="128" width="120" height="80"/>
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task_FirstLevelReviewer_di" bpmnElement="Task_FirstLevelReviewer">
        <dc:Bounds x="710" y="128" width="120" height="80"/>
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="EndEvent_1_di" bpmnElement="EndEvent_1">
        <dc:Bounds x="880" y="150" width="36" height="36"/>
      </bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="Flow_1_di" bpmnElement="Flow_1">
        <di:waypoint x="136" y="168"/>
        <di:waypoint x="200" y="168"/>
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_2_di" bpmnElement="Flow_2">
        <di:waypoint x="320" y="168"/>
        <di:waypoint x="370" y="168"/>
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_3_di" bpmnElement="Flow_3">
        <di:waypoint x="490" y="168"/>
        <di:waypoint x="540" y="168"/>
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_4_di" bpmnElement="Flow_4">
        <di:waypoint x="660" y="168"/>
        <di:waypoint x="710" y="168"/>
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_5_di" bpmnElement="Flow_5">
        <di:waypoint x="830" y="168"/>
        <di:waypoint x="880" y="168"/>
      </bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>"""


def init_green_workflow():
    """初始化绿色认定流程"""
    db = SessionLocal()
    
    try:
        # 检查是否已存在
        existing = db.query(ProcessDefinition).filter(
            ProcessDefinition.key == "green_identification"
        ).first()
        
        if existing:
            print("绿色认定流程已存在，跳过创建")
            return
        
        # 创建流程定义
        definition = ProcessDefinition(
            key="green_identification",
            name="绿色认定流程",
            version=1,
            description="绿色贷款认定审批流程：支行客户经理→二级分行绿色金融管理岗→一级分行绿色金融管理岗→一级分行绿色金融复核岗",
            bpmn_xml=GREEN_IDENTIFICATION_BPMN,
            status="active",
            deployed_by=1,  # 系统管理员
            deployed_at=datetime.now()
        )
        
        db.add(definition)
        db.flush()
        
        # 创建任务节点
        nodes = [
            {
                "node_id": "Task_BranchManager",
                "node_name": "支行客户经理",
                "node_type": "userTask",
                "role_id": None,  # 可以后续关联角色
                "org_level": "branch",
                "is_skip_if_empty": 0,  # 第一个节点不能跳过
                "sequence": 1
            },
            {
                "node_id": "Task_SecondLevelManager",
                "node_name": "二级分行绿色金融管理岗",
                "node_type": "userTask",
                "role_id": None,
                "org_level": "second_level",
                "is_skip_if_empty": 1,  # 无人员时自动跳过
                "sequence": 2
            },
            {
                "node_id": "Task_FirstLevelManager",
                "node_name": "一级分行绿色金融管理岗",
                "node_type": "userTask",
                "role_id": None,
                "org_level": "first_level",
                "is_skip_if_empty": 1,  # 无人员时自动跳过
                "sequence": 3
            },
            {
                "node_id": "Task_FirstLevelReviewer",
                "node_name": "一级分行绿色金融复核岗",
                "node_type": "userTask",
                "role_id": None,
                "org_level": "first_level",
                "is_skip_if_empty": 1,  # 无人员时自动跳过
                "sequence": 4
            }
        ]
        
        for node_data in nodes:
            node = TaskNode(
                definition_id=definition.id,
                **node_data
            )
            db.add(node)
        
        db.commit()
        print(f"✓ 成功创建绿色认定流程: {definition.name} (ID: {definition.id})")
        print(f"✓ 创建了 {len(nodes)} 个审批节点")
        
        for node in nodes:
            skip_text = "自动跳过" if node["is_skip_if_empty"] else "不跳过"
            print(f"  - {node['node_name']} ({skip_text})")
            
    except Exception as e:
        print(f"✗ 创建流程失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_green_workflow()