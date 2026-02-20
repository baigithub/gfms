from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class WorkflowVariableBase(BaseModel):
    definition_id: int = Field(..., description="流程定义ID")
    variable_name: str = Field(..., max_length=100, description="变量名称")
    variable_key: str = Field(..., max_length=100, description="变量键")
    variable_type: str = Field(..., max_length=50, description="变量类型")
    default_value: Optional[str] = Field(None, description="默认值")
    description: Optional[str] = Field(None, description="描述")
    required: bool = Field(default=False, description="是否必填")


class WorkflowVariableCreate(WorkflowVariableBase):
    pass


class WorkflowVariableUpdate(BaseModel):
    variable_name: Optional[str] = Field(None, max_length=100)
    variable_key: Optional[str] = Field(None, max_length=100)
    variable_type: Optional[str] = Field(None, max_length=50)
    default_value: Optional[str] = None
    description: Optional[str] = None
    required: Optional[bool] = None


class WorkflowVariableResponse(WorkflowVariableBase):
    id: int
    definition_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True