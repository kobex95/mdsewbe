# Docker Compose 管理插件

## 简介
这是一个为 mdserver-web 面板开发的 Docker Compose 项目管理插件，提供完整的容器化应用管理功能。

## 功能特性

### 核心功能
- ✅ Docker Compose 项目创建、删除管理
- ✅ 项目模板库（WordPress、NextCloud等）
- ✅ 服务启动/停止控制
- ✅ 实时服务状态监控
- ✅ 项目日志查看
- ✅ 图形化管理界面

### 管理功能
- **项目管理**: 创建、删除、启动、停止Docker Compose项目
- **模板中心**: 预设常用应用模板，一键部署
- **服务监控**: 实时查看各服务运行状态
- **日志管理**: 集中查看项目和服务日志
- **配置管理**: 插件参数和路径设置

## 环境要求

### 系统依赖
- Docker Engine 18.06+
- Docker Compose 1.22+
- Python 3.6+

### 安装检查
```bash
# 检查Docker
docker --version

# 检查Docker Compose
docker-compose --version
```

## 安装方式

### 通过面板安装
1. 确保系统已安装Docker和Docker Compose
2. 在 mdserver-web 面板中进入"软件管理"
3. 找到 Docker Compose 插件并点击安装
4. 安装完成后即可使用

### 手动安装
```bash
# 确保Docker环境就绪
systemctl start docker
systemctl enable docker

# 插件会自动检测环境依赖
```

## 使用说明

### 项目管理
- **创建项目**: 点击"创建项目"，可选择模板或从空白开始
- **启动/停止**: 在项目列表中控制项目运行状态
- **删除项目**: 彻底删除项目及其所有容器和数据

### 模板使用
- **WordPress**: 一键部署博客系统
- **NextCloud**: 私有云存储解决方案
- 支持自定义模板扩展

### 服务监控
- 实时显示各服务运行状态
- 查看服务配置信息
- 监控项目整体健康状况

### 日志查看
- 集中查看项目日志
- 按服务筛选日志
- 实时日志滚动显示

## 目录结构
```
docker_compose/
├── info.json           # 插件配置信息
├── index.py            # 插件核心逻辑
├── index.html          # 前端界面
├── README.md           # 使用说明
├── conf/               # 配置文件目录
│   └── docker_compose.sql  # 数据库初始化脚本
├── js/                 # 前端JavaScript
│   └── docker_compose.js   # 交互逻辑
└── templates/          # 项目模板目录（预留）
```

## API 接口

插件提供以下命令行接口：

```bash
# 服务控制
python3 index.py status          # 查看状态
python3 index.py start           # 启动插件
python3 index.py stop            # 停止插件
python3 index.py restart         # 重启插件

# 项目管理
python3 index.py get_projects    # 获取项目列表
python3 index.py create_project  # 创建项目
python3 index.py delete_project  # 删除项目
python3 index.py start_project   # 启动项目
python3 index.py stop_project    # 停止项目

# 服务管理
python3 index.py get_services    # 获取服务列表

# 模板管理
python3 index.py get_templates   # 获取模板列表

# 日志管理
python3 index.py get_logs        # 获取项目日志

# 配置管理
python3 index.py get_config      # 获取配置
python3 index.py set_config      # 设置配置
```

## 数据库存储结构

插件使用SQLite数据库存储管理信息：

### 主要表结构
- **projects**: 存储项目基本信息
- **project_services**: 存储项目服务信息
- **templates**: 存储项目模板
- **project_logs**: 存储项目日志
- **config**: 存储插件配置参数

## 注意事项

1. **权限要求**: 确保运行用户有Docker操作权限
2. **磁盘空间**: 监控容器镜像和数据卷占用空间
3. **网络配置**: 注意端口映射和网络冲突
4. **数据备份**: 重要项目建议定期备份compose文件

## 故障排除

### 常见问题

**Q: 插件显示"docker-compose命令不可用"**
A: 确认已安装Docker Compose，检查命令路径配置

**Q: 项目启动失败**
A: 检查docker-compose.yml语法，查看具体错误日志

**Q: 服务状态显示不准确**
A: 手动刷新项目列表，或检查Docker守护进程状态

**Q: 权限不足错误**
A: 确保运行用户在docker用户组中

## 开发说明

该插件遵循 mdserver-web 插件开发规范：
- 使用标准的插件目录结构
- 实现统一的命令行接口
- 提供完整的 Web 管理界面
- 基于项目内置的数据库操作类

如需二次开发，请参考现有代码结构和命名规范。

## 模板扩展

支持自定义模板，格式如下：
```yaml
---
version: '3.8'
services:
  your_service:
    image: your_image:tag
    # 其他配置...
```

将模板文件放入templates目录即可在面板中使用。