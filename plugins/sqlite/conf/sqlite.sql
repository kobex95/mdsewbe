-- SQLite数据库管理插件初始化SQL脚本

CREATE TABLE IF NOT EXISTS databases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    path TEXT NOT NULL,
    size INTEGER DEFAULT 0,
    tables_count INTEGER DEFAULT 0,
    created_time TEXT,
    updated_time TEXT,
    description TEXT,
    status TEXT DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS database_tables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    db_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    rows_count INTEGER DEFAULT 0,
    created_time TEXT,
    updated_time TEXT,
    FOREIGN KEY (db_id) REFERENCES databases(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS queries_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    db_id INTEGER NOT NULL,
    query_text TEXT NOT NULL,
    execution_time REAL,
    result_rows INTEGER,
    executed_time TEXT,
    FOREIGN KEY (db_id) REFERENCES databases(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT,
    description TEXT
);

-- 插入默认配置
INSERT OR IGNORE INTO config (key, value, description) VALUES 
('default_path', '/www/server/sqlite/databases', '默认数据库存储路径'),
('max_db_size', '1073741824', '单个数据库最大大小(字节)'),
('backup_path', '/www/server/sqlite/backups', '备份文件存储路径');

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_databases_name ON databases(name);
CREATE INDEX IF NOT EXISTS idx_database_tables_db_id ON database_tables(db_id);
CREATE INDEX IF NOT EXISTS idx_queries_history_db_id ON queries_history(db_id);