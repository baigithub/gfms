#!/usr/bin/env python
"""创建 workflow_variables 表"""

from app.database import engine, Base
from app.models.workflow_variable import WorkflowVariable
from app.models.workflow import ProcessDefinition

# 创建所有表
Base.metadata.create_all(bind=engine)

print("数据库表创建成功！")
print("已创建/更新表：workflow_variables")