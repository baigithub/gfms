# Docker MySQL 配置说明

## 快速启动

### 1. 启动MySQL容器

```bash
# 使用启动脚本（推荐）
chmod +x docker-start.sh
./docker-start.sh

# 或直接使用docker-compose
docker-compose up -d mysql
```

### 2. 验证MySQL是否启动

```bash
# 检查容器状态
docker ps | grep gfms-mysql

# 查看日志
docker logs gfms-mysql

# 测试连接
docker exec -it gfms-mysql mysql -u gfms_user -pgfms_password green_finance
```

### 3. 启动后端服务

```bash
cd backend

# 设置Docker环境标识
export IS_DOCKER=true

# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 启动前端服务

```bash
cd frontend
npm install
npm run dev
```

## 数据库连接信息

| 配置项 | 值 |
|--------|-----|
| 主机 | localhost (外部) / mysql (Docker内部) |
| 端口 | 3306 |
| 数据库 | green_finance |
| 用户 | gfms_user |
| 密码 | gfms_password |
| Root密码 | root123456 |

## 环境变量配置

后端会根据 `IS_DOCKER` 环境变量自动选择数据库连接方式：

### Docker环境
```bash
export IS_DOCKER=true
```
使用配置：
- MYSQL_HOST=mysql
- MYSQL_USER=gfms_user
- MYSQL_PASSWORD=gfms_password

### 本地开发环境
```bash
export IS_DOCKER=false
```
使用配置：
- MYSQL_HOST=localhost
- MYSQL_USER=gfms_user
- MYSQL_PASSWORD=gfms_password

如果需要连接本地MySQL，可以设置本地覆盖变量：
```bash
export MYSQL_HOST_LOCAL=localhost
export MYSQL_USER_LOCAL=root
export MYSQL_PASSWORD_LOCAL=your_password
```

## 常用命令

### 查看MySQL日志
```bash
docker logs -f gfms-mysql
```

### 进入MySQL容器
```bash
docker exec -it gfms-mysql bash
```

### 备份数据库
```bash
docker exec gfms-mysql mysqldump -u gfms_user -pgfms_password green_finance > backup.sql
```

### 恢复数据库
```bash
docker exec -i gfms-mysql mysql -u gfms_user -pgfms_password green_finance < backup.sql
```

### 重启MySQL
```bash
docker-compose restart mysql
```

### 停止所有容器
```bash
docker-compose down
```

### 删除所有数据（危险！）
```bash
docker-compose down -v
```

## 初始化数据

数据库初始化脚本 `init.sql` 会在容器首次启动时自动执行，创建：

- 数据表结构
- 默认角色（超级管理员、客户经理、绿色金融管理岗、绿色金融复核岗）
- 默认机构（总行、分行、支行）
- 默认用户账号

## 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | 123456 | 超级管理员 |
| manager1 | 123456 | 客户经理 |
| reviewer1 | 123456 | 绿色金融管理岗 |
| auditor1 | 123456 | 绿色金融复核岗 |

## 故障排查

### MySQL连接失败

1. 检查MySQL是否启动：
```bash
docker ps | grep gfms-mysql
```

2. 查看MySQL日志：
```bash
docker logs gfms-mysql
```

3. 测试连接：
```bash
docker exec gfms-mysql mysql -u gfms_user -pgfms_password green_finance -e "SELECT 1"
```

### 数据持久化

MySQL数据存储在Docker卷 `mysql_data` 中，即使容器删除数据也不会丢失。

查看数据卷：
```bash
docker volume ls | grep mysql_data
```

删除数据卷（会清空所有数据）：
```bash
docker-compose down -v
```

### 端口冲突

如果3306端口被占用，可以修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "3307:3306"  # 将3306映射到主机的3307
```

然后更新后端配置：
```bash
export MYSQL_PORT=3307
```