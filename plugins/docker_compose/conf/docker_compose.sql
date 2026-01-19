-- Docker Compose管理插件初始化SQL脚本

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    path TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'stopped',
    created_time TEXT,
    updated_time TEXT,
    compose_version TEXT,
    services_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS project_services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    service_name TEXT NOT NULL,
    image TEXT,
    status TEXT DEFAULT 'unknown',
    ports TEXT,
    volumes TEXT,
    environment TEXT,
    created_time TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT,
    description TEXT,
    compose_content TEXT,
    created_time TEXT,
    downloads INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS project_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    service_name TEXT,
    log_level TEXT,
    message TEXT,
    timestamp TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT,
    description TEXT
);

-- 插入默认配置
INSERT OR IGNORE INTO config (key, value, description) VALUES 
('projects_path', '/www/server/docker_compose/projects', '项目存储路径'),
('templates_path', '/www/server/docker_compose/templates', '模板存储路径'),
('docker_compose_path', '/usr/local/bin/docker-compose', 'docker-compose命令路径'),
('auto_start', 'false', '是否开机自启');

-- 插入默认模板
INSERT OR IGNORE INTO templates (name, category, description, compose_content, created_time) VALUES 
('WordPress', 'CMS', 'WordPress博客系统', 
'---\nversion: ''3.8''\nservices:\n  wordpress:\n    image: wordpress:latest\n    ports:\n      - "8080:80"\n    environment:\n      WORDPRESS_DB_HOST: db\n      WORDPRESS_DB_USER: wordpress\n      WORDPRESS_DB_PASSWORD: wordpress\n      WORDPRESS_DB_NAME: wordpress\n    volumes:\n      - wordpress_data:/var/www/html\n    depends_on:\n      - db\n  db:\n    image: mysql:5.7\n    environment:\n      MYSQL_DATABASE: wordpress\n      MYSQL_USER: wordpress\n      MYSQL_PASSWORD: wordpress\n      MYSQL_ROOT_PASSWORD: somewordpress\n    volumes:\n      - db_data:/var/lib/mysql\nvolumes:\n  wordpress_data:\n  db_data:', 
datetime('now'));

INSERT OR IGNORE INTO templates (name, category, description, compose_content, created_time) VALUES 
('NextCloud', 'Storage', '私有云存储系统', 
'---\nversion: ''3.8''\nservices:\n  nextcloud:\n    image: nextcloud:latest\n    ports:\n      - "8081:80"\n    environment:\n      MYSQL_HOST: db\n      MYSQL_USER: nextcloud\n      MYSQL_PASSWORD: nextcloud\n      MYSQL_DATABASE: nextcloud\n    volumes:\n      - nextcloud_html:/var/www/html\n    depends_on:\n      - db\n  db:\n    image: mariadb:10.5\n    environment:\n      MYSQL_ROOT_PASSWORD: nextcloud\n      MYSQL_PASSWORD: nextcloud\n      MYSQL_DATABASE: nextcloud\n      MYSQL_USER: nextcloud\n    volumes:\n      - db_data:/var/lib/mysql\nvolumes:\n  nextcloud_html:\n  db_data:', 
datetime('now'));

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name);
CREATE INDEX IF NOT EXISTS idx_project_services_project_id ON project_services(project_id);
CREATE INDEX IF NOT EXISTS idx_templates_category ON templates(category);
CREATE INDEX IF NOT EXISTS idx_project_logs_project_id ON project_logs(project_id);