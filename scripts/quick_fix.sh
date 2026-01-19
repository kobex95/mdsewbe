#!/bin/bash
# 快速修复已安装 mdserver-web 的目录问题

echo "==========================================="
echo "  mdserver-web 目录结构快速修复工具"
echo "==========================================="

# 检查是否在正确的目录
if [ ! -d "/www/server/mdserver-web" ]; then
    echo "错误: 未找到 mdserver-web 安装目录 /www/server/mdserver-web"
    echo "请确保已经正确安装 mdserver-web"
    exit 1
fi

cd /www/server/mdserver-web

# 执行修复脚本
if [ -f "scripts/fix_directories.sh" ]; then
    bash scripts/fix_directories.sh
else
    echo "未找到修复脚本，正在手动创建必要目录..."
    
    # 手动创建目录
    mkdir -p data logs tmp config plugins
    
    # 设置权限
    chmod 755 data logs tmp config
    
    # 创建必要文件
    if [ ! -f "data/default.pl" ]; then
        echo "admin" > data/default.pl
        echo "已创建默认用户名文件"
    fi
    
    if [ ! -f "data/admin_path.pl" ]; then
        echo "/admin" > data/admin_path.pl
        echo "已创建管理路径文件"
    fi
    
    # 创建日志文件
    touch logs/panel_task.log logs/debug.log
    chmod 644 logs/panel_task.log logs/debug.log
    
    # 设置所有者
    chown -R www:www data logs tmp 2>/dev/null || true
fi

echo ""
echo "==========================================="
echo "修复完成！现在尝试启动服务..."
echo "==========================================="

# 尝试启动服务
bash cli.sh start

# 检查服务状态
sleep 3
if ps -ef | grep -v grep | grep "gunicorn -c setting.py app:app" > /dev/null; then
    echo "✅ 服务启动成功！"
    echo "面板访问地址: http://你的服务器IP:7200"
    echo "默认用户名: admin"
    echo "默认密码请查看 data/default.pl 文件"
else
    echo "❌ 服务启动失败，请检查错误信息"
    echo "查看详细日志: tail -f logs/panel_task.log"
fi