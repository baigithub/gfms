# 绿色金融管理系统 - 前端

基于 Vue 3 + Element Plus + Vite 的绿色金融管理系统前端应用。

## 技术栈

- **框架**: Vue 3.3.11
- **构建工具**: Vite 5.0.8
- **UI组件**: Element Plus 2.4.4
- **路由**: Vue Router 4.2.5
- **状态管理**: Pinia 2.1.7
- **HTTP客户端**: Axios 1.6.2
- **图表**: ECharts 5.4.3
- **日期处理**: Day.js 1.11.10

## 项目结构

```
frontend/
├── src/
│   ├── api/             # API接口
│   │   ├── index.js     # Axios配置
│   │   ├── auth.js      # 认证接口
│   │   ├── green_finance.js  # 绿色金融业务接口
│   │   └── system.js    # 系统管理接口
│   ├── assets/          # 静态资源
│   ├── components/      # 公共组件
│   ├── router/          # 路由配置
│   │   └── index.js
│   ├── store/           # 状态管理
│   │   └── auth.js      # 认证状态
│   ├── views/           # 页面组件
│   │   ├── Login.vue    # 登录页
│   │   ├── Layout.vue   # 布局页
│   │   ├── Dashboard.vue  # 工作台
│   │   ├── TaskPending.vue  # 待办任务
│   │   ├── TaskCompleted.vue  # 已办任务
│   │   ├── TaskArchived.vue  # 办结任务
│   │   ├── TaskQuery.vue  # 综合查询
│   │   ├── System.vue   # 系统管理
│   │   ├── SystemUser.vue   # 用户管理
│   │   ├── SystemRole.vue   # 角色管理
│   │   └── SystemOrg.vue    # 机构管理
│   ├── App.vue          # 根组件
│   └── main.js          # 应用入口
├── index.html           # HTML模板
├── package.json         # 项目配置
└── vite.config.js       # Vite配置
```

## 安装与运行

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 开发模式

```bash
npm run dev
```

应用将在 `http://localhost:5173` 启动。

### 3. 生产构建

```bash
npm run build
```

构建产物将输出到 `dist/` 目录。

### 4. 预览生产构建

```bash
npm run preview
```

## 功能模块

### 1. 登录页

- 用户名/密码登录
- 验证码验证
- 自动保存登录状态

### 2. 工作台

- 绿色贷款核心指标展示
- 绿色投资、租赁、理财、承销子类指标
- 待办事项列表
- 数据可视化展示

### 3. 绿色认定

- **待办任务**: 查看和办理待处理的任务
- **已办任务**: 查看已处理的任务
- **办结任务**: 查询已办结的任务
- **综合查询**: 高级查询功能（开发中）

### 4. 系统管理

- **用户管理**: 创建、编辑、删除用户
- **角色管理**: 查看角色列表
- **机构管理**: 查看机构列表

## 主要功能

### 任务办理

1. 查看任务详情（业务信息、审批记录、流程跟踪）
2. 审批任务（同意/不同意/退回）
3. 填写审批意见和原因
4. 撤回任务

### 流程跟踪

- 可视化展示工作流进度
- 显示各节点的审批人和审批结果
- 查看完整的审批历史

### 查询功能

- 多条件组合查询
- 日期范围筛选
- 分页显示

## 配置说明

### API代理

在 `vite.config.js` 中配置了API代理：

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

开发环境下的API请求会自动代理到后端服务。

### 路由配置

路由配置在 `src/router/index.js` 中：

- `/login` - 登录页
- `/dashboard` - 工作台
- `/green-identify/*` - 绿色认定模块
- `/system/*` - 系统管理模块

### 状态管理

使用 Pinia 进行状态管理，主要模块：

- `auth` - 认证状态（token、用户信息）

## 样式规范

- 主色调：绿色 (#2E8B57)
- 辅助色：浅绿色 (#4CAF50)
- 警告色：橙色 (#FF9800)
- 成功色：绿色 (#67C23A)
- 危险色：红色 (#F56C6C)

## 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 超级管理员 |
| manager1 | manager123 | 客户经理 |
| reviewer1 | reviewer123 | 绿色金融管理岗 |
| auditor1 | auditor123 | 绿色金融复核岗 |

## 开发说明

### 添加新页面

1. 在 `src/views/` 目录下创建页面组件
2. 在 `src/router/index.js` 中添加路由配置
3. 如需要，在 `src/api/` 中添加API接口

### 添加API接口

在 `src/api/` 目录下创建接口文件：

```javascript
import request from './index'

export const getData = (params) => {
  return request({
    url: '/api/endpoint',
    method: 'get',
    params
  })
}
```

### 组件开发规范

- 使用 Vue 3 Composition API
- 使用 `<script setup>` 语法
- 组件名使用 PascalCase
- 样式使用 scoped CSS

## 注意事项

1. 所有API请求都会自动携带JWT token
2. token过期会自动跳转到登录页
3. 使用 Element Plus 组件库保持UI一致性
4. 日期格式化使用 Day.js
5. 金额格式化使用 toLocaleString 方法

## 浏览器支持

- Chrome (推荐)
- Edge
- Firefox
- Safari

最低版本要求：现代浏览器（ES6+支持）