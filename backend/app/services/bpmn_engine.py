"""基于SpiffWorkflow的BPMN工作流引擎"""
import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.workflow import ProcessDefinition, ProcessInstance, ProcessTask, TaskNode
from app.models.user import User, Role


class BpmnWorkflowEngine:
    """BPMN工作流引擎"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def deploy_process(self, key: str, name: str, bpmn_xml: str, 
                       deployed_by: int, description: str = "") -> ProcessDefinition:
        """部署流程定义"""
        # 获取最新版本
        latest = self.db.query(ProcessDefinition).filter(
            ProcessDefinition.key == key
        ).order_by(ProcessDefinition.version.desc()).first()
        
        version = (latest.version + 1) if latest else 1
        
        definition = ProcessDefinition(
            key=key,
            name=name,
            version=version,
            description=description,
            bpmn_xml=bpmn_xml,
            status="active",
            deployed_by=deployed_by,
            deployed_at=datetime.now()
        )
        
        self.db.add(definition)
        self.db.commit()
        self.db.refresh(definition)
        
        return definition
    
    def start_instance(self, definition_id: int, business_key: str, 
                      started_by: int, variables: Dict[str, Any] = None) -> ProcessInstance:
        """启动流程实例"""
        definition = self.db.query(ProcessDefinition).get(definition_id)
        if not definition:
            raise ValueError("流程定义不存在")
        
        # 创建流程实例
        instance_key = f"{definition.key}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        instance = ProcessInstance(
            instance_key=instance_key,
            definition_id=definition_id,
            business_key=business_key,
            status="running",
            started_by=started_by,
            variables=json.dumps(variables or {})
        )
        
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        
        # 解析BPMN并启动流程
        self._execute_workflow(instance, definition, variables or {})
        
        return instance
    
    def _execute_workflow(self, instance: ProcessInstance, definition: ProcessDefinition, 
                         variables: Dict[str, Any]):
        """执行工作流逻辑"""
        # 获取任务节点配置
        task_nodes = self.db.query(TaskNode).filter(
            TaskNode.definition_id == definition.id
        ).order_by(TaskNode.sequence).all()
        
        # 为每个节点创建任务
        for node in task_nodes:
            self._create_task_for_node(instance, node, variables)
        
        # 更新实例状态
        pending_tasks = self.db.query(ProcessTask).filter(
            ProcessTask.instance_id == instance.id,
            ProcessTask.status == "pending"
        ).count()
        
        if pending_tasks == 0:
            instance.status = "completed"
            instance.completed_at = datetime.now()
        
        self.db.commit()
    
    def _create_task_for_node(self, instance: ProcessInstance, node: TaskNode, 
                             variables: Dict[str, Any]):
        """为节点创建任务"""
        # 查找处理人
        assignee = self._find_assignee(node, variables)
        
        if assignee:
            # 有处理人，创建待办任务
            task = ProcessTask(
                instance_id=instance.id,
                task_key=node.node_id,
                task_name=node.node_name,
                node_id=node.node_id,
                assignee_id=assignee.id,
                status="pending",
                variables=json.dumps(variables)
            )
            self.db.add(task)
        elif node.is_skip_if_empty:
            # 无处理人且设置为跳过，创建跳过任务
            task = ProcessTask(
                instance_id=instance.id,
                task_key=node.node_id,
                task_name=node.node_name,
                node_id=node.node_id,
                assignee_id=None,
                status="skipped",
                comment="无处理人，自动跳过",
                variables=json.dumps(variables)
            )
            self.db.add(task)
        else:
            # 无处理人但不跳过，创建待办任务（等待分配）
            task = ProcessTask(
                instance_id=instance.id,
                task_key=node.node_id,
                task_name=node.node_name,
                node_id=node.node_id,
                assignee_id=None,
                status="pending",
                variables=json.dumps(variables)
            )
            self.db.add(task)
    
    def _find_assignee(self, node: TaskNode, variables: Dict[str, Any]) -> Optional[User]:
        """查找任务处理人"""
        # 1. 优先从流程变量中获取
        if f"{node.node_id}_assignee" in variables:
            assignee_id = variables[f"{node.node_id}_assignee"]
            return self.db.query(User).get(assignee_id)
        
        # 2. 根据角色查找
        if node.role_id:
            users = self.db.query(User).filter(
                User.role_id == node.role_id,
                User.is_active == True
            ).all()
            if users:
                return users[0]  # 返回第一个用户
        
        # 3. 根据机构层级查找
        if node.org_level:
            # 这里可以根据业务逻辑实现机构层级查找
            pass
        
        return None
    
    def complete_task(self, task_id: int, user_id: int, 
                     variables: Dict[str, Any] = None, comment: str = ""):
        """完成任务"""
        from app.models.user import Organization
        
        task = self.db.query(ProcessTask).get(task_id)
        if not task:
            raise ValueError("任务不存在")
        
        if task.assignee_id != user_id:
            raise ValueError("无权处理此任务")
        
        if task.status != "pending":
            raise ValueError("任务已完成")
        
        # 获取当前提交人
        user = self.db.query(User).get(user_id)
        if not user or not user.org_id:
            raise ValueError("用户或用户机构不存在")
        
        # 计算机构层级：获取父机构的父机构的级别
        user_org = self.db.query(Organization).get(user.org_id)
        islvl2 = None
        
        if user_org and user_org.parent_id:
            parent_org = self.db.query(Organization).get(user_org.parent_id)
            if parent_org and parent_org.parent_id:
                grandparent_org = self.db.query(Organization).get(parent_org.parent_id)
                if grandparent_org:
                    # 祖父机构的级别
                    if grandparent_org.level == 1:  # 总行
                        islvl2 = '1'
                    elif grandparent_org.level == 2:  # 分行
                        islvl2 = '2'
        
        # 准备流程变量
        if variables is None:
            variables = {}
        
        # 设置 islvl2 变量
        if islvl2 is not None:
            variables['islvl2'] = islvl2
        
        # 更新任务状态
        task.status = "completed"
        task.completed_at = datetime.now()
        task.comment = comment
        if variables:
            task.variables = json.dumps(variables)
        
        # 检查实例是否完成
        instance = task.instance
        pending_tasks = self.db.query(ProcessTask).filter(
            ProcessTask.instance_id == instance.id,
            ProcessTask.status == "pending"
        ).count()
        
        if pending_tasks == 0:
            instance.status = "completed"
            instance.completed_at = datetime.now()
        
        self.db.commit()
    
    def get_user_tasks(self, user_id: int) -> List[ProcessTask]:
        """获取用户待办任务"""
        return self.db.query(ProcessTask).filter(
            ProcessTask.assignee_id == user_id,
            ProcessTask.status == "pending"
        ).order_by(ProcessTask.started_at.desc()).all()
    
    def get_instance_tasks(self, instance_id: int) -> List[ProcessTask]:
        """获取实例的所有任务"""
        return self.db.query(ProcessTask).filter(
            ProcessTask.instance_id == instance_id
        ).order_by(ProcessTask.started_at).all()
    
    def get_instance_history(self, instance_id: int) -> List[Dict]:
        """获取实例历史记录"""
        tasks = self.get_instance_tasks(instance_id)
        history = []
        for task in tasks:
            assignee = self.db.query(User).get(task.assignee_id) if task.assignee_id else None
            history.append({
                "task_id": task.id,
                "task_name": task.task_name,
                "node_id": task.node_id,
                "status": task.status,
                "assignee_name": assignee.real_name if assignee else None,
                "assignee_id": task.assignee_id,
                "started_at": task.started_at,
                "completed_at": task.completed_at,
                "comment": task.comment
            })
        return history