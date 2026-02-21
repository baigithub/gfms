from sqlalchemy import Column, Integer, String, DateTime, Numeric, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class TaskStatus(str, enum.Enum):
    PENDING = "待办"
    PROCESSING = "办理中"
    DRAFT = "暂存"
    COMPLETED = "已办"
    ARCHIVED = "办结"
    REJECTED = "驳回"
    WITHDRAWN = "撤回"
    SYSTEM_TERMINATED = "系统终止"


class GreenIdentification(Base):
    __tablename__ = "green_identifications"
    
    id = Column(Integer, primary_key=True, index=True)
    loan_code = Column(String(50), unique=True, index=True, nullable=False)
    customer_name = Column(String(100), nullable=False)
    customer_id = Column(String(50))
    business_type = Column(String(50))  # 业务品种
    loan_account = Column(String(50))
    loan_amount = Column(Numeric(18, 2))
    disbursement_date = Column(DateTime)
    maturity_date = Column(DateTime)
    interest_rate = Column(Numeric(10, 4))
    green_percentage = Column(Numeric(5, 2))
    green_loan_balance = Column(Numeric(18, 2))
    
    # 绿色项目分类
    project_category_large = Column(String(50))  # 大类
    project_category_medium = Column(String(50))  # 中类
    project_category_small = Column(String(100))  # 小类
    green_project_category = Column(String(500))  # 绿色金融支持项目目录（合并字段）
    
    # 环境社会风险
    esg_risk_level = Column(String(20))
    esg_performance_level = Column(String(20))
    
    status = Column(String(20), default=TaskStatus.PENDING.value)
    initiator_id = Column(Integer, ForeignKey("users.id"))
    initiator = relationship("User", foreign_keys=[initiator_id])
    
    current_handler_id = Column(Integer, ForeignKey("users.id"))
    current_handler = relationship("User", foreign_keys=[current_handler_id])
    
    org_id = Column(Integer, ForeignKey("organizations.id"))
    organization = relationship("Organization")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    deadline = Column(DateTime(timezone=True))
    
    # Relationships
    workflow_instances = relationship("WorkflowInstance", back_populates="identification")


class WorkflowInstance(Base):
    __tablename__ = "workflow_instances"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String(50), unique=True, index=True)
    process_key = Column(String(50), default="green_identification_process")
    process_definition_id = Column(Integer, ForeignKey("process_definitions.id"), nullable=True, comment="流程定义ID，用于关联BPMN流程版本")
    business_key = Column(String(50))  # loan_code
    current_node = Column(String(50))
    status = Column(String(20))
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    
    # Relationships
    identification_id = Column(Integer, ForeignKey("green_identifications.id"))
    identification = relationship("GreenIdentification", foreign_keys=[identification_id])
    identification = relationship("GreenIdentification", back_populates="workflow_instances")
    tasks = relationship("WorkflowTask", back_populates="workflow_instance")
    process_definition = relationship("ProcessDefinition", foreign_keys=[process_definition_id])


class WorkflowTask(Base):
    __tablename__ = "workflow_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_key = Column(String(50))
    task_name = Column(String(100))
    node_id = Column(String(50))
    assignee_id = Column(Integer, ForeignKey("users.id"))
    assignee = relationship("User")
    status = Column(String(20))  # 待处理, 已完成, 已撤回
    approval_result = Column(String(20))  # 同意, 不同意, 撤回
    comment = Column(Text)
    reason = Column(Text)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    variables = Column(Text)  # 存储工作流变量的JSON字符串
    
    # 绿色分类信息（用于跟踪分类变动）
    project_category_large = Column(String(50))  # 大类
    project_category_medium = Column(String(50))  # 中类
    project_category_small = Column(String(100))  # 小类
    formatted_category = Column(String(500))  # 格式化的分类名称
    
    # Relationships
    workflow_instance_id = Column(Integer, ForeignKey("workflow_instances.id"))
    workflow_instance = relationship("WorkflowInstance", back_populates="tasks")
    
    identification_id = Column(Integer, ForeignKey("green_identifications.id"))
    identification = relationship("GreenIdentification", foreign_keys=[identification_id])


class TaskAttachment(Base):
    __tablename__ = "task_attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("workflow_tasks.id"), nullable=False)
    task = relationship("WorkflowTask", foreign_keys=[task_id])
    
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploader = relationship("User", foreign_keys=[uploader_id])
    
    original_filename = Column(String(255), nullable=False)  # 原始文件名
    stored_filename = Column(String(255), nullable=False)  # 存储的文件名（UUID）
    file_size = Column(Integer)  # 文件大小（字节）
    file_path = Column(String(500))  # 文件存储路径
    download_url = Column(String(500))  # 下载URL
    
    task_key = Column(String(50))  # 冗余字段，方便查询：任务key（如 manager_identification）
    task_name = Column(String(100))  # 冗余字段，方便查询：任务名称
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class GreenLoanIndicator(Base):
    __tablename__ = "green_loan_indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    stat_date = Column(DateTime, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    organization = relationship("Organization")
    
    # 核心指标
    green_loan_balance = Column(Numeric(18, 2))  # 绿色贷款余额
    green_loan_ratio = Column(Numeric(5, 2))  # 绿色贷款占比
    customer_count = Column(Integer)  # 客户数
    growth_rate = Column(Numeric(8, 2))  # 增速
    
    # 子类指标
    green_investment = Column(Numeric(18, 2))  # 绿色投资
    green_leasing = Column(Numeric(18, 2))  # 绿色租赁
    green_wealth_management = Column(Numeric(18, 2))  # 绿色理财
    green_underwriting = Column(Numeric(18, 2))  # 绿色承销
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())