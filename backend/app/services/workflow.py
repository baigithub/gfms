from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, text

from app.models.green_finance import (
    GreenIdentification,
    WorkflowInstance,
    WorkflowTask,
    TaskStatus
)
from app.models.workflow import ProcessDefinition
from app.services.bpmn_parser import BPMNParser
from app.models.user import User, Role, Organization
from app.schemas.green_finance import (
    GreenIdentificationCreate,
    GreenIdentificationUpdate,
    WorkflowTaskCreate,
    TaskQuery,
    TaskListItem
)


class WorkflowEngine:
    """
    绿色认定工作流引擎（支持 BPMN 流程定义）
    实现以下流程:
    1. 客户经理发起认定 -> 2. 二级分行绿色金融管理岗审核 -> 3. 一级分行绿色金融管理岗审批 -> 4. 绿色金融复核岗复核 -> 5. 结束
    """
    
    # 流程定义缓存
    _process_definition_cache = None
    _process_definition_cache_time = None
    
    @staticmethod
    def calculate_business_deadline(start_date: datetime, business_days: int = 3) -> datetime:
        """计算工作日截止时间
        
        Args:
            start_date: 开始时间（包含）
            business_days: 工作日数量（默认3个工作日）
            
        Returns:
            截止时间（次日凌晨0点）
        """
        from datetime import timedelta
        
        current_date = start_date
        days_counted = 0
        
        while days_counted < business_days:
            current_date += timedelta(days=1)
            # 跳过周末（周六=5，周日=6）
            if current_date.weekday() < 5:  # 0-4 是周一到周五
                days_counted += 1
        
        # 返回次日凌晨0点
        return datetime(current_date.year, current_date.month, current_date.day, 0, 0, 0)
    
    @classmethod
    def start_process(cls, db: Session, identification: GreenIdentification, initiator: User) -> WorkflowInstance:
        """启动工作流实例"""
        # 获取启用状态的流程定义（根据流程名称）
        process_definition = db.query(ProcessDefinition).filter(
            ProcessDefinition.name == "绿色认定",
            ProcessDefinition.status == "active"
        ).first()
        
        if not process_definition:
            raise ValueError("未找到启用状态的流程定义，请先启用一个流程版本")
        
        # 解析 BPMN XML
        try:
            parsed_process = BPMNParser.parse(process_definition.bpmn_xml)
        except Exception as e:
            raise ValueError(f"解析流程定义失败: {str(e)}")
        
        # 找到起始节点
        start_nodes = [n for n in parsed_process['nodes'] if n.type == 'start']
        if not start_nodes:
            raise ValueError("流程定义中未找到开始节点")
        
        start_node = start_nodes[0]
        
        # 从流程图中找到起始节点的后续节点
        flow_graph = parsed_process['flow_graph']
        next_node_ids = flow_graph.get(start_node.id, [])
        
        if not next_node_ids:
            raise ValueError("流程定义中起始节点没有后续节点")
        
        # 获取第一个用户任务节点
        first_task_node = None
        for node_id in next_node_ids:
            node = next((n for n in parsed_process['nodes'] if n.id == node_id), None)
            if node and node.type == 'task':
                first_task_node = node
                break
        
        if not first_task_node:
            raise ValueError("流程定义中未找到用户任务节点")
        
        # 将节点名称映射到 task_key
        task_key = cls._map_node_name_to_task_key(first_task_node.name)
        
        # 构建节点映射（从 task_key 到节点信息）
        nodes_map = {n.id: n for n in parsed_process['nodes']}
        
        # 创建工作流实例
        case_id = f"CASE_{datetime.now().strftime('%Y%m%d%H%M%S')}_{identification.id}"
        
        workflow = WorkflowInstance(
            case_id=case_id,
            process_key="green_identification_process",
            process_definition_id=process_definition.id,
            business_key=identification.loan_code,
            current_node=task_key,
            status="进行中",
            identification_id=identification.id
        )
        db.add(workflow)
        db.flush()
        
        # 创建第一个任务，设置截止时间为三个工作日后的凌晨0点
        deadline = cls.calculate_business_deadline(datetime.now(), 3)
        
        task = WorkflowTask(
            task_key=task_key,
            task_name=first_task_node.name,
            node_id=first_task_node.id,
            assignee_id=initiator.id,
            status="待处理",
            workflow_instance_id=workflow.id,
            identification_id=identification.id
        )
        # 更新认定和任务的截止时间
        identification.deadline = deadline
        task.started_at = datetime.now()
        db.add(task)
        db.commit()
        
        return workflow
    
    @classmethod
    def complete_task(cls, db: Session, task: WorkflowTask, approval_result: str, comment: Optional[str] = None, reason: Optional[str] = None) -> Optional[WorkflowTask]:
        """完成任务并流转到下一节点"""
        # 获取流程定义
        workflow_instance = task.workflow_instance
        process_definition = None
        parsed_process = None
        
        # 如果workflow_instance没有绑定流程定义，动态获取启用状态的流程定义
        if hasattr(workflow_instance, 'process_definition_id') and not workflow_instance.process_definition_id:
            # 动态获取启用状态的流程定义
            process_definition = db.query(ProcessDefinition).filter(
                ProcessDefinition.name == "绿色认定",
                ProcessDefinition.status == "active"
            ).first()
            
            if process_definition:
                # 绑定流程定义到工作流实例
                workflow_instance.process_definition_id = process_definition.id
                db.commit()
                print(f"已绑定流程版本v{process_definition.version}到工作流实例 {workflow_instance.id}")
        # 检查是否有process_definition_id字段（兼容旧系统）
        elif hasattr(workflow_instance, 'process_definition_id') and workflow_instance.process_definition_id:
            process_definition = db.query(ProcessDefinition).filter(
                ProcessDefinition.id == workflow_instance.process_definition_id
            ).first()
        
        if process_definition:
            try:
                parsed_process = BPMNParser.parse(process_definition.bpmn_xml)
            except Exception as e:
                print(f"警告: 解析流程定义失败，使用硬编码节点: {str(e)}")
                parsed_process = None
        
        # 获取提交人信息
        from app.models.user import User
        submitter = db.query(User).get(task.assignee_id)
        
        # 计算islvl2变量
        islvl2 = None
        if submitter and submitter.org_id:
            from app.models.user import Organization
            user_org = db.query(Organization).get(submitter.org_id)
            
            if user_org and user_org.parent_id:
                parent_org = db.query(Organization).get(user_org.parent_id)
                
                if parent_org and parent_org.parent_id:
                    grandparent_org = db.query(Organization).get(parent_org.parent_id)
                    
                    if grandparent_org:
                        if grandparent_org.level == 1:
                            islvl2 = '1'
                        elif grandparent_org.level == 2:
                            islvl2 = '2'
        
        # 设置islvl2变量
        if islvl2 is not None:
            # 将变量存储在当前任务的variables字段中（JSON格式）
            import json
            existing_vars = {}
            if task.variables:
                try:
                    existing_vars = json.loads(task.variables)
                except:
                    existing_vars = {}
            
            existing_vars['islvl2'] = islvl2
            task.variables = json.dumps(existing_vars)
        
        task.approval_result = approval_result
        task.comment = comment
        task.reason = reason
        task.completed_at = datetime.now()
        task.status = "已完成"
        
        # 保存当前节点的绿色分类信息
        identification = task.workflow_instance.identification
        if identification:
            task.project_category_large = identification.project_category_large
            task.project_category_medium = identification.project_category_medium
            task.project_category_small = identification.project_category_small
            # 获取格式化的分类名称
            formatted_category = get_formatted_category(db, identification)
            task.formatted_category = formatted_category
        
        workflow = task.workflow_instance
        
        # 获取下一节点
        current_node = workflow.current_node
        
        # 必须有解析的流程定义，否则无法流转
        if not parsed_process:
            raise ValueError("流程定义未解析，无法完成任务")
        
        # 从流程图决定下一个节点
        next_node = None
        
        # 在流程图中找到当前节点的后续节点
        nodes_map = {n.id: n for n in parsed_process['nodes']}
        flow_graph = parsed_process['flow_graph']
        
        # 找到当前节点对应的 BPMN 节点
        current_bpmn_node = None
        for node in parsed_process['nodes']:
            if node.type == 'task' and cls._map_node_name_to_task_key(node.name) == current_node:
                current_bpmn_node = node
                break
        
        if current_bpmn_node:
            # 从流程图获取后续节点
            next_node_ids = flow_graph.get(current_bpmn_node.id, [])
            
            if approval_result == "同意":
                # 特殊处理 manager_identification 节点
                if current_node == "manager_identification":
                    # 直接使用第一个后续节点
                    if next_node_ids:
                        first_next_node = nodes_map.get(next_node_ids[0])
                        if first_next_node and first_next_node.type == 'task':
                            next_node = cls._map_node_name_to_task_key(first_next_node.name)
                        elif first_next_node and first_next_node.type == 'end':
                            next_node = "end"
                        else:
                            next_node = None
                    else:
                        next_node = None
                else:
                    # 其他节点，走第一个后续节点
                    if next_node_ids:
                        first_next_node = nodes_map.get(next_node_ids[0])
                        if first_next_node:
                            if first_next_node.type == 'task':
                                next_node = cls._map_node_name_to_task_key(first_next_node.name)
                            elif first_next_node.type == 'end':
                                next_node = "end"
                            else:
                                # 如果是网关，需要进一步处理
                                next_node = None
                        else:
                            next_node = None
                    else:
                        next_node = None
            elif approval_result in ["不同意", "退回"]:
                # 退回逻辑：查找条件表达式或默认退回路径
                # 这里简化处理，如果序列流中有条件表达式为 "return" 或类似的，则走该路径
                # 否则走最后一个路径
                if next_node_ids:
                    # 默认走最后一个节点（通常表示退回）
                    last_next_node = nodes_map.get(next_node_ids[-1])
                    if last_next_node and last_next_node.type == 'task':
                        next_node = cls._map_node_name_to_task_key(last_next_node.name)
                    else:
                        next_node = None
                else:
                    next_node = None
        
        if not next_node:
            raise ValueError(f"无法找到当前节点 {current_node} 的后续节点")
        
        if next_node == "end":
            workflow.status = "已办结"
            workflow.ended_at = datetime.now()
            workflow.current_node = "end"
            
            # 更新认定状态
            identification = workflow.identification
            identification.status = TaskStatus.ARCHIVED.value if approval_result == "同意" else TaskStatus.REJECTED.value
            identification.completed_at = datetime.now()
            db.commit()
            return None
        
        # 流转到下一节点
        workflow.current_node = next_node
        
        if next_node == "end":
            workflow.status = "已办结"
            workflow.ended_at = datetime.now()
            
            identification = workflow.identification
            identification.status = TaskStatus.ARCHIVED.value
            identification.completed_at = datetime.now()
            db.commit()
            return None
        
        # 检查当前workflow实例是否已经有待处理任务，防止重复创建
        existing_pending_task = db.query(WorkflowTask).filter(
            WorkflowTask.workflow_instance_id == workflow.id,
            WorkflowTask.status == "待处理",
            WorkflowTask.id != task.id  # 排除当前正在完成的任务
        ).first()
        
        if existing_pending_task:
            raise ValueError(f"当前流程已有待处理任务（{existing_pending_task.task_name}），无法创建新任务")
        
        # 必须有解析的流程定义，否则无法创建任务
        if not parsed_process:
            raise ValueError("流程定义未解析，无法创建任务")
        
        # 从流程定义中获取节点信息（不使用硬编码）
        task_name = next_node  # 默认值
        node_id = f"UserTask_{next_node}"
        
        # 通过节点名称查找节点
        for node in parsed_process['nodes']:
            if node.type == 'task' and cls._map_node_name_to_task_key(node.name) == next_node:
                task_name = node.name
                node_id = node.id
                break
        
        # 根据当前认定的机构，查找下一节点的处理人
        assignee = cls._find_assignee(db, next_node, task.identification_id)
        
        if not assignee:
            raise ValueError(f"无法找到{task_name}的处理人")
        
        # 计算新的截止时间（从当前时间开始三个工作日后的凌晨0点）
        new_deadline = cls.calculate_business_deadline(datetime.now(), 3)
        
        next_task = WorkflowTask(
            task_key=next_node,
            task_name=task_name,
            node_id=node_id,
            assignee_id=assignee.id,
            status="待处理",
            workflow_instance_id=workflow.id,
            identification_id=task.identification_id,
            # 继承认定任务的绿色分类信息
            project_category_large=identification.project_category_large,
            project_category_medium=identification.project_category_medium,
            project_category_small=identification.project_category_small,
            formatted_category=get_formatted_category(db, identification)
        )
        db.add(next_task)
        
        # 更新认定状态、当前处理人和截止时间
        identification = workflow.identification
        identification.current_handler_id = assignee.id
        identification.status = TaskStatus.PROCESSING.value
        identification.deadline = new_deadline
        db.commit()
        
        return next_task
    
    @classmethod
    def assign_task(cls, db: Session, task: WorkflowTask, assignee: User):
        """分配任务给用户"""
        task.assignee_id = assignee.id
        
        # 更新认定的当前处理人
        identification = db.query(GreenIdentification).filter(GreenIdentification.id == task.identification_id).first()
        if identification:
            identification.current_handler_id = assignee.id
        
        db.commit()
    
    @classmethod
    def _map_node_name_to_task_key(cls, node_name: str) -> str:
        """将 BPMN 节点名称映射到 task_key
        
        根据节点名称中的关键词映射到对应的 task_key：
        - "客户经理" -> "manager_identification"
        - "二级分行" -> "branch_review"
        - "一级分行" -> "first_approval"
        - "复核" -> "final_review"
        """
        if "客户经理" in node_name:
            return "manager_identification"
        elif "二级分行" in node_name:
            return "branch_review"
        elif "一级分行" in node_name and "复核" in node_name:
            return "final_review"
        elif "一级分行" in node_name:
            return "first_approval"
        elif "复核" in node_name:
            return "final_review"
        else:
            # 默认返回节点名称的拼音首字母或简化版本
            return node_name.lower().replace(" ", "_")
    
    @classmethod
    def _find_assignee(cls, db: Session, next_node: str, identification_id: int) -> Optional[User]:
        """根据机构层级查找合适的处理人"""
        from app.models.user import Role, Organization
        
        # 获取当前认定信息
        identification = db.query(GreenIdentification).filter(GreenIdentification.id == identification_id).first()
        if not identification:
            return None
        
        # 获取发起人的机构
        initiator_org = db.query(Organization).filter(Organization.id == identification.org_id).first()
        if not initiator_org:
            return None
        
        if next_node == "manager_identification":
            # 客户经理认定：返回认定的发起人
            initiator = db.query(User).filter(User.id == identification.initiator_id).first()
            return initiator
            
        if next_node == "branch_review":
            # 分行审核：使用BPMN引擎查找处理人
            role = db.query(Role).filter(Role.name == "绿色金融管理岗").first()
            if not role:
                return None
            
            # 获取工作流实例的流程定义
            workflow_instance = db.query(WorkflowInstance).filter(
                WorkflowInstance.identification_id == identification_id
            ).first()
            
            parsed_process = None
            if workflow_instance and workflow_instance.process_definition_id:
                process_definition = db.query(ProcessDefinition).filter(
                    ProcessDefinition.id == workflow_instance.process_definition_id
                ).first()
                if process_definition:
                    try:
                        from app.services.bpmn_engine import BPMNParser
                        parsed_process = BPMNParser.parse(process_definition.bpmn_xml)
                    except Exception as e:
                        print(f"警告: 解析流程定义失败: {str(e)}")
            
            # 根据BPMN流程定义中的orgLevels属性查找处理人
            # 如果有解析的流程定义，使用其中的节点信息
            if parsed_process:
                # 查找当前节点信息
                current_node_info = None
                for node in parsed_process['nodes']:
                    if node.type == 'task' and cls._map_node_name_to_task_key(node.name) == next_node:
                        current_node_info = node
                        break
                
                if current_node_info and current_node_info.properties:
                    org_levels = current_node_info.properties.get('orgLevels', [])
                    candidate_groups = current_node_info.properties.get('candidateGroups', [])
                    
                    # 根据机构层级和候选组查找处理人
                    if org_levels and candidate_groups:
                        # 解析orgLevels
                        import json
                        try:
                            levels = json.loads(org_levels) if isinstance(org_levels, str) else org_levels
                        except:
                            levels = []
                        
                        # 查找符合条件的机构
                        org_query = db.query(Organization).filter(Organization.level.in_(levels))
                        
                        # 根据发起人机构进行过滤：查找发起人机构的父机构
                        if initiator_org.parent_id:
                            # 查找发起人机构的父级机构（无论发起人机构是level=2还是level=3）
                            org_query = org_query.filter(Organization.id == initiator_org.parent_id)
                        
                        valid_orgs = org_query.all()
                        
                        if valid_orgs:
                            # 查找这些机构中符合候选组的用户
                            role_name_map = {
                                "绿色金融管理岗": "绿色金融管理岗",
                                "绿色金融复核岗": "绿色金融复核岗"
                            }
                            
                            role_name = role_name_map.get(candidate_groups[0] if candidate_groups else "", candidate_groups[0] if candidate_groups else "")
                            if role_name:
                                role = db.query(Role).filter(Role.name == role_name).first()
                                if role:
                                    assignee = db.query(User).filter(
                                        User.org_id.in_([org.id for org in valid_orgs]),
                                        User.role_id == role.id,
                                        User.is_active == True
                                    ).first()
                                    if assignee:
                                        return assignee
            
            # 如果BPMN引擎找不到，使用原有逻辑作为后备
            assignee = None
            if initiator_org.level == 3 and initiator_org.parent_id:
                parent_org = db.query(Organization).filter(Organization.id == initiator_org.parent_id).first()
                if parent_org and parent_org.level == 2:
                    assignee = db.query(User).filter(
                        User.org_id == parent_org.id,
                        User.role_id == role.id,
                        User.is_active == True
                    ).first()
            elif initiator_org.level == 2:
                assignee = db.query(User).filter(
                    User.org_id == initiator_org.id,
                    User.role_id == role.id,
                    User.is_active == True
                ).first()
            
            if not assignee and initiator_org.parent_id:
                parent_org = db.query(Organization).filter(Organization.id == initiator_org.parent_id).first()
                if parent_org:
                    assignee = db.query(User).filter(
                        User.org_id == parent_org.id,
                        User.role_id == role.id,
                        User.is_active == True
                    ).first()
            
            return assignee
            
        elif next_node == "first_approval":
            # 一级分行绿色金融管理岗：查找一级分行的绿色金融管理岗
            role = db.query(Role).filter(Role.name == "绿色金融管理岗").first()
            if not role:
                return None
            
            # 获取发起人的机构
            initiator_org = db.query(Organization).filter(Organization.id == identification.org_id).first()
            if not initiator_org:
                return None
            
            # 一级分行绿色金融管理岗：查找parent_id指向level=1的level=2机构（一级分行）的绿色金融管理岗
            assignee = db.query(User).filter(
                User.role_id == role.id,
                User.is_active == True
            ).join(Organization, User.org_id == Organization.id).filter(
                Organization.level == 2,
                Organization.parent_id.in_(
                    db.query(Organization.id).filter(Organization.level == 1)
                )
            ).first()
            
            return assignee
            
        elif next_node == "final_review":
            # 绿色金融复核岗：查找绿色金融复核岗
            role = db.query(Role).filter(Role.name == "绿色金融复核岗").first()
            if not role:
                return None
            
            # 查找绿色金融复核岗
            assignee = db.query(User).filter(
                User.role_id == role.id,
                User.is_active == True
            ).first()
            
            return assignee
        
        return None
    
    @classmethod
    def withdraw_task(cls, db: Session, task: WorkflowTask, user: User):
        """撤回任务
        
        撤回规则：
        1. 只能撤回已完成的任务
        2. 检查下一个节点的任务状态，如果是"待处理"（未做暂存或提交），则可以撤回
        3. 如果下一个节点任务已经是"已完成"，则不能撤回
        4. 一级分行绿色金融复核岗（final_review）完成后不能撤回
        
        撤回时保留完整的历史记录：
        - 原本的"已完成"任务记录保持不变
        - 下一节点的待处理任务标记为"已撤回"
        - 创建新的"待处理"任务给当前用户
        """
        if task.status != "已完成":
            raise ValueError("只能撤回已完成的任务")
        
        if task.assignee_id != user.id:
            raise ValueError("只能撤回自己经办的任务")
        
        current_node = task.task_key
        
        # 复核节点完成后不能撤回
        # 使用current_node检查，避免依赖parsed_process
        if "final_review" in current_node:
            raise ValueError("一级分行复核完成后不能撤回")
        
        # 获取流程定义
        workflow = task.workflow_instance
        process_definition = None
        parsed_process = None
        
        if workflow.process_definition_id:
            process_definition = db.query(ProcessDefinition).filter(
                ProcessDefinition.id == workflow.process_definition_id
            ).first()
        
        if process_definition and process_definition.bpmn_xml:
            try:
                parsed_process = BPMNParser.parse(process_definition.bpmn_xml)
            except Exception as e:
                print(f"解析流程定义失败: {str(e)}")
        
        # 从流程定义中获取当前节点的名称
        current_node_name = current_node
        if parsed_process:
            for node in parsed_process['nodes']:
                if node.type == 'task' and cls._map_node_name_to_task_key(node.name) == current_node:
                    current_node_name = node.name
                    break
        
        # 从流程定义中获取下一个节点的信息
        next_node = None
        next_node_name = None
        
        if parsed_process:
            # 在流程图中找到当前节点的后续节点
            nodes_map = {n.id: n for n in parsed_process['nodes']}
            flow_graph = parsed_process['flow_graph']
            
            # 找到当前节点对应的 BPMN 节点
            current_bpmn_node = None
            for node in parsed_process['nodes']:
                if node.type == 'task' and cls._map_node_name_to_task_key(node.name) == current_node:
                    current_bpmn_node = node
                    break
            
            if current_bpmn_node:
                # 从流程图获取后续节点
                next_node_ids = flow_graph.get(current_bpmn_node.id, [])
                
                # 获取第一个用户任务节点
                if next_node_ids:
                    first_next_node = nodes_map.get(next_node_ids[0])
                    if first_next_node and first_next_node.type == 'task':
                        next_node = cls._map_node_name_to_task_key(first_next_node.name)
                        next_node_name = first_next_node.name
        
        if next_node:
            # 检查下一节点是否有已完成任务（已经提交审批）
            next_completed_task = db.query(WorkflowTask).filter(
                WorkflowTask.workflow_instance_id == workflow.id,
                WorkflowTask.task_key == next_node,
                WorkflowTask.status == "已完成"
            ).first()
            
            if next_completed_task:
                raise ValueError(f"无法撤回：下一个节点（{next_node_name if next_node_name else next_node}）已经提交审批，无法撤回")
            
            # 将下一节点的待处理任务标记为"已撤回"，而不是删除
            next_pending_task = db.query(WorkflowTask).filter(
                WorkflowTask.workflow_instance_id == workflow.id,
                WorkflowTask.task_key == next_node,
                WorkflowTask.status == "待处理"
            ).first()
            
            if next_pending_task:
                next_pending_task.status = "已撤回"
                next_pending_task.completed_at = datetime.now()
                next_pending_task.approval_result = "撤回"
                next_pending_task.reason = "撤回操作"
        
        # 设置任务名称和节点ID
        task_name = current_node_name
        node_id = f"UserTask_{current_node}"
        if parsed_process:
            for node in parsed_process['nodes']:
                if node.type == 'task' and cls._map_node_name_to_task_key(node.name) == current_node:
                    task_name = node.name
                    node_id = node.id
                    break
        
        # 创建新的待处理任务给当前用户，而不是修改当前任务的状态
        # 这样可以保留原本的"已完成"任务记录
        new_task = WorkflowTask(
            task_key=current_node,
            task_name=task_name,
            node_id=node_id,
            assignee_id=user.id,
            status="待处理",
            approval_result=None,
            reason=None,
            started_at=datetime.now(),
            completed_at=None,
            workflow_instance_id=workflow.id,
            identification_id=task.identification_id,
            variables=task.variables,
            # 复制绿色分类信息
            project_category_large=task.project_category_large,
            project_category_medium=task.project_category_medium,
            project_category_small=task.project_category_small,
            formatted_category=task.formatted_category
        )
        
        # 将原本的已完成任务标记为已撤回，这样就不会出现在已办列表中
        task.status = "已撤回"
        task.approval_result = "撤回"
        task.reason = "用户撤回操作"
        task.completed_at = datetime.now()
        
        db.add(new_task)
        
        # 更新流程实例的当前节点
        workflow.current_node = current_node
        workflow.status = "running"
        
        # 更新认定信息的处理人
        identification = task.identification
        identification.current_handler_id = user.id
        identification.status = TaskStatus.PROCESSING.value
        
        db.commit()
    
    @classmethod
    def return_task(cls, db: Session, task: WorkflowTask, return_to_node: str, comment: Optional[str] = None, user: User = None):
        """退回任务
        
        退回规则：
        1. 客户经理（manager_identification）：不能退回
        2. 二级分行绿色金融管理岗（branch_review）：可以退回到客户经理
        3. 一级分行绿色金融管理岗（first_approval）：可以退回给客户经理或二级分行绿色金融管理岗
        4. 一级分行绿色金融复核岗（final_review）：可以退回到客户经理、二级分行绿色金融管理岗或一级分行绿色金融管理岗
        """
        if task.status != "待处理":
            raise ValueError("只能退回待处理的任务")
        
        current_node = task.task_key
        
        # 客户经理不能退回
        if current_node == "manager_identification":
            raise ValueError("客户经理不能退回")
        
        # 获取流程定义
        workflow = task.workflow_instance
        process_definition = None
        parsed_process = None
        
        if workflow.process_definition_id:
            process_definition = db.query(ProcessDefinition).filter(
                ProcessDefinition.id == workflow.process_definition_id
            ).first()
        
        if process_definition and process_definition.bpmn_xml:
            try:
                parsed_process = BPMNParser.parse(process_definition.bpmn_xml)
            except Exception as e:
                print(f"解析流程定义失败: {str(e)}")
        
        # 验证退回目标节点是否合法
        valid_return_nodes = cls._get_valid_return_nodes(current_node, parsed_process)
        print(f"DEBUG: current_node={current_node}, return_to_node={return_to_node}, valid_return_nodes={valid_return_nodes}")
        if return_to_node not in valid_return_nodes:
            raise ValueError(f"当前节点不能退回到 {return_to_node}")
        
        # 标记当前任务为已退回
        task.status = "已退回"
        task.completed_at = datetime.now()
        task.approval_result = "退回"
        task.comment = comment
        
        # 从流程定义中获取退回目标节点的名称
        return_to_node_name = return_to_node
        if parsed_process:
            for node in parsed_process['nodes']:
                if node.type == 'task' and cls._map_node_name_to_task_key(node.name) == return_to_node:
                    return_to_node_name = node.name
                    break
        
        task.reason = f"退回到 {return_to_node_name}"
        
        # 更新流程实例的当前节点
        workflow = task.workflow_instance
        workflow.current_node = return_to_node
        
        # 保存当前任务的分类信息
        identification = workflow.identification
        if identification:
            task.project_category_large = identification.project_category_large
            task.project_category_medium = identification.project_category_medium
            task.project_category_small = identification.project_category_small
            # 获取格式化的分类名称
            formatted_category = get_formatted_category(db, identification)
            task.formatted_category = formatted_category
        
        # 获取退回目标节点的处理人
        assignee = cls._find_assignee(db, return_to_node, identification.id)
        
        if not assignee:
            raise ValueError(f"无法找到{return_to_node_name}的处理人")
        
        # 从流程定义中获取退回目标节点的node_id
        return_to_node_id = f"UserTask_{return_to_node}"
        if parsed_process:
            for node in parsed_process['nodes']:
                if node.type == 'task' and cls._map_node_name_to_task_key(node.name) == return_to_node:
                    return_to_node_id = node.id
                    break
        
        # 创建退回目标节点的新任务
        new_task = WorkflowTask(
            task_key=return_to_node,
            task_name=return_to_node_name,
            node_id=return_to_node_id,
            assignee_id=assignee.id,
            status="待处理",
            workflow_instance_id=workflow.id,
            identification_id=task.identification_id
        )
        # 将原本的已完成任务标记为已撤回，这样就不会出现在已办列表中
        task.status = "已撤回"
        task.approval_result = "撤回"
        task.reason = "用户撤回操作"
        task.completed_at = datetime.now()
        
        db.add(new_task)
        
        identification.current_handler_id = assignee.id
        identification.status = TaskStatus.PROCESSING.value
        db.commit()
    
    @classmethod
    def _get_valid_return_nodes(cls, current_node: str, parsed_process: dict = None) -> List[str]:
        """获取当前节点可以退回的节点列表
        
        从流程定义中动态获取可退回的节点。
        默认规则：当前节点可以退回到所有前置的任务节点（除了客户经理节点）
        """
        valid_nodes = []
        
        if parsed_process:
            # 从流程图中获取所有前置节点
            nodes_map = {n.id: n for n in parsed_process['nodes']}
            flow_graph = parsed_process['flow_graph']
            
            # 找到当前节点对应的 BPMN 节点
            current_bpmn_node = None
            for node in parsed_process['nodes']:
                if node.type == 'task' and cls._map_node_name_to_task_key(node.name) == current_node:
                    current_bpmn_node = node
                    break
            
            if current_bpmn_node:
                # 递归查找所有前置用户任务节点
                visited = set()  # 防止循环
                queue = [current_bpmn_node.id]
                
                print(f"DEBUG: 开始递归查找前置节点，起始节点: {current_bpmn_node.id}")
                
                while queue:
                    node_id = queue.pop(0)
                    if node_id in visited:
                        print(f"DEBUG: 节点 {node_id} 已访问，跳过")
                        continue
                    visited.add(node_id)
                    
                    # 查找所有流向当前节点的节点
                    for source_id, next_node_ids in flow_graph.items():
                        if node_id in next_node_ids:
                            predecessor = nodes_map.get(source_id)
                            if predecessor:
                                print(f"DEBUG: 找到前置节点 {source_id} (type={predecessor.type}, name={predecessor.name})")
                                if predecessor.type == 'task':
                                    task_key = cls._map_node_name_to_task_key(predecessor.name)
                                    # 允许退回到所有前置任务节点（包括客户经理节点）
                                    if task_key not in valid_nodes:
                                        valid_nodes.append(task_key)
                                        print(f"DEBUG: 添加到可退回节点列表: {predecessor.name} -> {task_key}")
                                elif predecessor.type == 'gateway':
                                    print(f"DEBUG: 遇到网关，继续向前查找")
                                
                                # 无论什么类型，都继续向前查找（除了开始节点）
                                if predecessor.type != 'start' and predecessor.id not in visited:
                                    queue.append(predecessor.id)
                                    print(f"DEBUG: 继续向前查找: {predecessor.id}")
                                elif predecessor.type == 'start':
                                    print(f"DEBUG: 到达开始节点，停止查找")
                
                print(f"DEBUG: 最终找到的可退回节点: {valid_nodes}")
        else:
            # 后备逻辑：硬编码的退回规则
            return_nodes_map = {
                "manager_identification": [],  # 客户经理不能退回
                "branch_review": ["manager_identification"],
                "first_approval": ["manager_identification", "branch_review"],
                "final_review": ["manager_identification", "branch_review", "first_approval"]
            }
            return return_nodes_map.get(current_node, [])
        
        return valid_nodes


def get_user_tasks(db: Session, user: User, status: str) -> List[TaskListItem]:
    """获取用户的任务列表"""
    query = db.query(WorkflowTask, GreenIdentification, User).join(
        GreenIdentification, WorkflowTask.identification_id == GreenIdentification.id
    ).join(
        User, WorkflowTask.assignee_id == User.id
    ).filter(
        WorkflowTask.assignee_id == user.id
    )
    
    # 根据状态过滤任务
    if status == "待处理":
        query = query.filter(WorkflowTask.status == "待处理")
    elif status == "已完成":
        # 已办任务包括已完成和已退回的任务
        query = query.filter(WorkflowTask.status.in_(["已完成", "已退回"]))
    
    # 对于已办任务，排除流程已完结的任务
    if status == "已完成":
        query = query.filter(GreenIdentification.status != "办结")
    
    query = query.order_by(WorkflowTask.started_at.desc())  # 按任务创建时间倒序排列
    
    tasks = query.all()
    
    # 对于已办任务，对identification_id进行去重，只保留最新的任务记录
    if status == "已完成":
        seen_identification_ids = set()
        unique_tasks = []
        for task in tasks:
            identification_id = task[0].identification_id
            if identification_id not in seen_identification_ids:
                seen_identification_ids.add(identification_id)
                unique_tasks.append(task)
        tasks = unique_tasks
    
    items = []
    for task, identification, assignee in tasks:
        # 获取该流程中所有有分类信息的任务，按时间倒序排列，取最新的
        tasks_with_category = db.query(WorkflowTask).filter(
            WorkflowTask.identification_id == identification.id,
            WorkflowTask.formatted_category.isnot(None)
        ).order_by(WorkflowTask.started_at.desc()).all()
        
        # 使用最新节点的绿色分类信息
        if tasks_with_category and tasks_with_category[0].formatted_category:
            formatted_category = tasks_with_category[0].formatted_category
        else:
            formatted_category = get_formatted_category(db, identification)
        
        items.append(TaskListItem(
            id=identification.id,
            identification_id=f"ID-{identification.id}",  # 添加identification_id字段
            task_id=task.id,  # 添加task_id字段
            loan_code=identification.loan_code,
            customer_name=identification.customer_name,
            business_type=identification.business_type or "",
            loan_account=identification.loan_account or "",
            loan_amount=identification.loan_amount or 0,
            disbursement_date=identification.disbursement_date or datetime.now(),
            project_category_small=identification.project_category_small or "",
            formatted_category=formatted_category,
            deadline=identification.deadline,
            status=identification.status,
            initiator_name=initiator_name(db, identification.initiator_id),
            completed_at=identification.completed_at,
            org_name=None
        ))
    
    return items


def initiator_name(db: Session, initiator_id: Optional[int]) -> str:
    if not initiator_id:
        return ""
    user = db.query(User).filter(User.id == initiator_id).first()
    return user.real_name if user else ""


def query_tasks(db: Session, query_params: TaskQuery, status: str, user: Optional[User] = None, org_id: Optional[int] = None, restrict_to_assigned: bool = False) -> tuple[List[TaskListItem], int]:
    """查询任务列表"""
    query = db.query(GreenIdentification, User).outerjoin(
        User, GreenIdentification.initiator_id == User.id
    ).filter(GreenIdentification.status == status)
    
    # 如果限制只显示用户经办的已办结任务，添加子查询过滤
    if restrict_to_assigned and user:
        # 获取用户在工作流中有任务记录的所有identification_id
        assigned_identification_ids = db.query(WorkflowTask.identification_id).filter(
            WorkflowTask.assignee_id == user.id
        ).distinct().all()
        assigned_identification_ids = [id[0] for id in assigned_identification_ids]
        
        if assigned_identification_ids:
            query = query.filter(GreenIdentification.id.in_(assigned_identification_ids))
        else:
            # 如果用户没有任何任务记录，返回空结果
            return [], 0
    
    if query_params.customer_name:
        query = query.filter(GreenIdentification.customer_name.like(f"%{query_params.customer_name}%"))
    
    if query_params.business_type:
        query = query.filter(GreenIdentification.business_type == query_params.business_type)
    
    if query_params.loan_account:
        query = query.filter(GreenIdentification.loan_account.like(f"%{query_params.loan_account}%"))
    
    if query_params.project_category:
        query = query.filter(
            or_(
                GreenIdentification.project_category_large.like(f"%{query_params.project_category}%"),
                GreenIdentification.project_category_medium.like(f"%{query_params.project_category}%"),
                GreenIdentification.project_category_small.like(f"%{query_params.project_category}%")
            )
        )
    
    if query_params.disbursement_date_start:
        query = query.filter(GreenIdentification.disbursement_date >= query_params.disbursement_date_start)
    
    if query_params.disbursement_date_end:
        query = query.filter(GreenIdentification.disbursement_date <= query_params.disbursement_date_end)
    
    if status == TaskStatus.ARCHIVED.value and query_params.completed_date_start:
        query = query.filter(GreenIdentification.completed_at >= query_params.completed_date_start)
    
    if status == TaskStatus.ARCHIVED.value and query_params.completed_date_end:
        query = query.filter(GreenIdentification.completed_at <= query_params.completed_date_end)
    
    if query_params.deadline_start:
        query = query.filter(GreenIdentification.deadline >= query_params.deadline_start)
    
    if query_params.deadline_end:
        query = query.filter(GreenIdentification.deadline <= query_params.deadline_end)
    
    if org_id:
        query = query.filter(GreenIdentification.org_id == org_id)
    
    # 添加排序逻辑：按办结时间倒序，如果没有办结时间则按创建时间倒序
    if status == TaskStatus.ARCHIVED.value:
        # MySQL不支持nulls_last()，使用CASE WHEN来模拟
        from sqlalchemy import case
        query = query.order_by(
            case(
                (GreenIdentification.completed_at == None, 1),
                (GreenIdentification.completed_at != None, 0),
                else_=2
            ).asc(),
            GreenIdentification.completed_at.desc(),
            GreenIdentification.created_at.desc()
        )
    else:
        query = query.order_by(GreenIdentification.created_at.desc())
    
    total = query.count()
    
    items = []
    for identification, initiator in query.all():
        # 获取该认定记录的最新已完成任务的绿色分类信息
        latest_task = db.query(WorkflowTask).filter(
            WorkflowTask.identification_id == identification.id,
            WorkflowTask.status == "已完成",
            WorkflowTask.formatted_category.isnot(None),
            WorkflowTask.formatted_category != ""
        ).order_by(WorkflowTask.completed_at.desc()).first()
        
        # 如果最新的任务有分类信息，使用最新的；否则使用当前的 identification 信息
        if latest_task and latest_task.formatted_category:
            formatted_category = latest_task.formatted_category
        else:
            formatted_category = get_formatted_category(db, identification)
        
        items.append(TaskListItem(
            id=identification.id,
            identification_id=f"ID-{identification.id}",  # 添加带前缀的identification_id
            task_id=latest_task.id if latest_task else identification.id,  # 添加task_id字段
            loan_code=identification.loan_code,
            customer_name=identification.customer_name,
            business_type=identification.business_type or "",
            loan_account=identification.loan_account or "",
            loan_amount=identification.loan_amount or 0,
            disbursement_date=identification.disbursement_date or datetime.now(),
            project_category_small=identification.project_category_small or "",
            formatted_category=formatted_category,
            deadline=identification.deadline,
            status=identification.status,
            initiator_name=initiator.real_name if initiator else "",
            completed_at=identification.completed_at,
            org_name=None
        ))
    
    return items, total


def get_formatted_category(db: Session, identification: GreenIdentification) -> Optional[str]:
    """获取格式化的带编号的分类名称"""
    large = identification.project_category_large
    medium = identification.project_category_medium
    small = identification.project_category_small
    
    if not large and not medium and not small:
        return None
    
    # 尝试匹配完整的三级分类
    result = db.execute(text("""
        SELECT formatted_name
        FROM green_project_categories
        WHERE large_name = :large AND medium_name = :medium AND small_name = :small
        LIMIT 1
    """), {"large": large, "medium": medium, "small": small}).fetchone()
    
    if result:
        return result[0]
    
    # 如果没有找到三级分类，尝试匹配二级分类
    result = db.execute(text("""
        SELECT formatted_name
        FROM green_project_categories
        WHERE large_name = :large AND medium_name = :medium AND small_code IS NULL
        LIMIT 1
    """), {"large": large, "medium": medium}).fetchone()
    
    if result:
        return result[0]
    
    # 如果还是没有，手动拼接带编号的格式
    # 需要查找编号
    large_code = None
    medium_code = None
    small_code = None
    
    if large:
        result = db.execute(text("""
            SELECT large_code
            FROM green_project_categories
            WHERE large_name = :large
            ORDER BY large_code DESC
            LIMIT 1
        """), {"large": large}).fetchone()
        if result:
            large_code = result[0]
    
    if medium:
        # 如果已经知道 large_code，在查询中添加过滤条件
        if large_code:
            result = db.execute(text("""
                SELECT medium_code, large_code
                FROM green_project_categories
                WHERE large_name = :large AND medium_name = :medium AND large_code = :large_code
                LIMIT 1
            """), {"large": large, "medium": medium, "large_code": large_code}).fetchone()
        else:
            result = db.execute(text("""
                SELECT medium_code, large_code
                FROM green_project_categories
                WHERE large_name = :large AND medium_name = :medium
                ORDER BY large_code DESC, medium_code DESC
                LIMIT 1
            """), {"large": large, "medium": medium}).fetchone()
        
        if result:
            medium_code = result[0]
            # 如果之前没有large_code，使用查询到的large_code
            if not large_code:
                large_code = result[1]
    
    if small:
        # 如果已经知道 large_code 和 medium_code，在查询中添加过滤条件
        if large_code and medium_code:
            result = db.execute(text("""
                SELECT small_code, large_code, medium_code
                FROM green_project_categories
                WHERE large_name = :large AND medium_name = :medium AND small_name = :small
                  AND large_code = :large_code AND medium_code = :medium_code
                LIMIT 1
            """), {"large": large, "medium": medium, "small": small, "large_code": large_code, "medium_code": medium_code}).fetchone()
        else:
            result = db.execute(text("""
                SELECT small_code, large_code, medium_code
                FROM green_project_categories
                WHERE large_name = :large AND medium_name = :medium AND small_name = :small
                ORDER BY large_code DESC, medium_code DESC, small_code DESC
                LIMIT 1
            """), {"large": large, "medium": medium, "small": small}).fetchone()
        
        if result:
            small_code = result[0]
            # 验证并更新large_code和medium_code以确保一致性
            if result[1]:
                large_code = result[1]
            if result[2]:
                medium_code = result[2]
    
    # 手动拼接带编号的格式
    parts = []
    if large_code and large:
        parts.append(f"{large_code} {large}")
    elif large:
        parts.append(large)
    
    if medium_code and medium:
        parts.append(f"{medium_code} {medium}")
    elif medium:
        parts.append(medium)
    
    if small_code and small:
        parts.append(f"{small_code} {small}")
    elif small:
        parts.append(small)
    
    return '/'.join(parts) if parts else None