"""
BPMN XML 解析服务
用于从 BPMN XML 中提取流程定义、节点和连接关系
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class BPMNNode:
    """BPMN 节点"""
    id: str
    name: str
    type: str  # 'start', 'end', 'task', 'gateway'
    task_key: Optional[str] = None  # 任务键，用于匹配处理人


@dataclass
class BPMNFlow:
    """BPMN 序列流"""
    id: str
    source_ref: str  # 源节点引用
    target_ref: str  # 目标节点引用
    condition_expression: Optional[str] = None


class BPMNParser:
    """BPMN XML 解析器"""
    
    # BPMN 命名空间
    NAMESPACES = {
        'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
        'bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
        'dc': 'http://www.omg.org/spec/DD/20100524/DC',
        'di': 'http://www.omg.org/spec/DD/20100524/DI'
    }
    
    @staticmethod
    def parse(xml_string: str) -> Dict[str, any]:
        """解析 BPMN XML"""
        try:
            root = ET.fromstring(xml_string)
            
            # 提取流程定义信息
            process_name = BPMNParser._extract_process_name(root)
            process_id = BPMNParser._extract_process_id(root)
            
            # 提取所有节点
            nodes = BPMNParser._extract_nodes(root)
            
            # 提取所有序列流（连接关系）
            flows = BPMNParser._extract_flows(root)
            
            # 构建流程图（邻接表）
            flow_graph = BPMNParser._build_flow_graph(nodes, flows)
            
            # 识别流程起始节点
            start_nodes = [n for n in nodes if n.type == 'start']
            
            return {
                'name': process_name,
                'id': process_id,
                'nodes': nodes,
                'flows': flows,
                'flow_graph': flow_graph,
                'start_nodes': start_nodes
            }
        except Exception as e:
            raise ValueError(f"解析 BPMN XML 失败: {str(e)}")
    
    @staticmethod
    def _extract_process_name(root) -> str:
        """提取流程名称"""
        # 查找 process 元素
        for prefix, namespace in BPMNParser.NAMESPACES.items():
            if prefix == 'bpmn':
                process = root.find(f'{{{namespace}}}process')
                if process is not None and process.get('name'):
                    return process.get('name')
        return '未命名流程'
    
    @staticmethod
    def _extract_process_id(root) -> str:
        """提取流程 ID"""
        for prefix, namespace in BPMNParser.NAMESPACES.items():
            if prefix == 'bpmn':
                process = root.find(f'{{{namespace}}}process')
                if process is not None and process.get('id'):
                    return process.get('id')
        return 'process'
    
    @staticmethod
    def _extract_nodes(root) -> List[BPMNNode]:
        """提取所有节点"""
        nodes = []
        
        for prefix, namespace in BPMNParser.NAMESPACES.items():
            if prefix == 'bpmn':
                # 查找 process 元素
                process = root.find(f'{{{namespace}}}process')
                if process is None:
                    continue
                
                # 提取开始事件
                for start_event in process.findall(f'{{{namespace}}}startEvent'):
                    node_id = start_event.get('id')
                    nodes.append(BPMNNode(
                        id=node_id,
                        name=start_event.get('name', node_id),
                        type='start'
                    ))
                
                # 提取结束事件
                for end_event in process.findall(f'{{{namespace}}}endEvent'):
                    node_id = end_event.get('id')
                    nodes.append(BPMNNode(
                        id=node_id,
                        name=end_event.get('name', node_id),
                        type='end'
                    ))
                
                # 提取用户任务
                for user_task in process.findall(f'{{{namespace}}}userTask'):
                    node_id = user_task.get('id')
                    task_key = user_task.get('id', '').replace('UserTask_', '').lower()
                    
                    nodes.append(BPMNNode(
                        id=node_id,
                        name=user_task.get('name', node_id),
                        type='task',
                        task_key=task_key
                    ))
                
                # 提取其他任务类型（serviceTask等）
                for task_type in ['task', 'serviceTask', 'scriptTask', 'businessRuleTask', 'receiveTask', 'sendTask', 'manualTask']:
                    for task in process.findall(f'{{{namespace}}}{task_type}'):
                        node_id = task.get('id')
                        task_key = task.get('id', '').replace(f'{task_type[:-4]}_', '').lower()
                        
                        nodes.append(BPMNNode(
                            id=node_id,
                            name=task.get('name', node_id),
                            type='task',
                            task_key=task_key
                        ))
                
                # 提取网关
                for gateway in process.findall(f'{{{namespace}}}exclusiveGateway'):
                    node_id = gateway.get('id')
                    nodes.append(BPMNNode(
                        id=node_id,
                        name=gateway.get('name', node_id),
                        type='gateway'
                    ))
                
                for gateway in process.findall(f'{{{namespace}}}parallelGateway'):
                    node_id = gateway.get('id')
                    nodes.append(BPMNNode(
                        id=node_id,
                        name=gateway.get('name', node_id),
                        type='gateway'
                    ))
        
        return nodes
    
    @staticmethod
    def _extract_flows(root) -> List[BPMNFlow]:
        """提取所有序列流"""
        flows = []
        
        for prefix, namespace in BPMNParser.NAMESPACES.items():
            if prefix == 'bpmn':
                # 查找 process 元素
                process = root.find(f'{{{namespace}}}process')
                if process is None:
                    continue
                
                # 提取序列流
                for sequence_flow in process.findall(f'{{{namespace}}}sequenceFlow'):
                    flow_id = sequence_flow.get('id')
                    source_ref = sequence_flow.get('sourceRef')
                    target_ref = sequence_flow.get('targetRef')
                    
                    # 检查是否有条件表达式
                    condition_expression = None
                    condition = sequence_flow.find(f'{{{namespace}}}conditionExpression')
                    if condition is not None and condition.get('body'):
                        condition_expression = condition.get('body')
                    
                    flows.append(BPMNFlow(
                        id=flow_id,
                        source_ref=source_ref,
                        target_ref=target_ref,
                        condition_expression=condition_expression
                    ))
        
        return flows
    
    @staticmethod
    def _build_flow_graph(nodes: List[BPMNNode], flows: List[BPMNFlow]) -> Dict[str, List[str]]:
        """构建流程图（邻接表）"""
        graph = {node.id: [] for node in nodes}
        
        for flow in flows:
            if flow.source_ref in graph and flow.target_ref in graph:
                graph[flow.source_ref].append(flow.target_ref)
        
        return graph