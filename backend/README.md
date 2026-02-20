# 绿色金融管理系统 - 后端

基于 FastAPI + MySQL + SQLAlchemy 的绿色金融管理系统后端服务。

## 技术栈

- **框架**: FastAPI 0.104.1
- **数据库**: MySQL 8.0+
- **ORM**: SQLAlchemy 2.0.23
- **认证**: JWT (python-jose)
- **密码加密**: bcrypt

## 项目结构

```
backend/
├── app/
│   ├── models/          # 数据模型
│   │   ├── user.py      # 用户、角色、机构模型
│   │   └── green_finance.py  # 绿色金融业务模型
│   ├── schemas/         # Pydantic模式
│   │   ├── user.py
│   │   └── green_finance.py
│   ├── routers/         # API路由
│   │   ├── auth.py      # 认证路由
│   │   ├── green_finance.py  # 绿色金融业务路由
│   │   └── system.py    # 系统管理路由
│   ├── services/        # 业务逻辑
│   │   ├── auth.py      # 认证服务
│   │   └── workflow.py  # 工作流引擎
│   ├── config.py        # 配置文件
│   ├── database.py      # 数据库连接
│   └── main.py          # 应用入口
├── init_db.py          # 数据库初始化脚本
├── requirements.txt    # Python依赖
└── .env.example        # 环境变量示例
```

## 安装与运行

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置数据库

复制 `.env.example` 为 `.env` 并修改数据库配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=green_finance
```

### 3. 创建数据库

```bash
mysql -u root -p
CREATE DATABASE green_finance CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 4. 初始化数据库

```bash
python init_db.py
```

这将创建所有表并初始化默认角色、机构和用户数据。

### 5. 启动服务

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

或直接运行：

```bash
python -m app.main
```

服务将在 `http://localhost:8000` 启动。

### 6. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 默认账号

初始化脚本会创建以下测试账号：

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| admin | admin123 | 超级管理员 | 拥有所有权限 |
| manager1 | manager123 | 客户经理 | 负责发起绿色贷款认定 |
| reviewer1 | reviewer123 | 绿色金融管理岗 | 负责审核 |
| auditor1 | auditor123 | 绿色金融复核岗 | 负责最终审批 |

## API接口

### 认证接口

- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息
- `POST /api/auth/logout` - 用户登出

### 绿色金融业务接口

- `GET /api/dashboard` - 获取工作台数据
- `GET /api/tasks/pending` - 获取待办任务
- `GET /api/tasks/completed` - 获取已办任务
- `GET /api/tasks/archived` - 获取办结任务
- `GET /api/tasks/{task_id}` - 获取任务详情
- `POST /api/tasks/{task_id}/complete` - 完成任务
- `POST /api/tasks/{task_id}/withdraw` - 撤回任务
- `GET /api/identifications/{id}/workflow` - 获取工作流历史
- `GET /api/identifications/{id}/workflow-instance` - 获取工作流实例

### 系统管理接口

- `GET /api/system/users` - 获取用户列表
- `POST /api/system/users` - 创建用户
- `PUT /api/system/users/{user_id}` - 更新用户
- `DELETE /api/system/users/{user_id}` - 删除用户
- `GET /api/system/roles` - 获取角色列表
- `POST /api/system/roles` - 创建角色
- `GET /api/system/organizations` - 获取机构列表
- `POST /api/system/organizations` - 创建机构

## 工作流

系统内置绿色认定工作流引擎，实现以下审批流程：

1. **客户经理认定** → 发起绿色贷款认定申请
2. **分行绿色金融管理部门审核** → 分行审核人员审核
3. **一级分行绿色金融最终审批** → 总行复核人员审批
4. **结束** → 流程完成

支持的操作：
- 同意：流转到下一节点
- 不同意：流程结束
- 退回：退回到上一节点
- 撤回：发起人可撤回待处理的任务

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| APP_NAME | 应用名称 | 绿色金融管理系统 |
| APP_VERSION | 应用版本 | 1.0.0 |
| SECRET_KEY | JWT密钥 | - |
| MYSQL_HOST | MySQL主机 | localhost |
| MYSQL_PORT | MySQL端口 | 3306 |
| MYSQL_USER | MySQL用户名 | root |
| MYSQL_PASSWORD | MySQL密码 | - |
| MYSQL_DATABASE | MySQL数据库名 | green_finance |
| CORS_ORIGINS | 允许的跨域来源 | http://localhost:5173 |

## 开发说明

### 添加新的API接口

1. 在 `app/routers/` 目录下创建或编辑路由文件
2. 在 `app/schemas/` 目录下定义Pydantic模式
3. 在 `app/models/` 目录下定义数据模型（如需要）
4. 在 `app/main.py` 中注册路由

### 数据库迁移

当前使用 SQLAlchemy 自动创建表，生产环境建议使用 Alembic 进行数据库迁移管理。

## 注意事项

1. 生产环境请修改 `SECRET_KEY` 为强密码
2. 数据库密码请使用强密码
3. 建议配置 HTTPS
4. 建议配置数据库连接池参数