"""定时任务调度器"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def check_overdue_tasks():
    """检查并终止超时任务"""
    from app.database import SessionLocal
    from app.models.green_finance import WorkflowTask, WorkflowInstance, GreenIdentification, TaskStatus
    
    db = SessionLocal()
    try:
        now = datetime.now()
        
        # 查找所有超时的待处理任务
        overdue_tasks = db.query(WorkflowTask).filter(
            WorkflowTask.status == "待处理",
            WorkflowTask.started_at.isnot(None)
        ).join(
            GreenIdentification, WorkflowTask.identification_id == GreenIdentification.id
        ).filter(
            GreenIdentification.deadline.isnot(None),
            GreenIdentification.deadline <= now
        ).all()
        
        logger.info(f"检查到 {len(overdue_tasks)} 个超时任务")
        
        for task in overdue_tasks:
            # 终止任务
            task.status = "系统终止"
            task.completed_at = now
            task.approval_result = "系统终止"
            task.comment = "任务超时，系统自动终止"
            
            # 终止工作流实例
            workflow = task.workflow_instance
            workflow.status = "已办结"
            workflow.ended_at = now
            workflow.current_node = "end"
            
            # 更新认定状态
            identification = workflow.identification
            identification.status = TaskStatus.WITHDRAWN.value  # 使用撤回状态
            identification.completed_at = now
            
            logger.info(f"任务 {task.id} ({task.task_name}) 已超时终止")
        
        db.commit()
        logger.info(f"成功终止 {len(overdue_tasks)} 个超时任务")
        
    except Exception as e:
        logger.error(f"检查超时任务时发生错误: {e}")
        db.rollback()
    finally:
        db.close()


def start_scheduler():
    """启动定时任务调度器"""
    # 每天凌晨0点执行一次
    scheduler.add_job(
        check_overdue_tasks,
        trigger=CronTrigger(hour=0, minute=0),
        id='check_overdue_tasks',
        name='检查超时任务',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("定时任务调度器已启动")


def stop_scheduler():
    """停止定时任务调度器"""
    scheduler.shutdown()
    logger.info("定时任务调度器已停止")