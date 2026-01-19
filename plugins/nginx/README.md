# Nginx 插件

## 简介
这是一个为 mdserver-web 面板开发的 Nginx 服务器管理插件，提供完整的 Nginx 服务管理功能。

## 功能特性

### 核心功能
- ✅ Nginx 服务启停管理
- ✅ 配置文件在线编辑
- ✅ 虚拟主机管理
- ✅ 运行状态监控
- ✅ 日志查看（错误日志、访问日志）
- ✅ 配置文件语法检查
- ✅ 性能调优建议

### 支持版本
- Nginx 1.20.2
- Nginx 1.22.1  
- Nginx 1.24.0
- Nginx 1.25.3

## 安装方式

### 通过面板安装
1. 在 mdserver-web 面板中进入"软件管理"
2. 找到 Nginx 插件并点击安装
3. 选择需要的版本进行安装

### 手动安装
```bash
# 进入插件目录
cd /www/server/mdserver-web/plugins/nginx

# 安装指定版本
bash install.sh install 1.24.0
```

## 使用说明

### 服务管理
- **启动/停止**: 控制 Nginx 服务的启停
- **重启**: 重启 Nginx 服务
- **重载**: 重新加载配置文件（不停止服务）

### 配置管理
- **配置文件编辑**: 在线编辑 nginx.conf 主配置文件
- **语法检查**: 在保存前检查配置文件语法
- **自动备份**: 修改配置时自动创建备份文件

### 监控功能
- **运行状态**: 显示进程状态、版本信息、监听端口等
- **错误日志**: 实时查看错误日志
- **访问日志**: 实时查看访问日志
- **虚拟主机**: 查看已配置的虚拟主机列表

## 目录结构
```
nginx/
├── info.json           # 插件配置信息
├── install.sh          # 安装脚本
├── index.py            # 插件核心逻辑
├── index.html          # 前端界面
├── conf/               # 配置文件目录
├── init.d/             # 启动脚本
│   └── nginx.init      # systemd启动脚本模板
├── js/                 # 前端JavaScript
│   └── nginx.js        # 插件交互逻辑
└── versions/           # 版本特定文件（预留）
```

## API 接口

插件提供以下命令行接口：

```bash
# 服务控制
python3 index.py status      # 查看状态
python3 index.py start       # 启动服务
python3 index.py stop        # 停止服务
python3 index.py restart     # 重启服务
python3 index.py reload      # 重载配置

# 系统集成
python3 index.py initd_status    # 自启动状态
python3 index.py initd_install   # 设置自启动
python3 index.py initd_uninstall # 取消自启动

# 信息获取
python3 index.py run_info        # 运行状态信息
python3 index.py error_logs      # 错误日志
python3 index.py access_logs     # 访问日志
python3 index.py get_vhosts      # 虚拟主机列表
python3 index.py get_config      # 获取配置文件
python3 index.py test_config     # 测试配置语法
```

## 注意事项

1. **权限要求**: 需要 root 权限进行安装和管理
2. **依赖环境**: 需要 gcc、make 等编译工具
3. **端口冲突**: 确保 80、443 等端口未被占用
4. **配置备份**: 修改重要配置前建议手动备份

## 故障排除

### 常见问题

**Q: 安装失败**
A: 检查网络连接和系统依赖，确保有足够磁盘空间

**Q: 启动失败**  
A: 检查配置文件语法，查看错误日志定位问题

**Q: 端口被占用**
A: 修改配置文件中的 listen 端口，或停止占用端口的服务

**Q: 权限不足**
A: 确保以 root 用户执行相关操作

## 开发说明

该插件遵循 mdserver-web 插件开发规范：
- 使用标准的插件目录结构
- 实现统一的命令行接口
- 提供完整的 Web 管理界面
- 支持多版本管理

如需二次开发，请参考现有代码结构和命名规范。