# 绿色金融管理系统

面向2030年碳达峰、2060年碳中和目标的银行绿色贷款管理系统，支持绿色贷款认定、审批、统计分析的全流程管理。

## 项目简介

本系统是为银行业务设计的绿色金融管理平台，旨在支持国家"双碳"目标的实现。系统提供完整的绿色贷款认定工作流，包括客户经理发起、分行审核、总行审批等环节，同时提供丰富的数据统计和分析功能。

## 技术架构

### 前端技术栈
- **框架**: Vue 3.3.11
- **UI组件**: Element Plus 2.4.4
- **构建工具**: Vite 5.0.8
- **路由**: Vue Router 4.2.5
- **状态管理**: Pinia 2.1.7
- **HTTP客户端**: Axios 1.6.2

### 后端技术栈
- **框架**: FastAPI 0.104.1
- **数据库**: MySQL 8.0+
- **ORM**: SQLAlchemy 2.0.23
- **认证**: JWT (python-jose)
- **密码加密**: bcrypt

### 工作流引擎
- 内置绿色认定工作流引擎
- 支持流程节点配置和流转
- 支持同意、退回、撤回等操作

## 功能模块

### 1. 用户认证
- 用户登录/登出
- JWT Token认证
- 权限管理

### 2. 工作台
- 绿色贷款核心指标展示
- 待办事项统计
- 数据可视化

### 3. 绿色认定
- **待办任务**: 查看和办理待处理任务
- **已办任务**: 查看已处理任务
- **办结任务**: 查询已办结任务
- **综合查询**: 高级查询功能

### 4. 任务办理
- 查看任务详情
- 审批任务（同意/不同意/退回）
- 填写审批意见
- 撤回任务
- 流程跟踪

### 5. 系统管理
- **用户管理**: 创建、编辑、删除用户
- **角色管理**: 管理系统角色
- **机构管理**: 管理组织机构

## 项目结构

```
gfms/
├── backend/               # 后端服务
│   ├── app/
│   │   ├── models/       # 数据模型
│   │   ├── schemas/      # Pydantic模式
│   │   ├── routers/      # API路由
│   │   ├── services/     # 业务逻辑
│   │   ├── config.py     # 配置文件
│   │   ├── database.py   # 数据库连接
│   │   └── main.py       # 应用入口
│   ├── init_db.py        # 数据库初始化脚本
│   ├── requirements.txt  # Python依赖
│   └── .env.example      # 环境变量示例
├── frontend/             # 前端应用
│   ├── src/
│   │   ├── api/          # API接口
│   │   ├── assets/       # 静态资源
│   │   ├── components/   # 公共组件
│   │   ├── router/       # 路由配置
│   │   ├── store/        # 状态管理
│   │   ├── views/        # 页面组件
│   │   ├── App.vue       # 根组件
│   │   └── main.js       # 应用入口
│   ├── index.html        # HTML模板
│   ├── package.json      # 项目配置
│   └── vite.config.js    # Vite配置
└── README.md             # 项目说明
```

## 快速开始

### 环境要求

- Node.js 16+
- Python 3.9+
- MySQL 8.0+

### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置数据库

复制 `.env.example` 为 `.env` 并修改数据库配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件中的数据库连接信息。

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

### 5. 启动后端服务

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将在 `http://localhost:8000` 启动。

### 6. 安装前端依赖

```bash
cd frontend
npm install
```

### 7. 启动前端应用

```bash
npm run dev
```

前端应用将在 `http://localhost:5173` 启动。

### 8. 访问系统

打开浏览器访问 `http://localhost:5173`

## 默认账号

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| admin | admin123 | 超级管理员 | 拥有所有权限 |
| manager1 | manager123 | 客户经理 | 负责发起绿色贷款认定 |
| reviewer1 | reviewer123 | 绿色金融管理岗 | 负责审核 |
| auditor1 | auditor123 | 绿色金融复核岗 | 负责最终审批 |

## 工作流说明

系统内置绿色认定工作流，流程如下：

1. **客户经理认定**: 客户经理发起绿色贷款认定申请，填写相关信息
2. **分行绿色金融管理部门审核**: 分行审核人员对申请进行审核
3. **一级分行绿色金融最终审批**: 总行复核人员进行最终审批
4. **结束**: 流程完成，生成认定结果

支持的操作：
- **同意**: 流转到下一节点
- **不同意**: 流程结束，认定失败
- **退回**: 退回到上一节点重新处理
- **撤回**: 发起人可撤回待处理的任务

## API文档

后端服务启动后，可访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 主要特性

### 业务特性
- ✅ 完整的绿色贷款认定工作流
- ✅ 多角色权限管理
- ✅ 流程跟踪可视化
- ✅ 任务审批历史记录
- ✅ 丰富的数据统计指标

### 技术特性
- ✅ 前后端分离架构
- ✅ RESTful API设计
- ✅ JWT Token认证
- ✅ 响应式UI设计
- ✅ 数据库ORM映射
- ✅ 环境变量配置

## 开发说明

### 后端开发

参考 `backend/README.md` 了解后端开发详情。

### 前端开发

参考 `frontend/README.md` 了解前端开发详情。

## 部署说明

### 生产环境配置

1. 修改后端 `.env` 文件：
   - 修改 `SECRET_KEY` 为强密码
   - 配置生产数据库连接
   - 配置生产环境CORS

2. 前端构建：
   ```bash
   cd frontend
   npm run build
   ```

3. 使用 Nginx 或其他Web服务器部署前端静态文件

4. 使用 Gunicorn 或 Uvicorn 部署后端服务

## 注意事项

1. 生产环境请务必修改默认密码和密钥
2. 数据库密码请使用强密码
3. 建议配置HTTPS
4. 建议配置数据库备份策略
5. 建议配置日志记录

## 许可证

本项目仅供学习和参考使用。

## 联系方式

如有问题或建议，请联系项目维护者。