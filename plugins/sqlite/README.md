# SQLite 插件

## 简介
这是一个为 mdserver-web 面板开发的 SQLite 数据库管理插件，提供完整的 SQLite 数据库管理功能。

## 功能特性

### 核心功能
- ✅ SQLite 数据库创建、删除管理
- ✅ SQL 查询编辑器
- ✅ 数据库表结构查看
- ✅ 数据库备份功能
- ✅ 查询历史记录
- ✅ 数据库统计信息展示
- ✅ 图形化管理界面

### 管理功能
- **数据库管理**: 创建、删除、查看数据库列表
- **SQL执行**: 在线执行SQL查询语句
- **表结构**: 查看数据库中所有表的结构信息
- **数据备份**: 一键备份数据库文件
- **历史记录**: 查看SQL查询执行历史
- **配置管理**: 插件参数设置

## 安装方式

### 通过面板安装
1. 在 mdserver-web 面板中进入"软件管理"
2. 找到 SQLite 插件并点击安装
3. 安装完成后即可使用

### 手动安装
```bash
# 插件已内置SQLite支持，无需额外安装
# 确保系统中有Python sqlite3模块即可
```

## 使用说明

### 数据库管理
- **创建数据库**: 点击"创建数据库"按钮，输入名称和描述
- **删除数据库**: 在数据库列表中点击对应的删除按钮
- **使用数据库**: 选择数据库进行查询操作

### SQL查询
- 选择目标数据库
- 在查询编辑器中输入SQL语句
- 点击"执行查询"查看结果
- 支持 SELECT、INSERT、UPDATE、DELETE 等所有标准SQL语句

### 表结构查看
- 在数据库管理页面点击"查看表"
- 显示所有表的名称、列数、行数等信息

### 备份管理
- 选择要备份的数据库
- 点击"立即备份"生成备份文件
- 备份文件保存在 `/www/server/sqlite/backups/` 目录

## 目录结构
```
sqlite/
├── info.json           # 插件配置信息
├── index.py            # 插件核心逻辑
├── index.html          # 前端界面
├── conf/               # 配置文件目录
│   └── sqlite.sql      # 插件数据库初始化脚本
├── js/                 # 前端JavaScript
│   └── sqlite.js       # 插件交互逻辑
└── README.md           # 使用说明
```

## API 接口

插件提供以下命令行接口：

```bash
# 服务控制
python3 index.py status          # 查看状态
python3 index.py start           # 启动插件
python3 index.py stop            # 停止插件
python3 index.py restart         # 重启插件

# 数据库管理
python3 index.py get_databases   # 获取数据库列表
python3 index.py add_database    # 添加数据库
python3 index.py delete_database # 删除数据库

# 查询操作
python3 index.py execute_query   # 执行SQL查询
python3 index.py get_tables      # 获取表结构

# 备份管理
python3 index.py backup_database # 备份数据库
python3 index.py get_history     # 查询历史

# 配置管理
python3 index.py get_config      # 获取配置
python3 index.py set_config      # 设置配置
```

## 数据库存储结构

插件使用自己的SQLite数据库存储管理信息：

### 主要表结构
- **databases**: 存储管理的数据库信息
- **database_tables**: 存储表结构信息  
- **queries_history**: 存储查询历史记录
- **config**: 存储插件配置参数

## 注意事项

1. **文件权限**: 确保 `/www/server/sqlite/` 目录有适当的读写权限
2. **磁盘空间**: 监控数据库文件大小，避免占用过多磁盘空间
3. **备份策略**: 建议定期备份重要数据库
4. **SQL安全**: 生产环境中注意SQL注入防护

## 故障排除

### 常见问题

**Q: 无法创建数据库**
A: 检查目录权限，确保 `/www/server/sqlite/databases/` 目录可写

**Q: SQL查询执行失败**  
A: 检查SQL语法是否正确，查看错误信息

**Q: 备份功能异常**
A: 确认备份目录是否存在且可写

**Q: 插件无法启动**
A: 检查Python环境是否包含sqlite3模块

## 开发说明

该插件遵循 mdserver-web 插件开发规范：
- 使用标准的插件目录结构
- 实现统一的命令行接口
- 提供完整的 Web 管理界面
- 基于项目内置的SQLite数据库操作类

如需二次开发，请参考现有代码结构和命名规范。