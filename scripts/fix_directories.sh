#!/bin/bash
# 修复 mdserver-web 目录结构问题的脚本

echo "正在修复 mdserver-web 目录结构..."

# 创建必要的目录结构
mkdir -p /www/server/mdserver-web/data
mkdir -p /www/server/mdserver-web/logs
mkdir -p /www/server/mdserver-web/tmp
mkdir -p /www/server/mdserver-web/config
mkdir -p /www/server/mdserver-web/plugins

# 设置正确的权限
chmod 755 /www/server/mdserver-web/data
chmod 755 /www/server/mdserver-web/logs
chmod 755 /www/server/mdserver-web/tmp
chmod 755 /www/server/mdserver-web/config

# 创建必要的配置文件
if [ ! -f /www/server/mdserver-web/data/default.pl ]; then
    echo "admin" > /www/server/mdserver-web/data/default.pl
    echo "已创建默认管理员用户名文件"
fi

if [ ! -f /www/server/mdserver-web/data/admin_path.pl ]; then
    echo "/admin" > /www/server/mdserver-web/data/admin_path.pl
    echo "已创建默认管理路径文件"
fi

# 创建日志文件
touch /www/server/mdserver-web/logs/panel_task.log
touch /www/server/mdserver-web/logs/debug.log
chmod 644 /www/server/mdserver-web/logs/panel_task.log
chmod 644 /www/server/mdserver-web/logs/debug.log

# 检查 www 用户是否存在，不存在则创建
if ! id www &>/dev/null; then
    groupadd www 2>/dev/null || true
    useradd -g www -s /usr/sbin/nologin www 2>/dev/null || true
    echo "已创建 www 用户"
fi

# 设置目录所有者
chown -R www:www /www/server/mdserver-web/data 2>/dev/null || true
chown -R www:www /www/server/mdserver-web/logs 2>/dev/null || true
chown -R www:www /www/server/mdserver-web/tmp 2>/dev/null || true

echo "目录结构修复完成！"
echo "现在可以尝试重新启动服务："
echo "cd /www/server/mdserver-web && bash cli.sh start"