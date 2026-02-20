from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class WorkflowVariable(Base):
    """流程变量模型"""
    __tablename__ = "workflow_variables"
    
    id = Column(Integer, primary_key=True, index=True)
    definition_id = Column(Integer, ForeignKey("process_definitions.id"), nullable=False, comment="流程定义ID")
    variable_name = Column(String(100), nullable=False, comment="变量名称")
    variable_key = Column(String(100), nullable=False, comment="变量键")
    variable_type = Column(String(50), nullable=False, comment="变量类型：string/number/boolean/array/object")
    default_value = Column(Text, comment="默认值")
    description = Column(Text, comment="描述")
    required = Column(Boolean, default=False, comment="是否必填")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    definition = relationship("ProcessDefinition", back_populates="variables")