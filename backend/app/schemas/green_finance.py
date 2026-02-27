from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class GreenIdentificationBase(BaseModel):
    loan_code: str
    customer_name: str
    customer_id: Optional[str] = None
    business_type: Optional[str] = None
    loan_account: Optional[str] = None
    loan_amount: Optional[Decimal] = None
    disbursement_date: Optional[datetime] = None
    maturity_date: Optional[datetime] = None
    interest_rate: Optional[Decimal] = None
    green_percentage: Optional[Decimal] = None
    green_loan_balance: Optional[Decimal] = None
    project_category_large: Optional[str] = None
    project_category_medium: Optional[str] = None
    project_category_small: Optional[str] = None
    esg_risk_level: Optional[str] = None
    esg_performance_level: Optional[str] = None


class GreenIdentificationCreate(GreenIdentificationBase):
    pass


class GreenIdentificationUpdate(BaseModel):
    customer_name: Optional[str] = None
    business_type: Optional[str] = None
    loan_amount: Optional[Decimal] = None
    project_category_large: Optional[str] = None
    project_category_medium: Optional[str] = None
    project_category_small: Optional[str] = None
    green_project_category: Optional[str] = None
    esg_risk_level: Optional[str] = None
    esg_performance_level: Optional[str] = None


class GreenIdentification(GreenIdentificationBase):
    id: int
    status: str
    initiator_id: Optional[int] = None
    current_handler_id: Optional[int] = None
    org_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TaskQuery(BaseModel):
    status: Optional[str] = None
    customer_name: Optional[str] = None
    business_type: Optional[str] = None
    loan_account: Optional[str] = None
    initiator: Optional[str] = None
    project_category: Optional[str] = None
    disbursement_date_start: Optional[datetime] = None
    disbursement_date_end: Optional[datetime] = None
    completed_date_start: Optional[datetime] = None
    completed_date_end: Optional[datetime] = None
    deadline_start: Optional[datetime] = None
    deadline_end: Optional[datetime] = None


class TaskListItem(BaseModel):
    id: int
    identification_id: str  # 带前缀的ID，格式：ID-{identification_id}
    task_id: int
    loan_code: str
    customer_name: str
    business_type: str
    loan_account: str
    loan_amount: Decimal
    disbursement_date: datetime
    project_category_small: str
    formatted_category: Optional[str] = None
    deadline: Optional[datetime] = None
    status: str
    initiator_name: str
    completed_at: Optional[datetime] = None
    org_name: Optional[str] = None


class TaskListResponse(BaseModel):
    items: List[TaskListItem]
    total: int
    page: int
    page_size: int


class WorkflowTaskBase(BaseModel):
    task_key: str
    task_name: str
    node_id: str
    assignee_id: int


class WorkflowTaskCreate(BaseModel):
    approval_result: str
    comment: Optional[str] = None
    reason: Optional[str] = None
    project_category_large: Optional[str] = None
    project_category_medium: Optional[str] = None
    project_category_small: Optional[str] = None


class WorkflowTask(WorkflowTaskBase):
    id: int
    status: str
    approval_result: Optional[str] = None
    comment: Optional[str] = None
    reason: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    assignee_name: Optional[str] = None
    assignee_username: Optional[str] = None  # 添加办理人员账号
    position_name: Optional[str] = None
    project_category_large: Optional[str] = None
    project_category_medium: Optional[str] = None
    project_category_small: Optional[str] = None
    formatted_category: Optional[str] = None
    
    class Config:
        from_attributes = True


class WorkflowInstance(BaseModel):
    id: int
    case_id: str
    process_key: str
    process_definition_id: Optional[int] = None
    business_key: str
    current_node: str
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class GreenLoanIndicator(BaseModel):
    id: int
    stat_date: datetime
    org_id: int
    green_loan_balance: Decimal
    green_loan_ratio: Decimal
    customer_count: int
    growth_rate: Decimal
    green_investment: Decimal
    green_leasing: Decimal
    green_wealth_management: Decimal
    green_underwriting: Decimal
    created_at: datetime
    
    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    green_loan_balance: Decimal
    customer_count: int
    green_loan_ratio: Optional[Decimal] = None
    growth_rate: Decimal
    green_investment: Decimal
    green_leasing: Decimal
    green_wealth_management: Decimal
    green_underwriting: Decimal


class TodoItem(BaseModel):
    category: str
    count: int


class DashboardData(BaseModel):
    stats: DashboardStats
    todos: List[TodoItem]