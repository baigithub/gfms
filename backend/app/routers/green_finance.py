from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from app.database import get_db
from app.models.user import User
from app.models.green_finance import GreenIdentification, WorkflowTask, WorkflowInstance, GreenLoanIndicator, TaskStatus
from app.models.workflow import ProcessDefinition
from app.schemas.green_finance import (
    GreenIdentificationCreate,
    GreenIdentificationUpdate,
    GreenIdentification as GreenIdentificationSchema,
    TaskQuery,
    TaskListResponse,
    TaskListItem,
    WorkflowTaskCreate,
    WorkflowTask as WorkflowTaskSchema,
    WorkflowInstance as WorkflowInstanceSchema,
    DashboardData,
    DashboardStats,
    TodoItem
)
from app.services.auth import get_current_user
from app.services.workflow import WorkflowEngine, get_user_tasks, query_tasks, get_formatted_category

router = APIRouter(prefix="/api", tags=["绿色金融"])


def get_workflow_version(db: Session, process_definition_id: Optional[int]) -> int:
    """获取流程定义版本"""
    if not process_definition_id:
        return 1
    process_def = db.query(ProcessDefinition).filter(ProcessDefinition.id == process_definition_id).first()
    return process_def.version if process_def else 1


@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取工作台数据"""
    
    # 获取最新指标数据
    indicator = db.query(GreenLoanIndicator).order_by(
        GreenLoanIndicator.stat_date.desc()
    ).first()
    
    if indicator:
        stats = DashboardStats(
            green_loan_balance=indicator.green_loan_balance,
            customer_count=indicator.customer_count,
            green_loan_ratio=indicator.green_loan_ratio,
            growth_rate=indicator.growth_rate,
            green_investment=indicator.green_investment,
            green_leasing=indicator.green_leasing,
            green_wealth_management=indicator.green_wealth_management,
            green_underwriting=indicator.green_underwriting
        )
    else:
        stats = DashboardStats(
            green_loan_balance=Decimal("0"),
            customer_count=0,
            green_loan_ratio=Decimal("0"),
            growth_rate=Decimal("0"),
            green_investment=Decimal("0"),
            green_leasing=Decimal("0"),
            green_wealth_management=Decimal("0"),
            green_underwriting=Decimal("0")
        )
    
    # 获取待办统计
    todos = []
    
    # 统计各类型待办任务
    from app.models.green_finance import WorkflowTask as WorkflowTaskModel
    from app.models.workflow import ProcessDefinition
    from app.services.workflow import WorkflowEngine
    from app.services.bpmn_parser import BPMNParser
    
    pending_tasks = db.query(WorkflowTaskModel).filter(
        WorkflowTaskModel.status == "待处理",
        WorkflowTaskModel.assignee_id == current_user.id
    ).all()
    
    # 按任务类型统计
    task_counts = {}
    for task in pending_tasks:
        task_key = task.task_key
        task_counts[task_key] = task_counts.get(task_key, 0) + 1
    
    # 从流程定义中动态获取节点名称
    task_name_map = {}
    
    # 获取启用状态的流程定义
    process_definition = db.query(ProcessDefinition).filter(
        ProcessDefinition.name == "绿色认定",
        ProcessDefinition.status == "active"
    ).first()
    
    if process_definition and process_definition.bpmn_xml:
        try:
            parsed_process = BPMNParser.parse(process_definition.bpmn_xml)
            for node in parsed_process['nodes']:
                if node.type == 'task':
                    task_key = WorkflowEngine._map_node_name_to_task_key(node.name)
                    task_name_map[task_key] = node.name
        except Exception as e:
            print(f"解析流程定义失败: {str(e)}")
    
    for task_key, count in task_counts.items():
        todos.append(TodoItem(
            category=task_name_map.get(task_key, task_key),
            count=count
        ))
    
    return DashboardData(stats=stats, todos=todos)


@router.get("/tasks/pending", response_model=TaskListResponse)
async def get_pending_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取待办任务列表"""
    tasks = get_user_tasks(db, current_user, "待处理")
    
    total = len(tasks)
    start = (page - 1) * page_size
    end = start + page_size
    items = tasks[start:end]
    
    return TaskListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/tasks/completed", response_model=TaskListResponse)
async def get_completed_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取已办任务列表"""
    tasks = get_user_tasks(db, current_user, "已完成")
    
    total = len(tasks)
    start = (page - 1) * page_size
    end = start + page_size
    items = tasks[start:end]
    
    return TaskListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/tasks/archived", response_model=TaskListResponse)
async def get_archived_tasks(
    customer_name: Optional[str] = None,
    business_type: Optional[str] = None,
    loan_account: Optional[str] = None,
    initiator: Optional[str] = None,
    project_category: Optional[str] = None,
    disbursement_date_start: Optional[datetime] = None,
    disbursement_date_end: Optional[datetime] = None,
    completed_date_start: Optional[datetime] = None,
    completed_date_end: Optional[datetime] = None,
    deadline_start: Optional[datetime] = None,
    deadline_end: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取办结任务列表"""
    query = TaskQuery(
        customer_name=customer_name,
        business_type=business_type,
        loan_account=loan_account,
        initiator=initiator,
        project_category=project_category,
        disbursement_date_start=disbursement_date_start,
        disbursement_date_end=disbursement_date_end,
        completed_date_start=completed_date_start,
        completed_date_end=completed_date_end,
        deadline_start=deadline_start,
        deadline_end=deadline_end
    )
    
    # 权限控制：
    # 超级用户可以查看所有机构的办结任务
    # 其他用户只能查看自己经办的已办结任务（在工作流中有任务记录的任务）
    # 当restrict_to_assigned=True时，不使用org_id过滤，因为用户经办的任务可能属于不同机构
    items, total = query_tasks(db, query, "办结", current_user, org_id=None, restrict_to_assigned=True)
    
    start = (page - 1) * page_size
    end = start + page_size
    paginated_items = items[start:end]
    
    return TaskListResponse(
        items=paginated_items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/tasks/search")
async def search_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    customer_name: Optional[str] = None,
    business_type: Optional[str] = None,
    loan_account: Optional[str] = None,
    loan_date_start: Optional[str] = None,
    loan_date_end: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """综合查询任务"""
    from app.models.user import Organization
    
    # 构建查询
    query = db.query(GreenIdentification)
    
    # 权限控制：根据用户机构级别过滤数据
    if not current_user.is_superuser:
        user_org = db.query(Organization).filter(Organization.id == current_user.org_id).first()
        if user_org:
            # Level 1（总行）：可以查看所有数据
            # Level 2（分行）：可以查看本级及下属支行的数据
            # Level 3（支行）：只能查看本级的数据
            if user_org.level == 2:
                # 获取该分行及其所有下属机构的ID
                org_ids = [user_org.id]
                child_orgs = db.query(Organization).filter(Organization.parent_id == user_org.id).all()
                for child in child_orgs:
                    org_ids.append(child.id)
                    # 获取支行的下属机构（如果有）
                    grandchild_orgs = db.query(Organization).filter(Organization.parent_id == child.id).all()
                    for grandchild in grandchild_orgs:
                        org_ids.append(grandchild.id)
                query = query.filter(GreenIdentification.org_id.in_(org_ids))
            elif user_org.level == 3:
                # 支行只能查看本级的数据
                query = query.filter(GreenIdentification.org_id == current_user.org_id)
    
    # 添加查询条件
    if customer_name:
        query = query.filter(GreenIdentification.customer_name.like(f"%{customer_name}%"))
    if business_type:
        query = query.filter(GreenIdentification.business_type == business_type)
    if loan_account:
        query = query.filter(GreenIdentification.loan_account.like(f"%{loan_account}%"))
    if loan_date_start:
        query = query.filter(GreenIdentification.disbursement_date >= loan_date_start)
    if loan_date_end:
        query = query.filter(GreenIdentification.disbursement_date <= loan_date_end)
    if status:
        query = query.filter(GreenIdentification.status == status)
    
    # 获取总数
    total = query.count()
    
    # 分页
    offset = (page - 1) * page_size
    identifications = query.offset(offset).limit(page_size).all()
    
    # 转换为任务列表格式
    result = []
    for ident in identifications:
        # 获取发起人
        initiator = db.query(User).filter(User.id == ident.initiator_id).first()
        
        # 获取格式化的绿色金融支持项目目录
        from app.services.workflow import get_formatted_category
        formatted_category = get_formatted_category(db, ident)
        
        item = {
            "task_id": ident.id,
            "task_key": "绿色认定",
            "customer_name": ident.customer_name,
            "business_type": ident.business_type,
            "loan_account": ident.loan_account,
            "loan_amount": str(ident.loan_amount) if ident.loan_amount else "0",
            "loan_date": str(ident.disbursement_date) if ident.disbursement_date else "",
            "green_project_category": formatted_category or ident.project_category_medium or "",
            "status": ident.status,
            "assignee_name": initiator.real_name if initiator else "",
            "created_at": str(ident.created_at) if ident.created_at else "",
            "completed_at": str(ident.completed_at) if ident.completed_at else "",
            "workflow_history": []
        }
        
        # 获取工作流历史
        # 按时间排序工作流历史
        history_tasks = db.query(WorkflowTask).filter(
            WorkflowTask.identification_id == ident.id
        ).order_by(WorkflowTask.started_at).all()
        
        history_list = []
        for history_task in history_tasks:
            history_assignee = db.query(User).filter(User.id == history_task.assignee_id).first()
            # 获取该任务的分类信息
            formatted_category = None
            # 优先使用formatted_category字段（带编号格式）
            if history_task.formatted_category:
                formatted_category = history_task.formatted_category
            # 如果没有formatted_category，才使用分类字段构建（不带编号）
            elif history_task.project_category_large:
                parts = []
                if history_task.project_category_large:
                    parts.append(history_task.project_category_large)
                if history_task.project_category_medium:
                    parts.append(history_task.project_category_medium)
                if history_task.project_category_small:
                    parts.append(history_task.project_category_small)
                formatted_category = ' / '.join(parts)
                # 如果任务没有分类信息，且任务是待处理状态，使用认定（identification）的分类信息
                if not formatted_category and history_task.status == "待处理":
                    # 待处理任务使用认定（identification）的分类信息
                    if ident.project_category_large:
                        parts = []
                        if ident.project_category_large:
                            parts.append(ident.project_category_large)
                        if ident.project_category_medium:
                            parts.append(ident.project_category_medium)
                        if ident.project_category_small:
                            parts.append(ident.project_category_small)
                        formatted_category = ' / '.join(parts)
            
            history_list.append({
                "node_name": history_task.task_name,
                "approver_name": history_assignee.real_name if history_assignee else "",
                "status": history_task.status,
                "comment": history_task.comment or "",
                "created_at": str(history_task.started_at) if history_task.started_at else "",
                "formatted_category": formatted_category
            })
        
        item["workflow_history"] = history_list
        
        # 获取附件信息
        from app.models.green_finance import TaskAttachment
        attachments = db.query(TaskAttachment).filter(
            TaskAttachment.task_id.in_([ht.id for ht in history_tasks])
        ).all()
        
        item["attachments"] = []
        for attachment in attachments:
            item["attachments"].append({
                "id": attachment.id,
                "task_id": attachment.task_id,
                "task_key": attachment.task_key,
                "task_name": attachment.task_name,
                "uploader_name": attachment.uploader.real_name if attachment.uploader else "",
                "original_filename": attachment.original_filename,
                "file_size": attachment.file_size,
                "download_url": attachment.download_url,
                "created_at": str(attachment.created_at) if attachment.created_at else ""
            })
        
        result.append(item)
    
    return {
        "data": result,
        "total": total
    }


@router.post("/tasks/{task_id}/complete")
async def complete_task(
    task_id: int,
    task_data: WorkflowTaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """完成任务"""
    # 先尝试作为 workflow_task ID 查找
    task = db.query(WorkflowTask).filter(
        WorkflowTask.id == task_id,
        WorkflowTask.assignee_id == current_user.id,
        WorkflowTask.status == "待处理"
    ).first()
    
    # 如果找不到，尝试作为 green_identification ID 查找对应的待处理任务
    if not task:
        # 获取该认定对应的待处理任务
        task = db.query(WorkflowTask).filter(
            WorkflowTask.identification_id == task_id,
            WorkflowTask.assignee_id == current_user.id,
            WorkflowTask.status == "待处理"
        ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在或无权操作")
    
    WorkflowEngine.complete_task(db, task, task_data.approval_result, task_data.comment, task_data.reason)
    
    return {"message": "任务已完成"}


@router.post("/tasks/{task_id}/withdraw")
async def withdraw_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """撤回任务
    
    从已办任务列表中撤回任务到待办任务列表
    task_id可以是workflow_task的ID或green_identification的ID
    """
    # 先尝试作为 workflow_task ID 查找已完成的任务
    task = db.query(WorkflowTask).filter(
        WorkflowTask.id == task_id,
        WorkflowTask.assignee_id == current_user.id,
        WorkflowTask.status == "已完成"
    ).first()
    
    # 如果找不到，尝试作为 green_identification ID 查找对应的已完成任务
    if not task:
        task = db.query(WorkflowTask).filter(
            WorkflowTask.identification_id == task_id,
            WorkflowTask.assignee_id == current_user.id,
            WorkflowTask.status == "已完成"
        ).order_by(WorkflowTask.completed_at.desc()).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在或无法撤回")
    
    try:
        WorkflowEngine.withdraw_task(db, task, current_user)
        return {"message": "任务已撤回到待办任务列表"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
async def withdraw_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """撤回任务"""
    # 先尝试作为 workflow_task ID 查找
    task = db.query(WorkflowTask).filter(
        WorkflowTask.id == task_id,
        WorkflowTask.assignee_id == current_user.id
    ).first()
    
    # 如果找不到，尝试作为 green_identification ID 查找对应的任务
    if not task:
        task = db.query(WorkflowTask).filter(
            WorkflowTask.identification_id == task_id,
            WorkflowTask.assignee_id == current_user.id
        ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在或无权操作")
    
    WorkflowEngine.withdraw_task(db, task, current_user)
    
    return {"message": "任务已撤回"}


@router.post("/tasks/{task_id}/return")
async def return_task(
    task_id: int,
    task_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """退回任务
    
    退回规则：
    1. 客户经理（manager_identification）：不能退回
    2. 二级分行绿色金融管理岗（branch_review）：可以退回到客户经理
    3. 一级分行绿色金融管理岗（first_approval）：可以退回给客户经理或二级分行绿色金融管理岗
    4. 一级分行绿色金融复核岗（final_review）：可以退回到客户经理、二级分行绿色金融管理岗或一级分行绿色金融管理岗
    """
    # 先尝试作为 workflow_task ID 查找
    task = db.query(WorkflowTask).filter(
        WorkflowTask.id == task_id,
        WorkflowTask.assignee_id == current_user.id,
        WorkflowTask.status == "待处理"
    ).first()
    
    # 如果找不到，尝试作为 green_identification ID 查找对应的待处理任务
    if not task:
        task = db.query(WorkflowTask).filter(
            WorkflowTask.identification_id == task_id,
            WorkflowTask.assignee_id == current_user.id,
            WorkflowTask.status == "待处理"
        ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在或无权操作")
    
    WorkflowEngine.return_task(db, task, task_data.get("return_to_node"), task_data.get("comment"), current_user)
    
    return {"message": "任务已退回"}


@router.post("/tasks/{task_id}/save")
async def save_task(
    task_id: int,
    task_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """保存（暂存）任务"""
    import logging
    logging.info(f"save_task called: task_id={task_id}, task_data={task_data}, user={current_user.username}")
    
    # 先尝试作为 workflow_task ID 查找
    task = db.query(WorkflowTask).filter(
        WorkflowTask.id == task_id,
        WorkflowTask.assignee_id == current_user.id
    ).first()
    
    # 如果找不到，尝试作为 green_identification ID 查找对应的任务
    if not task:
        task = db.query(WorkflowTask).filter(
            WorkflowTask.identification_id == task_id,
            WorkflowTask.assignee_id == current_user.id
        ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在或无权操作")
    
    logging.info(f"task found: id={task.id}, task_key={task.task_key}")
    
    # 更新任务的绿色分类信息
    identification = db.query(GreenIdentification).filter(
        GreenIdentification.id == task.identification_id
    ).first()
    
    if identification:
        logging.info(f"identification found: id={identification.id}, current category: {identification.project_category_large}/{identification.project_category_medium}/{identification.project_category_small}")
        
        if task_data.get("project_category_large"):
            identification.project_category_large = task_data["project_category_large"]
            logging.info(f"updated project_category_large: {task_data['project_category_large']}")
        if task_data.get("project_category_medium"):
            identification.project_category_medium = task_data["project_category_medium"]
            logging.info(f"updated project_category_medium: {task_data['project_category_medium']}")
        if task_data.get("project_category_small"):
            identification.project_category_small = task_data["project_category_small"]
            logging.info(f"updated project_category_small: {task_data['project_category_small']}")
        if task_data.get("comment"):
            task.comment = task_data["comment"]
        
        # 保存当前任务的绿色分类信息到任务记录
        task.project_category_large = identification.project_category_large
        task.project_category_medium = identification.project_category_medium
        task.project_category_small = identification.project_category_small
        # 获取并保存格式化的分类名称
        from app.services.workflow import get_formatted_category
        formatted_category = get_formatted_category(db, identification)
        task.formatted_category = formatted_category
        
        logging.info(f"task updated: id={task.id}, category: {task.project_category_large}/{task.project_category_medium}/{task.project_category_small}, formatted: {task.formatted_category}")
        
        # 更新认定状态为暂存
        identification.status = TaskStatus.DRAFT.value
        
        db.commit()
    
    return {"message": "任务已暂存"}


@router.put("/tasks/{task_id}/category")
async def update_task_category(
    task_id: int,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新任务的绿色金融支持项目目录"""
    import logging
    logging.info(f"收到PUT /api/tasks/{task_id}/category请求, data={data}")
    
    # task_id 可能是 workflow_task 的 ID，也可能是 green_identification 的 ID
    # 先尝试作为 workflow_task ID 查找
    task = db.query(WorkflowTask).filter(WorkflowTask.id == task_id).first()
    
    # 如果找不到，尝试作为 green_identification ID 查找对应的 workflow_task
    if not task:
        task = db.query(WorkflowTask).filter(WorkflowTask.identification_id == task_id).first()
    
    if not task:
        logging.warning(f"任务ID {task_id} 不存在")
        raise HTTPException(status_code=404, detail="任务不存在")
    
    identification = db.query(GreenIdentification).filter(
        GreenIdentification.id == task.identification_id
    ).first()
    if not identification:
        raise HTTPException(status_code=404, detail="认定不存在")
    
    # 更新分类信息
    identification.project_category_large = data.get("project_category_large")
    identification.project_category_medium = data.get("project_category_medium")
    identification.project_category_small = data.get("project_category_small")
    
    # 同时更新当前workflow_task的绿色分类
    task.project_category_large = data.get("project_category_large")
    task.project_category_medium = data.get("project_category_medium")
    task.project_category_small = data.get("project_category_small")
    
    # 获取并保存格式化的分类名称
    from app.services.workflow import get_formatted_category
    formatted_category = get_formatted_category(db, identification)
    task.formatted_category = formatted_category
    
    db.commit()
    
    return {"message": "绿色金融支持项目目录已更新"}


@router.get("/tasks/export")
async def export_tasks(
    customer_name: Optional[str] = Query(None),
    business_type: Optional[str] = Query(None),
    loan_account: Optional[str] = Query(None),
    loan_date_start: Optional[str] = Query(None),
    loan_date_end: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(10000, ge=1, le=100000, description="最大导出数量,默认10000条,最大100000条"),
    only_complete: bool = Query(False, description="是否只导出有完整数据的记录(有完成时间、发起人和分类信息)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导出任务数据为Excel"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Export tasks called - customer_name={customer_name}, business_type={business_type}, loan_account={loan_account}, loan_date_start={loan_date_start}, loan_date_end={loan_date_end}, status={status}, limit={limit}")
    from fastapi.responses import StreamingResponse
    from app.models.user import Organization
    import io
    import csv
    from datetime import datetime
    
    # 构建查询
    query = db.query(GreenIdentification)
    
    # 权限控制：根据用户机构级别过滤数据
    if not current_user.is_superuser:
        user_org = db.query(Organization).filter(Organization.id == current_user.org_id).first()
        if user_org:
            if user_org.level == 2:
                org_ids = [user_org.id]
                child_orgs = db.query(Organization).filter(Organization.parent_id == user_org.id).all()
                for child in child_orgs:
                    org_ids.append(child.id)
                    grandchild_orgs = db.query(Organization).filter(Organization.parent_id == child.id).all()
                    for grandchild in grandchild_orgs:
                        org_ids.append(grandchild.id)
                query = query.filter(GreenIdentification.org_id.in_(org_ids))
            elif user_org.level == 3:
                query = query.filter(GreenIdentification.org_id == current_user.org_id)
    
    # 添加查询条件
    if customer_name:
        query = query.filter(GreenIdentification.customer_name.like(f"%{customer_name}%"))
    if business_type:
        query = query.filter(GreenIdentification.business_type == business_type)
    if loan_account:
        query = query.filter(GreenIdentification.loan_account.like(f"%{loan_account}%"))
    if loan_date_start:
        query = query.filter(GreenIdentification.disbursement_date >= loan_date_start)
    if loan_date_end:
        query = query.filter(GreenIdentification.disbursement_date <= loan_date_end)
    if status:
        query = query.filter(GreenIdentification.status == status)
    
    # 获取数据,限制最大数量
    # 如果只导出有完整数据的记录,添加过滤条件
    if only_complete:
        query = query.filter(
            GreenIdentification.completed_at.isnot(None),
            GreenIdentification.initiator_id.isnot(None)
        )
    
    identifications = query.order_by(GreenIdentification.created_at.desc()).limit(limit).all()
    
    logger.info(f"Exporting {len(identifications)} records (only_complete={only_complete})")
    
    # 预加载所有发起人信息,避免N+1查询
    initiator_ids = [ident.initiator_id for ident in identifications if ident.initiator_id]
    initiators = {}
    if initiator_ids:
        users = db.query(User).filter(User.id.in_(initiator_ids)).all()
        initiators = {user.id: user.real_name for user in users}
    
    # 转换为CSV格式
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 写入表头
    writer.writerow([
        '任务ID', '客户名称', '业务品种', '贷款账号', '放款金额', '放款日期',
        '绿色金融支持项目目录', '发起人', '状态', '创建时间', '完成时间'
    ])
    
    # 写入数据
    from app.services.workflow import get_formatted_category
    for ident in identifications:
        formatted_category = get_formatted_category(db, ident)
        initiator_name = initiators.get(ident.initiator_id, "")
        
        writer.writerow([
            ident.id,
            ident.customer_name,
            ident.business_type,
            ident.loan_account,
            str(ident.loan_amount) if ident.loan_amount else "0",
            str(ident.disbursement_date) if ident.disbursement_date else "",
            formatted_category or ident.project_category_medium or "",
            initiator_name,
            ident.status,
            str(ident.created_at) if ident.created_at else "",
            str(ident.completed_at) if ident.completed_at else ""
        ])
    
    # 创建响应
    output.seek(0)
    from urllib.parse import quote
    filename = f'green_finance_tasks_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    filename_utf8 = f'绿色金融任务导出_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    response = StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        media_type='text/csv; charset=utf-8-sig',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"; filename*=UTF-8\'\'{quote(filename_utf8)}'
        }
    )
    
    return response


@router.get("/tasks/online-report")
async def get_online_report(
    level1_branch: Optional[str] = Query(None, description="一级分行"),
    level2_branch: Optional[str] = Query(None, description="二级分行"),
    branch: Optional[str] = Query(None, description="支行"),
    loan_account: Optional[str] = Query(None, description="贷款账号"),
    green_large: Optional[str] = Query(None, description="绿色大类"),
    green_medium: Optional[str] = Query(None, description="绿色中类"),
    green_small: Optional[str] = Query(None, description="绿色小类"),
    initiator: Optional[str] = Query(None, description="发起人"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=1000, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取在线功能报表"""
    from app.models.user import Organization
    
    # 构建查询
    query = db.query(GreenIdentification)
    
    # 关联查询用户表获取发起人信息
    query = query.join(User, GreenIdentification.initiator_id == User.id, isouter=True)
    
    # 关联查询机构表
    query = query.join(Organization, GreenIdentification.org_id == Organization.id, isouter=True)
    
    # 应用筛选条件
    if level1_branch:
        query = query.filter(Organization.name.like(f"%{level1_branch}%"))
    if level2_branch:
        query = query.filter(Organization.name.like(f"%{level2_branch}%"))
    if branch:
        query = query.filter(Organization.name.like(f"%{branch}%"))
    if loan_account:
        query = query.filter(GreenIdentification.loan_account.like(f"%{loan_account}%"))
    if green_large:
        query = query.filter(GreenIdentification.project_category_large.like(f"%{green_large}%"))
    if green_medium:
        query = query.filter(GreenIdentification.project_category_medium.like(f"%{green_medium}%"))
    if green_small:
        query = query.filter(GreenIdentification.project_category_small.like(f"%{green_small}%"))
    if initiator:
        query = query.filter(User.real_name.like(f"%{initiator}%"))
    
    # 获取总数
    total = query.count()
    
    # 排序规则：按照完成时间倒序排列，完成时间为空的排列到最后
    from sqlalchemy import case
    
    records = query.order_by(
        case(
            (GreenIdentification.completed_at == None, 1),  # 完成时间为空，排最后
            else_=0  # 有完成时间，排前面
        ),
        GreenIdentification.completed_at.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    # 转换为报表数据格式
    report_data = []
    for record in records:
        # 获取机构信息
        org = record.organization
        
        # 根据机构层级设置一级分行、二级分行、支行
        level1_name = ''  # 一级分行
        level2_name = ''  # 二级分行
        branch_name = ''  # 支行
        
        if org:
            # 根据实际的机构关系判断层级
            # 支行：level=3
            # 一级分行：level=2 且 parent_level=1
            # 二级分行：level=2 且 parent_level=2
            
            if org.level == 3:
                # 支行
                branch_name = org.name
                if org.parent:
                    # 如果父机构是level=2且父机构的父机构是总行（level=1），说明父机构是一级分行
                    if org.parent.level == 2 and org.parent.parent and org.parent.parent.level == 1:
                        # 父机构是一级分行，二级分行为空
                        level1_name = org.parent.name
                    else:
                        # 其他情况，父机构是二级分行
                        level2_name = org.parent.name
                        if org.parent.parent:
                            level1_name = org.parent.parent.name
            elif org.level == 2:
                if org.parent and org.parent.level == 1:
                    # 一级分行：level=2 且 parent_level=1
                    level1_name = org.name
                elif org.parent and org.parent.level == 2:
                    # 二级分行：level=2 且 parent_level=2
                    level2_name = org.name
                    level1_name = org.parent.name
                else:
                    # 没有父机构，默认为一级分行
                    level1_name = org.name
            # level=1 总行不显示在一级分行列
        
        # 确保一级分行列不显示"总行"
        if '总行' in level1_name:
            level1_name = ''
        
        report_data.append({
            "id": record.id,
            "level1_branch": level1_name,
            "level2_branch": level2_name,
            "branch": branch_name,
            "loan_account": record.loan_account,
            "loan_amount": record.loan_amount,
            "green_large": record.project_category_large,
            "green_medium": record.project_category_medium,
            "green_small": record.project_category_small,
            "initiator": record.initiator.real_name if record.initiator else '',
            "customer_name": record.customer_name,
            "business_type": record.business_type,
            "loan_date": record.disbursement_date.strftime('%Y-%m-%d') if record.disbursement_date else '',
            "status": record.status,
            "created_at": record.created_at.strftime('%Y-%m-%d %H:%M:%S') if record.created_at else '',
            "completed_at": record.completed_at.strftime('%Y-%m-%d %H:%M:%S') if record.completed_at else '',
            "approval_result": '',
        })
    
    return {
        "data": report_data,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/tasks/{task_id}")
async def get_task_detail(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取任务详情"""
    # task_id 可能是 green_identification 的 ID，也可能是 workflow_task 的 ID
    # 先检查是否存在该ID的workflow_task
    task = db.query(WorkflowTask).filter(WorkflowTask.id == task_id).first()
    
    # 再检查是否存在该ID的identification
    identification = db.query(GreenIdentification).filter(GreenIdentification.id == task_id).first()
    
    # 如果两者都存在，优先使用workflow_task（因为TaskCompleted.vue传的是task_id）
    # 如果只有task存在，使用task
    # 如果只有identification存在，使用identification
    if task:
        # 找到了task，获取对应的identification
        identification = db.query(GreenIdentification).filter(
            GreenIdentification.id == task.identification_id
        ).first()
    elif identification:
        # 只有identification存在，获取对应的第一个task
        task = db.query(WorkflowTask).filter(WorkflowTask.identification_id == task_id).first()
    
    if not identification or not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 获取格式化的带编号的分类名称
    from app.services.workflow import get_formatted_category
    formatted_category = get_formatted_category(db, identification)
    
    # 获取发起人名称
    initiator = db.query(User).filter(User.id == identification.initiator_id).first()
    initiator_name = initiator.real_name if initiator else ""
    
    # 获取机构名称
    org_name = identification.organization.name if identification.organization else ""
    
    # 构建返回结果
    result = {
        "id": identification.id,
        "identification_id": identification.id,  # 添加identification_id字段，与id相同
        "loan_code": identification.loan_code,
        "customer_name": identification.customer_name,
        "customer_id": identification.customer_id,
        "business_type": identification.business_type,
        "loan_account": identification.loan_account,
        "loan_amount": identification.loan_amount,
        "disbursement_date": identification.disbursement_date,
        "maturity_date": identification.maturity_date,
        "interest_rate": identification.interest_rate,
        "green_percentage": identification.green_percentage,
        "green_loan_balance": identification.green_loan_balance,
        "project_category_large": identification.project_category_large,
        "project_category_medium": identification.project_category_medium,
        "project_category_small": identification.project_category_small,
        "formatted_category": formatted_category,
        "esg_risk_level": identification.esg_risk_level,
        "esg_performance_level": identification.esg_performance_level,
        "status": identification.status,
        "initiator_id": identification.initiator_id,
        "initiator_name": initiator_name,
        "current_handler_id": identification.current_handler_id,
        "org_id": identification.org_id,
        "org_name": org_name,
        "created_at": identification.created_at,
        "updated_at": identification.updated_at,
        "completed_at": identification.completed_at,
        "deadline": identification.deadline,
        "started_at": task.workflow_instance.started_at if task.workflow_instance else None,
        "attachments": []
    }
    
    # 获取该认定记录的所有工作流任务
    workflow_tasks = db.query(WorkflowTask).filter(
        WorkflowTask.identification_id == identification.id
    ).order_by(WorkflowTask.started_at).all()
    
    # 检查是否有当前待处理任务
    current_task = [t for t in workflow_tasks if t.status == "待处理"]
    if current_task:
        # 如果有当前待处理任务，使用当前待处理任务的分类
        current_pending_task = current_task[0]
        if current_pending_task.formatted_category:
            result["project_category_large"] = current_pending_task.project_category_large
            result["project_category_medium"] = current_pending_task.project_category_medium
            result["project_category_small"] = current_pending_task.project_category_small
            result["formatted_category"] = current_pending_task.formatted_category
    else:
        # 如果没有当前待处理任务，获取上个节点最新的绿色分类（排除当前任务，只选择已完成的任务）
        previous_tasks = [t for t in workflow_tasks if t.id != task.id and t.status == "已完成"]
        if previous_tasks:
            # 按完成时间倒序排列，取最新的
            previous_tasks.sort(key=lambda x: x.completed_at if x.completed_at else x.started_at, reverse=True)
            latest_previous_task = previous_tasks[0]
            
            # 如果上个任务有分类信息，使用上个任务的分类
            if latest_previous_task.formatted_category:
                result["project_category_large"] = latest_previous_task.project_category_large
                result["project_category_medium"] = latest_previous_task.project_category_medium
                result["project_category_small"] = latest_previous_task.project_category_small
                result["formatted_category"] = latest_previous_task.formatted_category
    
    # 获取附件信息
    from app.models.green_finance import TaskAttachment
    import logging
    logging.info(f"DEBUG: task_id={task_id}, identification_id={identification.id}")
    logging.info(f"DEBUG: workflow_tasks={[ht.id for ht in workflow_tasks]}")
    
    attachments = db.query(TaskAttachment).filter(
        TaskAttachment.task_id.in_([ht.id for ht in workflow_tasks])
    ).all()
    
    logging.info(f"DEBUG: attachments查询结果数量={len(attachments)}")
    
    for attachment in attachments:
        result["attachments"].append({
            "id": attachment.id,
            "task_id": attachment.task_id,
            "task_key": attachment.task_key,
            "task_name": attachment.task_name,
            "uploader_name": attachment.uploader.real_name if attachment.uploader else "",
            "original_filename": attachment.original_filename,
            "file_size": attachment.file_size,
            "download_url": attachment.download_url,
            "created_at": attachment.created_at.isoformat() if attachment.created_at else ""
        })
    
    logging.info(f"DEBUG: result['attachments']数量={len(result['attachments'])}")
    
    # 根据分类名称查找对应的code
    if result.get("project_category_large") or result.get("project_category_medium") or result.get("project_category_small"):
        large_code = None
        medium_code = None
        small_code = None
        
        if result.get("project_category_large"):
            large_result = db.execute(text("""
                SELECT large_code
                FROM green_project_categories
                WHERE large_name = :large
                ORDER BY large_code DESC
                LIMIT 1
            """), {"large": result["project_category_large"]}).fetchone()
            if large_result:
                large_code = large_result[0]
        
        if result.get("project_category_medium") and large_code:
            medium_result = db.execute(text("""
                SELECT medium_code
                FROM green_project_categories
                WHERE large_code = :large_code AND medium_name = :medium
                ORDER BY medium_code DESC
                LIMIT 1
            """), {"large_code": large_code, "medium": result["project_category_medium"]}).fetchone()
            if medium_result:
                medium_code = medium_result[0]
        
        if result.get("project_category_small") and medium_code:
            small_result = db.execute(text("""
                SELECT small_code
                FROM green_project_categories
                WHERE large_code = :large_code AND medium_code = :medium_code AND small_name = :small
                ORDER BY small_code DESC
                LIMIT 1
            """), {"large_code": large_code, "medium_code": medium_code, "small": result["project_category_small"]}).fetchone()
            if small_result:
                small_code = small_result[0]
        
        result["project_category_large_code"] = large_code
        result["project_category_medium_code"] = medium_code
        result["project_category_small_code"] = small_code
    
    return result


@router.get("/identifications/{id}/workflow", response_model=List[WorkflowTaskSchema])
async def get_workflow_history(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取工作流历史"""
    # 处理带前缀的ID，格式：ID-{identification_id}
    if id.startswith("ID-"):
        identification_id = int(id.split("-")[1])
    else:
        # 兼容旧格式，直接作为数字ID处理
        identification_id = int(id)
    
    # 检查 identification 是否存在
    identification = db.query(GreenIdentification).filter(GreenIdentification.id == identification_id).first()
    if not identification:
        raise HTTPException(status_code=404, detail="认定信息不存在")
    
    tasks = db.query(WorkflowTask).filter(
        WorkflowTask.identification_id == identification_id
    ).order_by(WorkflowTask.started_at).all()
    
    # 增加用户信息
    result = []
    for task in tasks:
        assignee = db.query(User).filter(User.id == task.assignee_id).first()
        position_name = None
        if assignee and assignee.role:
            position_name = assignee.role.name
        
        # 如果认定状态为暂存且任务状态为待处理，则显示暂存
        display_status = task.status
        if identification.status == TaskStatus.DRAFT.value and task.status == "待处理":
            display_status = "暂存"
        
        # 如果formatted_category为空，动态计算
        formatted_category = task.formatted_category
        if not formatted_category:
            formatted_category = get_formatted_category(db, identification)
        
        task_dict = {
            "id": task.id,
            "task_key": task.task_key,
            "task_name": task.task_name,
            "node_id": task.node_id,
            "assignee_id": task.assignee_id,
            "status": display_status,
            "approval_result": task.approval_result,
            "comment": task.comment,
            "reason": task.reason,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "assignee_name": assignee.real_name if assignee else None,
            "assignee_username": assignee.username if assignee else None,  # 添加办理人员账号
            "position_name": position_name,
            "project_category_large": task.project_category_large,
            "project_category_medium": task.project_category_medium,
            "project_category_small": task.project_category_small,
            "formatted_category": formatted_category
        }
        result.append(WorkflowTaskSchema(**task_dict))
    
    return result


@router.get("/identifications/{id}/workflow-instance", response_model=WorkflowInstanceSchema)
async def get_workflow_instance(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取工作流实例"""
    # 处理带前缀的ID，格式：ID-{identification_id}
    if id.startswith("ID-"):
        identification_id = int(id.split("-")[1])
    else:
        # 兼容旧格式，直接作为数字ID处理
        identification_id = int(id)
    
    workflow = db.query(WorkflowInstance).filter(
        WorkflowInstance.identification_id == identification_id
    ).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流实例不存在")
    
    return workflow


@router.get("/workflow-instances")
async def get_workflow_instances(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取工作流实例列表"""
    # 联表查询，获取客户名称和贷款账号
    query = db.query(WorkflowInstance, GreenIdentification).join(
        GreenIdentification, WorkflowInstance.identification_id == GreenIdentification.id
    )
    
    if status:
        query = query.filter(WorkflowInstance.status == status)
    
    total = query.count()
    offset = (page - 1) * page_size
    
    # 按照状态和完成时间倒序排列
    # 已完成的按完成时间倒序，未完成的按开始时间倒序
    from sqlalchemy import case, literal_column, desc
    
    instances = query.order_by(
        case(
            (WorkflowInstance.status == 'completed', literal_column("'0'")),
            else_=literal_column("'1'")
        ),
        desc(WorkflowInstance.ended_at),
        desc(WorkflowInstance.started_at)
    ).offset(offset).limit(page_size).all()
    
    result_data = []
    for instance, identification in instances:
        result_data.append({
            "id": instance.id,
            "instance_key": instance.case_id,
            "definition_id": None,
            "business_key": instance.business_key,
            "status": instance.status,
            "current_node": instance.current_node,
            "started_by": None,
            "started_at": instance.started_at.isoformat() if instance.started_at else None,
            "completed_at": instance.ended_at.isoformat() if instance.ended_at else None,
            "customer_name": identification.customer_name,
            "loan_account": identification.loan_account,
            "definition": {
                "id": instance.process_definition_id,
                "key": instance.process_key,
                "name": "绿色认定流程",
                "version": get_workflow_version(db, instance.process_definition_id)
            }
        })
    
    return {
        "data": result_data,
        "total": total
    }


@router.get("/workflow-instances/{instance_id}/tasks")
async def get_workflow_instance_tasks(
    instance_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取绿色金融工作流实例的任务记录"""
    instance = db.query(WorkflowInstance).filter(WorkflowInstance.id == instance_id).first()
    if not instance:
        raise HTTPException(status_code=404, detail="工作流实例不存在")
    
    # 获取该实例的所有任务
    tasks = db.query(WorkflowTask).filter(
        WorkflowTask.workflow_instance_id == instance_id
    ).order_by(WorkflowTask.started_at).all()
    
    result = []
    for task in tasks:
        assignee = db.query(User).filter(User.id == task.assignee_id).first()
        task_dict = {
            "id": task.id,
            "task_name": task.task_name,
            "assignee_name": assignee.real_name if assignee else "",
            "status": task.status,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "comment": task.comment or ""
        }
        result.append(task_dict)
    
    return result


@router.delete("/workflow-instances/{instance_id}")
async def delete_workflow_instance(
    instance_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除绿色金融工作流实例"""
    import traceback

    instance = db.query(WorkflowInstance).get(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="工作流实例不存在")

    try:
        # 检查实例状态，审批中的实例不允许删除
        if instance.status == '审批中':
            raise HTTPException(
                status_code=400,
                detail="审批中的工作流实例不允许删除"
            )

        # 删除关联的任务
        db.query(WorkflowTask).filter(WorkflowTask.workflow_instance_id == instance_id).delete()

        # 删除关联的绿色认定记录
        if instance.identification_id:
            db.query(GreenIdentification).filter(GreenIdentification.id == instance.identification_id).delete()

        # 删除实例
        db.delete(instance)
        db.commit()

        return {"message": "工作流实例删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        error_detail = f"删除失败: {str(e)}\n{traceback.format_exc()}"
        print(f"Database error: {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)


@router.get("/green-project-categories")
async def get_green_project_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取绿色金融支持项目目录列表"""
    result = db.execute(text("""
        SELECT id, large_code, large_name, medium_code, medium_name, 
               small_code, small_name, formatted_name
        FROM green_project_categories
        ORDER BY 
          CAST(large_code AS UNSIGNED),
          CAST(medium_code AS UNSIGNED),
          CAST(small_code AS UNSIGNED)
    """)).fetchall()
    
    categories = []
    for row in result:
        categories.append({
            "id": row[0],
            "large_code": row[1],
            "large_name": row[2],
            "medium_code": row[3],
            "medium_name": row[4],
            "small_code": row[5],
            "small_name": row[6],
            "formatted_name": row[7]
        })
    
    return categories


@router.get("/green-categories")
async def get_green_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取绿色金融支持项目目录"""
    result = db.execute(text("""
        SELECT 
            large_code,
            large_name,
            medium_code,
            medium_name,
            small_code,
            small_name,
            formatted_name
        FROM green_project_categories
        ORDER BY 
          CAST(large_code AS UNSIGNED),
          CAST(medium_code AS UNSIGNED),
          CAST(small_code AS UNSIGNED)
    """))
    
    categories = []
    for row in result:
        categories.append({
            "large_code": row[0],
            "large_name": row[1],
            "medium_code": row[2],
            "medium_name": row[3],
            "small_code": row[4],
            "small_name": row[5],
            "formatted_name": row[6]
        })
    
    return categories


@router.post("/tasks/{task_id}/mark-non-green")
async def mark_task_as_non_green(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记任务为非绿"""
    # 获取任务
    task = db.query(WorkflowTask).filter(WorkflowTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有任务处理人可以标记为非绿")
    
    if task.status != "待处理":
        raise HTTPException(status_code=400, detail="只能标记待处理状态的任务")
    
    # 更新认定分类为非绿色贷款
    identification = db.query(GreenIdentification).filter(GreenIdentification.id == task.identification_id).first()
    if identification:
        identification.project_category_large = "其他"
        identification.project_category_medium = "非绿色贷款"
        identification.project_category_small = "非绿色贷款"
        identification.green_project_category = "10 其他 / 10.1 非绿色贷款 / 10.1.1 非绿色贷款"
    
    # 终止任务
    task.status = "系统终止"
    task.completed_at = datetime.now()
    task.approval_result = "系统终止"
    task.comment = "标记为非绿"
    
    # 终止工作流实例
    workflow = task.workflow_instance
    workflow.status = "已办结"
    workflow.ended_at = datetime.now()
    workflow.current_node = "end"
    
    # 更新认定状态
    identification.status = TaskStatus.SYSTEM_TERMINATED.value
    identification.completed_at = datetime.now()
    
    db.commit()
    
    return {"message": "任务已标记为非绿"}