"""流程管理API路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.workflow import ProcessDefinition, ProcessInstance, ProcessTask, TaskNode
from app.services.bpmn_engine import BpmnWorkflowEngine
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/workflow", tags=["流程管理"])


# ==================== Schemas ====================

class ProcessDefinitionCreate(BaseModel):
    key: str
    name: str
    description: Optional[str] = ""
    bpmn_xml: str


class ProcessDefinitionUpdate(BaseModel):
    bpmn_xml: str


class ProcessDefinitionResponse(BaseModel):
    id: int
    key: str
    name: str
    version: int
    description: str
    bpmn_xml: str
    status: str
    deployed_at: Optional[datetime]
    created_at: datetime
    instance_count: int = 0


class TaskNodeCreate(BaseModel):
    node_id: str
    node_name: str
    node_type: str
    role_id: Optional[int] = None
    org_level: Optional[str] = None
    is_skip_if_empty: bool = True
    sequence: int = 0


class ProcessInstanceCreate(BaseModel):
    definition_id: int
    business_key: str
    variables: Optional[Dict[str, Any]] = None


class TaskCompleteRequest(BaseModel):
    variables: Optional[Dict[str, Any]] = None
    comment: Optional[str] = ""


# ==================== 流程定义管理 ====================

@router.post("/definitions", response_model=ProcessDefinitionResponse)
async def create_definition(
    data: ProcessDefinitionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建流程定义"""
    engine = BpmnWorkflowEngine(db)
    
    # 查询相同名称的最新版本
    latest_definition = db.query(ProcessDefinition).filter(
        ProcessDefinition.name == data.name
    ).order_by(ProcessDefinition.version.desc()).first()
    
    # 计算新版本号
    new_version = (latest_definition.version + 1) if latest_definition else 1
    
    # 生成唯一的 key：名称_版本号
    unique_key = f"{data.key}_{new_version}"
    
    definition = engine.deploy_process(
        key=unique_key,
        name=data.name,
        bpmn_xml=data.bpmn_xml,
        deployed_by=current_user.id,
        description=data.description
    )
    
    # 更新版本号
    definition.version = new_version
    db.commit()
    
    return definition


@router.get("/definitions", response_model=List[ProcessDefinitionResponse])
async def get_definitions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取流程定义列表"""
    query = db.query(ProcessDefinition)
    
    if status:
        query = query.filter(ProcessDefinition.status == status)
    
    total = query.count()
    offset = (page - 1) * page_size
    definitions = query.order_by(
        ProcessDefinition.created_at.desc()
    ).offset(offset).limit(page_size).all()
    
    return definitions


@router.get("/definitions/{definition_id}", response_model=ProcessDefinitionResponse)
async def get_definition(
    definition_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取流程定义详情"""
    definition = db.query(ProcessDefinition).get(definition_id)
    if not definition:
        raise HTTPException(status_code=404, detail="流程流程定义不存在")
    
    # 统计关联的流程实例数量
    instance_count = db.query(ProcessInstance).filter(
        ProcessInstance.definition_id == definition_id
    ).count()
    
    # 将实例数量添加到返回结果
    result = {
        "id": definition.id,
        "key": definition.key,
        "name": definition.name,
        "version": definition.version,
        "description": definition.description,
        "bpmn_xml": definition.bpmn_xml,
        "status": definition.status,
        "deployed_at": definition.deployed_at,
        "created_at": definition.created_at,
        "instance_count": instance_count
    }
    
    return ProcessDefinitionResponse(**result)


@router.put("/definitions/{definition_id}")
async def update_definition(
    definition_id: int,
    data: ProcessDefinitionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新流程定义"""
    definition = db.query(ProcessDefinition).get(definition_id)
    if not definition:
        raise HTTPException(status_code=404, detail="流程定义不存在")
    
    # 检查是否有关联的流程实例
    instance_count = db.query(ProcessInstance).filter(
        ProcessInstance.definition_id == definition_id
    ).count()
    
    if instance_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"该流程版本已绑定 {instance_count} 个流程实例，无法修改。请先删除相关流程实例。"
        )
    
    # 更新 BPMN XML
    definition.bpmn_xml = data.bpmn_xml
    definition.updated_at = datetime.now()
    db.commit()
    
    return definition


@router.delete("/definitions/{definition_id}")
async def delete_definition(
    definition_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除流程定义"""
    import traceback
    
    definition = db.query(ProcessDefinition).get(definition_id)
    if not definition:
        raise HTTPException(status_code=404, detail="流程定义不存在")
    
    try:
        # 检查流程定义状态，启用状态不允许删除
        if definition.status == 'active':
            raise HTTPException(
                status_code=400, 
                detail="流程实例未完结不允许删除"
            )
        
        # 检查是否有绑定的流程实例
        instance_count = db.query(ProcessInstance).filter(
            ProcessInstance.definition_id == definition_id
        ).count()
        
        if instance_count > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"该流程版本已绑定 {instance_count} 个流程实例，无法删除。请先删除相关流程实例。"
            )
        
        # 删除关联的任务节点
        db.query(TaskNode).filter(TaskNode.definition_id == definition_id).delete()
        
        # 删除流程定义
        db.delete(definition)
        db.commit()
        
        return {"message": "流程定义删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        error_detail = f"删除失败: {str(e)}\n{traceback.format_exc()}"
        print(f"Database error: {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)


@router.post("/definitions/{definition_id}/activate")
async def activate_definition(
    definition_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """启用流程定义"""
    definition = db.query(ProcessDefinition).get(definition_id)
    if not definition:
        raise HTTPException(status_code=404, detail="流程定义不存在")
    
    if definition.status == "active":
        raise HTTPException(status_code=400, detail="流程定义已经是启用状态")
    
    # 停用同一名称下的其他启用版本
    db.query(ProcessDefinition).filter(
        ProcessDefinition.name == definition.name,
        ProcessDefinition.status == "active",
        ProcessDefinition.id != definition_id
    ).update({"status": "archived"})
    
    # 启用当前版本
    definition.status = "active"
    definition.updated_at = datetime.now()
    db.commit()
    
    return {"message": "流程定义启用成功"}


@router.post("/definitions/{definition_id}/deactivate")
async def deactivate_definition(
    definition_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """停用流程定义"""
    definition = db.query(ProcessDefinition).get(definition_id)
    if not definition:
        raise HTTPException(status_code=404, detail="流程定义不存在")
    
    if definition.status != "active":
        raise HTTPException(status_code=400, detail="只有启用状态的流程定义才能停用")
    
    # 检查是否有运行中的实例（审批中、退回、撤回、分配）
    running_instance_count = db.query(ProcessInstance).filter(
        ProcessInstance.definition_id == definition_id,
        ProcessInstance.status.in_(["running", "returned", "withdrawn", "assigned"])
    ).count()
    
    if running_instance_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"该流程版本有 {running_instance_count} 个运行中的流程实例（审批中、退回、撤回、分配），无法停用。请等待所有实例完成。"
        )
    
    # 停用流程定义
    definition.status = "archived"
    definition.updated_at = datetime.now()
    db.commit()
    
    return {"message": "流程定义停用成功"}


@router.post("/definitions/{definition_id}/nodes")
async def create_task_nodes(
    definition_id: int,
    nodes: List[TaskNodeCreate],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建任务节点"""
    definition = db.query(ProcessDefinition).get(definition_id)
    if not definition:
        raise HTTPException(status_code=404, detail="流程定义不存在")
    
    # 删除旧节点
    db.query(TaskNode).filter(TaskNode.definition_id == definition_id).delete()
    
    # 创建新节点
    for node_data in nodes:
        node = TaskNode(
            definition_id=definition_id,
            node_id=node_data.node_id,
            node_name=node_data.node_name,
            node_type=node_data.node_type,
            role_id=node_data.role_id,
            org_level=node_data.org_level,
            is_skip_if_empty=1 if node_data.is_skip_if_empty else 0,
            sequence=node_data.sequence
        )
        db.add(node)
    
    db.commit()
    return {"message": "任务节点创建成功"}


@router.get("/definitions/{definition_id}/nodes")
async def get_task_nodes(
    definition_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取任务节点列表"""
    nodes = db.query(TaskNode).filter(
        TaskNode.definition_id == definition_id
    ).order_by(TaskNode.sequence).all()
    return nodes


# ==================== 流程实例管理 ====================

@router.post("/instances")
async def start_instance(
    data: ProcessInstanceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """启动流程实例"""
    engine = BpmnWorkflowEngine(db)
    instance = engine.start_instance(
        definition_id=data.definition_id,
        business_key=data.business_key,
        started_by=current_user.id,
        variables=data.variables
    )
    return {"instance_id": instance.id, "instance_key": instance.instance_key}


@router.get("/instances")
async def get_instances(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取流程实例列表"""
    from sqlalchemy.orm import joinedload
    
    query = db.query(ProcessInstance).options(
        joinedload(ProcessInstance.definition)
    )
    
    if status:
        query = query.filter(ProcessInstance.status == status)
    
    total = query.count()
    offset = (page - 1) * page_size
    instances = query.order_by(
        ProcessInstance.started_at.desc()
    ).offset(offset).limit(page_size).all()
    
    # 转换为字典，包含流程定义信息
    result_data = []
    for instance in instances:
        result_data.append({
            "id": instance.id,
            "instance_key": instance.instance_key,
            "definition_id": instance.definition_id,
            "business_key": instance.business_key,
            "status": instance.status,
            "current_node": instance.current_node,
            "started_by": instance.started_by,
            "started_at": instance.started_at.isoformat() if instance.started_at else None,
            "completed_at": instance.completed_at.isoformat() if instance.completed_at else None,
            "definition": {
                "id": instance.definition.id,
                "key": instance.definition.key,
                "name": instance.definition.name,
                "version": instance.definition.version
            } if instance.definition else None
        })
    
    return {
        "data": result_data,
        "total": total
    }


@router.delete("/instances/{instance_id}")
async def delete_instance(
    instance_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除流程实例"""
    import traceback
    
    instance = db.query(ProcessInstance).get(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="流程实例不存在")
    
    try:
        # 删除实例的任务
        db.query(ProcessTask).filter(ProcessTask.instance_id == instance_id).delete()
        
        # 删除实例
        db.delete(instance)
        db.commit()
        
        return {"message": "流程实例删除成功"}
    except Exception as e:
        db.rollback()
        error_detail = f"删除失败: {str(e)}\n{traceback.format_exc()}"
        print(f"Database error: {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)


@router.get("/instances/{instance_id}")
async def get_instance(
    instance_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取流程实例详情"""
    instance = db.query(ProcessInstance).get(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="流程实例不存在")
    
    engine = BpmnWorkflowEngine(db)
    tasks = engine.get_instance_history(instance_id)
    
    return {
        "instance": instance,
        "tasks": tasks
    }


# ==================== 任务管理 ====================

@router.get("/tasks/my-tasks")
async def get_my_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取我的待办任务"""
    engine = BpmnWorkflowEngine(db)
    tasks = engine.get_user_tasks(current_user.id)
    return tasks


@router.post("/tasks/{task_id}/complete")
async def complete_task(
    task_id: int,
    data: TaskCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """完成任务"""
    engine = BpmnWorkflowEngine(db)
    engine.complete_task(
        task_id=task_id,
        user_id=current_user.id,
        variables=data.variables,
        comment=data.comment
    )
    return {"message": "任务已完成"}


@router.get("/instances/{instance_id}/tasks")
async def get_instance_tasks(
    instance_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取实例任务列表"""
    engine = BpmnWorkflowEngine(db)
    tasks = engine.get_instance_history(instance_id)
    return tasks