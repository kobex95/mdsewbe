-- Web防火墙增强版数据库初始化脚本

-- 攻击日志表
CREATE TABLE IF NOT EXISTS attack_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT NOT NULL,
    rule_name TEXT NOT NULL,
    uri TEXT,
    method TEXT,
    user_agent TEXT,
    referer TEXT,
    attack_time INTEGER NOT NULL,
    action_taken TEXT,
    risk_level TEXT DEFAULT 'medium',
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 规则表
CREATE TABLE IF NOT EXISTS rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL, -- sql_injection, xss, rce, file_upload, etc.
    pattern TEXT NOT NULL,
    action TEXT NOT NULL, -- block, log, redirect, challenge
    priority INTEGER DEFAULT 100,
    status TEXT DEFAULT 'enabled', -- enabled, disabled
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- IP黑白名单表
CREATE TABLE IF NOT EXISTS ip_lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT NOT NULL,
    list_type TEXT NOT NULL, -- whitelist, blacklist
    reason TEXT,
    expires_at INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 统计数据表
CREATE TABLE IF NOT EXISTS statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stat_date DATE NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stat_date, metric_name)
);

-- 威胁情报表
CREATE TABLE IF NOT EXISTS threat_intel (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT NOT NULL,
    threat_type TEXT NOT NULL,
    confidence INTEGER,
    source TEXT,
    first_seen INTEGER,
    last_seen INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 系统配置表
CREATE TABLE IF NOT EXISTS configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key TEXT NOT NULL UNIQUE,
    config_value TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_attack_logs_ip ON attack_logs(ip);
CREATE INDEX IF NOT EXISTS idx_attack_logs_time ON attack_logs(attack_time);
CREATE INDEX IF NOT EXISTS idx_attack_logs_rule ON attack_logs(rule_name);
CREATE INDEX IF NOT EXISTS idx_rules_priority ON rules(priority);
CREATE INDEX IF NOT EXISTS idx_rules_status ON rules(status);
CREATE INDEX IF NOT EXISTS idx_ip_lists_type ON ip_lists(list_type);
CREATE INDEX IF NOT EXISTS idx_threat_intel_ip ON threat_intel(ip);

-- 插入默认规则
INSERT OR IGNORE INTO rules (name, type, pattern, action, priority, status, description) VALUES
('SQL Injection Basic', 'sql_injection', '(union|select|insert|delete|update|drop|create|alter|exec|execute)[\s]+', 'block', 10, 'enabled', '基础SQL注入防护'),
('XSS Script Tag', 'xss', '<script[^>]*>.*?</script>', 'block', 20, 'enabled', 'XSS脚本标签防护'),
('Command Execution', 'rce', '(eval|assert|system|exec|shell_exec|passthru|proc_open)[\s\(]', 'block', 15, 'enabled', '命令执行防护'),
('File Upload PHP', 'file_upload', '\.(php|php3|php4|php5|phtml|phar)$', 'block', 25, 'enabled', 'PHP文件上传防护'),
('Admin Path Access', 'path_traversal', '(admin|manage|login)\.(php|asp|jsp)', 'log', 30, 'enabled', '管理路径访问记录');

-- 插入默认配置
INSERT OR IGNORE INTO configs (config_key, config_value, description) VALUES
('waf_enabled', 'true', 'WAF总开关'),
('log_level', 'info', '日志级别'),
('block_action', '403', '拦截动作'),
('rate_limit', '1000', '速率限制(QPS)'),
('learning_mode', 'false', '学习模式');