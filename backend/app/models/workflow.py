from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ProcessDefinition(Base):
    """流程定义表"""
    __tablename__ = "process_definitions"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False, comment="流程键")
    name = Column(String(200), nullable=False, comment="流程名称")
    version = Column(Integer, default=1, comment="版本号")
    description = Column(Text, comment="流程描述")
    bpmn_xml = Column(Text, nullable=False, comment="BPMN XML定义")
    status = Column(SQLEnum("active", "archived", name="process_status"), default="archived", comment="状态")
    deployed_by = Column(Integer, ForeignKey("users.id"), comment="部署人")
    deployed_at = Column(DateTime(timezone=True), comment="部署时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    deployer = relationship("User", foreign_keys=[deployed_by])
    instances = relationship("ProcessInstance", back_populates="definition")
    variables = relationship("WorkflowVariable", back_populates="definition")


class ProcessInstance(Base):
    """流程实例表"""
    __tablename__ = "process_instances"
    
    id = Column(Integer, primary_key=True, index=True)
    instance_key = Column(String(100), unique=True, index=True, comment="实例键")
    definition_id = Column(Integer, ForeignKey("process_definitions.id"), nullable=False)
    business_key = Column(String(100), comment="业务键")
    status = Column(SQLEnum("running", "completed", "terminated", "returned", "withdrawn", "assigned", name="instance_status"), default="running", comment="状态")
    current_node = Column(String(100), comment="当前节点")
    started_by = Column(Integer, ForeignKey("users.id"), comment="发起人")
    started_at = Column(DateTime(timezone=True), server_default=func.now(), comment="开始时间")
    completed_at = Column(DateTime(timezone=True), comment="完成时间")
    variables = Column(Text, comment="流程变量JSON")
    
    definition = relationship("ProcessDefinition", back_populates="instances")
    starter = relationship("User", foreign_keys=[started_by])
    tasks = relationship("ProcessTask", back_populates="instance")


class ProcessTask(Base):
    """流程任务表"""
    __tablename__ = "process_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    instance_id = Column(Integer, ForeignKey("process_instances.id"), nullable=False)
    task_key = Column(String(100), nullable=False, comment="任务键")
    task_name = Column(String(200), nullable=False, comment="任务名称")
    node_id = Column(String(100), comment="节点ID")
    assignee_id = Column(Integer, ForeignKey("users.id"), comment="处理人")
    status = Column(SQLEnum("pending", "completed", "skipped", "cancelled", name="task_status"), default="pending", comment="状态")
    priority = Column(Integer, default=50, comment="优先级")
    due_date = Column(DateTime(timezone=True), comment="到期时间")
    started_at = Column(DateTime(timezone=True), server_default=func.now(), comment="开始时间")
    completed_at = Column(DateTime(timezone=True), comment="完成时间")
    variables = Column(Text, comment="任务变量JSON")
    comment = Column(Text, comment="处理意见")
    
    instance = relationship("ProcessInstance", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assignee_id])


class TaskNode(Base):
    """任务节点定义表"""
    __tablename__ = "task_nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    definition_id = Column(Integer, ForeignKey("process_definitions.id"))
    node_id = Column(String(100), nullable=False, comment="节点ID")
    node_name = Column(String(200), nullable=False, comment="节点名称")
    node_type = Column(String(50), comment="节点类型")
    role_id = Column(Integer, ForeignKey("roles.id"), comment="关联角色")
    org_level = Column(String(50), comment="机构层级")
    is_skip_if_empty = Column(Integer, default=0, comment="无人员时是否跳过")
    sequence = Column(Integer, default=0, comment="顺序")
    
    role = relationship("Role")