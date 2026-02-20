#!/usr/bin/env python3
import re

with open('app/services/workflow.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 新的撤回函数
new_withdraw_function = '''    @classmethod
    def withdraw_task(cls, db: Session, task: WorkflowTask, user: User):
        """撤回任务
        
        撤回规则：
        1. 只能撤回已完成的任务
        2. 检查下一个节点是否已经有待处理任务（已被保存或提交）
        3. 如果下一个节点还没有待处理任务，则可以撤回
        4. 一级分行绿色金融复核岗（final_review）完成后不能撤回
        """
        if task.status != "已完成":
            raise ValueError("只能撤回已完成的任务")
        
        if task.assignee_id != user.id:
            raise ValueError("只能撤回自己经办的任务")
        
        current_node = task.task_key
        
        # 一级分行绿色金融复核岗完成后不能撤回
        if current_node == "final_review":
            raise ValueError("一级分行绿色金融复核岗完成后不能撤回")
        
        # 检查下一个节点是否已有待处理任务（已被保存或提交）
        workflow = task.workflow_instance
        next_node = cls._get_next_node(current_node)
        
        if next_node:
            # 检查下一节点是否有待处理任务
            next_task = db.query(WorkflowTask).filter(
                WorkflowTask.workflow_instance_id == workflow.id,
                WorkflowTask.task_key == next_node,
                WorkflowTask.status == "待处理"
            ).first()
            
            if next_task:
                raise ValueError("下一个节点已操作，无法撤回")
        
        # 标记当前任务为待处理（撤回到自己名下）
        task.status = "待处理"
        task.completed_at = None
        task.approval_result = None
        task.reason = None
        task.updated_at = datetime.now()
        
        # 更新流程实例的当前节点
        workflow.current_node = current_node
        workflow.status = "running"
        
        # 更新认定信息的处理人
        identification = task.identification
        identification.current_handler_id = user.id
        identification.status = TaskStatus.PROCESSING.value
        
        db.commit()'''

# 使用正则表达式匹配并替换整个withdraw_task函数
pattern = r'@classmethod\s+def withdraw_task\(cls, db: Session, task: WorkflowTask, user: User\):.*?(?=\n    @classmethod|\n    def |\Z)'
content_new = re.sub(pattern, new_withdraw_function, content, flags=re.DOTALL)

with open('app/services/workflow.py', 'w', encoding='utf-8') as f:
    f.write(content_new)

print("撤回函数已更新")
