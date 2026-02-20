from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.auth import get_current_user
from app.schemas.workflow_variable import WorkflowVariableCreate, WorkflowVariableUpdate, WorkflowVariableResponse

router = APIRouter(prefix="/api/workflow-variables", tags=["流程变量"])


@router.get("", response_model=List[WorkflowVariableResponse])
async def get_variables(
    definition_id: Optional[int] = Query(None, description="流程定义ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取流程变量列表"""
    from app.models.workflow_variable import WorkflowVariable
    from app.models.workflow import ProcessDefinition
    
    query = db.query(WorkflowVariable)
    
    if definition_id:
        query = query.filter(WorkflowVariable.definition_id == definition_id)
    
    variables = query.order_by(WorkflowVariable.created_at.desc()).all()
    
    # 构建响应数据
    result = []
    for var in variables:
        var_dict = {
            "id": var.id,
            "definition_id": var.definition_id,
            "variable_name": var.variable_name,
            "variable_key": var.variable_key,
            "variable_type": var.variable_type,
            "default_value": var.default_value,
            "description": var.description,
            "required": var.required,
            "definition_name": var.definition.name if var.definition else None,
            "created_at": var.created_at,
            "updated_at": var.updated_at
        }
        result.append(var_dict)
    
    return result


@router.post("", response_model=WorkflowVariableResponse)
async def create_variable(
    data: WorkflowVariableCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建流程变量"""
    from app.models.workflow_variable import WorkflowVariable
    from app.models.workflow import ProcessDefinition
    
    # 检查流程定义是否存在
    definition = db.query(ProcessDefinition).get(data.definition_id)
    if not definition:
        raise HTTPException(status_code=404, detail="流程定义不存在")
    
    # 检查变量键是否已存在
    existing = db.query(WorkflowVariable).filter(
        WorkflowVariable.definition_id == data.definition_id,
        WorkflowVariable.variable_key == data.variable_key
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该流程下已存在相同变量键")
    
    variable = WorkflowVariable(**data.model_dump())
    db.add(variable)
    db.commit()
    db.refresh(variable)
    
    return variable


@router.get("/{variable_id}", response_model=WorkflowVariableResponse)
async def get_variable(
    variable_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取流程变量详情"""
    from app.models.workflow_variable import WorkflowVariable
    
    variable = db.query(WorkflowVariable).get(variable_id)
    if not variable:
        raise HTTPException(status_code=404, detail="流程变量不存在")
    
    return variable


@router.put("/{variable_id}", response_model=WorkflowVariableResponse)
async def update_variable(
    variable_id: int,
    data: WorkflowVariableUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新流程变量"""
    from app.models.workflow_variable import WorkflowVariable
    
    variable = db.query(WorkflowVariable).get(variable_id)
    if not variable:
        raise HTTPException(status_code=404, detail="流程变量不存在")
    
    # 检查变量键是否与其他变量冲突
    if data.variable_key and data.variable_key != variable.variable_key:
        existing = db.query(WorkflowVariable).filter(
            WorkflowVariable.definition_id == variable.definition_id,
            WorkflowVariable.variable_key == data.variable_key,
            WorkflowVariable.id != variable_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="该流程下已存在相同变量键")
    
    # 更新字段
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(variable, field, value)
    
    db.commit()
    db.refresh(variable)
    
    return variable


@router.delete("/{variable_id}")
async def delete_variable(
    variable_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除流程变量"""
    from app.models.workflow_variable import WorkflowVariable
    
    variable = db.query(WorkflowVariable).get(variable_id)
    if not variable:
        raise HTTPException(status_code=404, detail="流程变量不存在")
    
    db.delete(variable)
    db.commit()
    
    return {"message": "删除成功"}