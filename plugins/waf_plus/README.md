# Web防火墙增强版 (WAF Plus)

## 🛡️ 简介

WAF Plus是基于原生OP防火墙的全新升级版本，采用了现代化的设计理念和技术架构，为您的Web应用提供更强大、更智能的安全防护。

## 🌟 主要特性

### 🔥 现代化界面
- 响应式设计，完美适配各种设备
- 暗色主题支持，保护眼睛健康
- 直观的操作体验，降低学习成本
- 实时数据可视化展示

### 🛡️ 增强安全防护
- **智能威胁检测**: 基于机器学习的异常流量识别
- **多维度防护**: SQL注入、XSS、RCE等全方位保护
- **实时IP情报**: 集成全球威胁情报数据库
- **自适应规则**: 根据攻击模式自动调整防护策略

### 📊 实时监控告警
- **仪表板概览**: 一站式安全态势感知
- **攻击趋势分析**: 可视化展示攻击模式变化
- **实时日志**: 流式日志查看和搜索
- **智能告警**: 多渠道告警通知机制

### ⚡ 高性能架构
- **异步处理**: 非阻塞式日志记录
- **缓存优化**: 智能缓存策略提升性能
- **资源隔离**: 独立进程确保稳定性
- **负载均衡**: 支持集群部署

## 🚀 快速开始

### 安装步骤

```bash
# 进入插件目录
cd /www/server/mdserver-web/plugins

# 下载插件
git clone https://github.com/your-repo/waf_plus.git

# 安装插件
cd waf_plus && bash install.sh install

# 启动服务
python3 index.py start
```

### 基本配置

1. 在面板中找到"WAF Plus"插件
2. 点击进入管理界面
3. 根据向导完成基础配置
4. 启用防护规则

## 📋 功能详解

### 仪表板
提供全面的安全态势概览：
- 实时攻击拦截统计
- 系统性能监控
- 威胁情报展示
- 攻击趋势分析

### 规则管理
灵活的规则配置系统：
```
- SQL注入防护
- XSS攻击防御  
- 命令执行拦截
- 文件上传控制
- 路径遍历防护
- 自定义规则
```

### 日志分析
强大的日志管理和分析功能：
- 实时日志流
- 多维度搜索
- 攻击溯源分析
- 日志导出功能

### 威胁情报
集成的威胁情报系统：
- 恶意IP识别
- 攻击来源分析
- 威胁等级评估
- 自动更新机制

## 🔧 高级配置

### 性能调优

```json
{
  "rate_limit": 2000,
  "cache_size": 100,
  "worker_processes": 4,
  "connection_timeout": 30
}
```

### 自定义规则示例

```lua
-- 自定义SQL注入规则
{
  "name": "Advanced SQL Injection",
  "type": "sql_injection",
  "pattern": "(union|select|insert|delete|update)[\\s]+(select|into|from)",
  "action": "block",
  "priority": 5
}
```

### 告警配置

```yaml
alert_channels:
  - type: email
    recipients: ["admin@example.com"]
    threshold: high
  
  - type: webhook
    url: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    events: ["attack_detected", "threshold_exceeded"]
```

## 📊 API接口

### 获取仪表板数据
```bash
curl -X POST http://localhost:7200/plugins/run \
  -d 'name=waf_plus&func=dashboard'
```

### 查询攻击日志
```bash
curl -X POST http://localhost:7200/plugins/run \
  -d 'name=waf_plus&func=logs&page=1&page_size=20&search=hack'
```

### 管理防护规则
```bash
# 添加规则
curl -X POST http://localhost:7200/plugins/run \
  -d 'name=waf_plus&func=add_rule&args={"name":"test","type":"xss","pattern":"<script>","action":"block"}'

# 删除规则
curl -X POST http://localhost:7200/plugins/run \
  -d 'name=waf_plus&func=delete_rule&args={"id":1}'
```

## 🛠️ 故障排除

### 常见问题

**Q: WAF影响网站性能怎么办？**
A: 可以调整以下配置：
- 降低日志级别
- 增加缓存大小
- 优化规则优先级
- 启用学习模式

**Q: 如何排除误报？**
A: 
1. 查看攻击详情日志
2. 调整相应规则的严格程度
3. 将正常请求加入白名单
4. 使用学习模式逐步优化

**Q: 威胁情报更新失败？**
A:
1. 检查网络连接
2. 验证API密钥有效性
3. 查看系统时间是否正确
4. 检查防火墙设置

### 日志位置
```
/www/server/waf_plus/logs/waf.db          # 数据库文件
/www/server/waf_plus/logs/access.log      # 访问日志
/www/server/waf_plus/logs/error.log       # 错误日志
/www/server/waf_plus/config/             # 配置文件
```

## 🔄 升级指南

### 从OP防火墙迁移

```bash
# 备份原配置
cp -r /www/server/op_waf /backup/

# 安装WAF Plus
cd /www/server/mdserver-web/plugins
git clone https://github.com/your-repo/waf_plus.git

# 迁移规则配置
python3 waf_plus/tools/migrate_rules.py

# 启动新服务
cd waf_plus && bash install.sh install
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发环境搭建
```bash
# 克隆仓库
git clone https://github.com/your-repo/waf_plus.git

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python3 dev_server.py
```

### 代码规范
- 遵循PEP8编码规范
- 使用类型注解
- 编写单元测试
- 提供API文档

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🔐 安全声明

本项目遵循负责任的漏洞披露原则。如发现安全问题，请通过以下方式联系我们：
- 邮箱: security@example.com
- 加密通信: PGP Key ID: XXXXXXXX

---

**WAF Plus - 让Web安全更简单！**