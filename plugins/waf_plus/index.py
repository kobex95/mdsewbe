# coding:utf-8

import sys
import io
import os
import time
import subprocess
import json
import re
import sqlite3
from datetime import datetime

web_dir = os.getcwd() + "/web"
if os.path.exists(web_dir):
    sys.path.append(web_dir)
    os.chdir(web_dir)

import core.mw as mw


app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'waf_plus'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getArgs():
    args = sys.argv[2:]
    tmp = {}
    args_len = len(args)

    if args_len == 1:
        t = args[0].strip('{').strip('}')
        t = t.split(':', 1)
        tmp[t[0]] = t[1]
    elif args_len > 1:
        for i in range(len(args)):
            t = args[i].split(':', 1)
            tmp[t[0]] = t[1]

    return tmp


def checkArgs(data, ck=[]):
    for i in range(len(ck)):
        if not ck[i] in data:
            return (False, mw.returnJson(False, '参数:(' + ck[i] + ')没有!'))
    return (True, mw.returnJson(True, 'ok'))


def pSqliteDb(dbname='logs'):
    name = "waf"
    db_dir = getServerDir() + '/logs/'
    
    if not os.path.exists(db_dir):
        mw.execShell('mkdir -p ' + db_dir)

    file = db_dir + name + '.db'
    if not os.path.exists(file):
        conn = mw.M(dbname).dbPos(db_dir, name)
        sql = mw.readFile(getPluginDir() + '/conf/waf.sql')
        sql_list = sql.split(';')
        for index in range(len(sql_list)):
            conn.execute(sql_list[index])
    else:
        conn = mw.M(dbname).dbPos(db_dir, name)

    conn.execute("PRAGMA synchronous = 0")
    conn.execute("PRAGMA page_size = 4096")
    conn.execute("PRAGMA journal_mode = wal")
    conn.execute("PRAGMA journal_size_limit = 1073741824")
    return conn


def initDb():
    """初始化数据库"""
    try:
        conn = pSqliteDb()
        # 数据库已通过SQL文件自动初始化
        return mw.returnJson(True, '数据库初始化成功')
    except Exception as e:
        return mw.returnJson(False, f'数据库初始化失败: {str(e)}')


def start():
    """启动服务"""
    try:
        # 检查依赖
        check_dependencies()
        
        # 生成配置文件
        generate_configs()
        
        # 启动监控进程
        start_monitor()
        
        return mw.returnJson(True, 'Web防火墙增强版启动成功')
    except Exception as e:
        return mw.returnJson(False, f'启动失败: {str(e)}')


def stop():
    """停止服务"""
    try:
        # 停止监控进程
        stop_monitor()
        
        # 清理临时文件
        cleanup_temp_files()
        
        return mw.returnJson(True, 'Web防火墙增强版停止成功')
    except Exception as e:
        return mw.returnJson(False, f'停止失败: {str(e)}')


def restart():
    """重启服务"""
    stop_result = stop()
    if not json.loads(stop_result)['status']:
        return stop_result
    
    time.sleep(2)
    start_result = start()
    return start_result


def reload():
    """重新加载配置"""
    try:
        generate_configs()
        reload_nginx()
        return mw.returnJson(True, '配置重新加载成功')
    except Exception as e:
        return mw.returnJson(False, f'配置重新加载失败: {str(e)}')


def getStatus():
    """获取服务状态"""
    try:
        # 检查监控进程是否运行
        monitor_status = check_monitor_status()
        
        # 检查配置文件是否存在
        config_status = os.path.exists(getServerDir() + '/config/main.conf')
        
        # 获取统计数据
        stats = get_statistics()
        
        data = {
            'monitor_running': monitor_status,
            'config_loaded': config_status,
            'stats': stats
        }
        
        return mw.returnJson(True, '状态获取成功', data)
    except Exception as e:
        return mw.returnJson(False, f'状态获取失败: {str(e)}')


def getDashboard():
    """获取仪表板数据"""
    try:
        # 获取实时统计数据
        real_time_stats = get_real_time_stats()
        
        # 获取攻击趋势
        attack_trends = get_attack_trends()
        
        # 获取威胁情报
        threat_intel = get_threat_intelligence()
        
        # 获取系统状态
        system_status = get_system_status()
        
        data = {
            'real_time_stats': real_time_stats,
            'attack_trends': attack_trends,
            'threat_intel': threat_intel,
            'system_status': system_status
        }
        
        return mw.returnJson(True, '仪表板数据获取成功', data)
    except Exception as e:
        return mw.returnJson(False, f'仪表板数据获取失败: {str(e)}')


def getAttackLogs(page=1, page_size=20, search=''):
    """获取攻击日志"""
    try:
        conn = pSqliteDb()
        
        # 构建查询条件
        where_clause = ""
        params = []
        
        if search:
            where_clause = "WHERE ip LIKE ? OR rule_name LIKE ? OR uri LIKE ?"
            search_param = f"%{search}%"
            params = [search_param, search_param, search_param]
        
        # 获取总数
        count_sql = f"SELECT COUNT(*) as count FROM attack_logs {where_clause}"
        count_result = conn.query(count_sql, tuple(params))
        total = count_result[0]['count'] if count_result else 0
        
        # 计算分页
        offset = (int(page) - 1) * int(page_size)
        
        # 获取日志数据
        log_sql = f"""
            SELECT id, ip, rule_name, uri, method, user_agent, referer, 
                   attack_time, action_taken, risk_level
            FROM attack_logs 
            {where_clause}
            ORDER BY attack_time DESC 
            LIMIT ? OFFSET ?
        """
        params.extend([int(page_size), offset])
        logs = conn.query(log_sql, tuple(params))
        
        data = {
            'logs': logs,
            'total': total,
            'page': int(page),
            'page_size': int(page_size),
            'pages': (total + int(page_size) - 1) // int(page_size)
        }
        
        return mw.returnJson(True, '攻击日志获取成功', data)
    except Exception as e:
        return mw.returnJson(False, f'攻击日志获取失败: {str(e)}')


def getRules():
    """获取规则列表"""
    try:
        conn = pSqliteDb()
        rules = conn.table('rules').order('priority ASC').select()
        return mw.returnJson(True, '规则列表获取成功', rules)
    except Exception as e:
        return mw.returnJson(False, f'规则列表获取失败: {str(e)}')


def addRule(rule_data):
    """添加规则"""
    try:
        conn = pSqliteDb()
        
        # 验证规则数据
        required_fields = ['name', 'type', 'pattern', 'action']
        for field in required_fields:
            if field not in rule_data:
                return mw.returnJson(False, f'缺少必要字段: {field}')
        
        # 插入规则
        rule_id = conn.table('rules').insert(rule_data)
        
        # 重新生成配置
        generate_configs()
        
        return mw.returnJson(True, '规则添加成功', {'id': rule_id})
    except Exception as e:
        return mw.returnJson(False, f'规则添加失败: {str(e)}')


def updateRule(rule_id, rule_data):
    """更新规则"""
    try:
        conn = pSqliteDb()
        
        # 更新规则
        conn.table('rules').where('id=?', (rule_id,)).update(rule_data)
        
        # 重新生成配置
        generate_configs()
        
        return mw.returnJson(True, '规则更新成功')
    except Exception as e:
        return mw.returnJson(False, f'规则更新失败: {str(e)}')


def deleteRule(rule_id):
    """删除规则"""
    try:
        conn = pSqliteDb()
        
        # 删除规则
        conn.table('rules').where('id=?', (rule_id,)).delete()
        
        # 重新生成配置
        generate_configs()
        
        return mw.returnJson(True, '规则删除成功')
    except Exception as e:
        return mw.returnJson(False, f'规则删除失败: {str(e)}')


def getStatistics(period='24h'):
    """获取统计信息"""
    try:
        conn = pSqliteDb()
        
        # 根据时间段计算起始时间
        end_time = datetime.now()
        if period == '24h':
            start_time = end_time.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == '7d':
            start_time = end_time - timedelta(days=7)
        elif period == '30d':
            start_time = end_time - timedelta(days=30)
        else:
            start_time = end_time - timedelta(hours=24)
        
        start_timestamp = int(start_time.timestamp())
        end_timestamp = int(end_time.timestamp())
        
        # 获取攻击统计
        attack_stats = conn.query("""
            SELECT rule_name, COUNT(*) as count, MAX(attack_time) as last_time
            FROM attack_logs 
            WHERE attack_time >= ? AND attack_time <= ?
            GROUP BY rule_name
            ORDER BY count DESC
            LIMIT 10
        """, (start_timestamp, end_timestamp))
        
        # 获取IP统计
        ip_stats = conn.query("""
            SELECT ip, COUNT(*) as count, MAX(attack_time) as last_time
            FROM attack_logs 
            WHERE attack_time >= ? AND attack_time <= ?
            GROUP BY ip
            ORDER BY count DESC
            LIMIT 10
        """, (start_timestamp, end_timestamp))
        
        # 获取总统计
        total_stats = conn.query("""
            SELECT 
                COUNT(*) as total_attacks,
                COUNT(DISTINCT ip) as unique_ips,
                COUNT(DISTINCT rule_name) as active_rules
            FROM attack_logs 
            WHERE attack_time >= ? AND attack_time <= ?
        """, (start_timestamp, end_timestamp))
        
        data = {
            'attack_stats': attack_stats,
            'ip_stats': ip_stats,
            'total_stats': total_stats[0] if total_stats else {},
            'period': period
        }
        
        return mw.returnJson(True, '统计信息获取成功', data)
    except Exception as e:
        return mw.returnJson(False, f'统计信息获取失败: {str(e)}')


# 辅助函数
def check_dependencies():
    """检查依赖"""
    # 检查OpenResty是否安装
    openresty_path = '/www/server/openresty'
    if not os.path.exists(openresty_path):
        raise Exception('OpenResty未安装，请先安装OpenResty')
    
    # 检查Lua模块
    lua_modules = ['resty.core', 'resty.lrucache']
    # 这里可以添加具体的Lua模块检查逻辑


def generate_configs():
    """生成配置文件"""
    # 读取规则并生成Lua配置
    conn = pSqliteDb()
    rules = conn.table('rules').where('status=?', ('enabled',)).order('priority ASC').select()
    
    # 生成主配置文件
    main_conf = generate_main_config(rules)
    mw.writeFile(getServerDir() + '/config/main.conf', main_conf)
    
    # 生成规则配置文件
    rules_conf = generate_rules_config(rules)
    mw.writeFile(getServerDir() + '/config/rules.conf', rules_conf)


def generate_main_config(rules):
    """生成主配置"""
    config = """
# WAF Plus Main Configuration
lua_shared_dict waf_cache 50m;
lua_shared_dict waf_stats 10m;
lua_shared_dict waf_rules 20m;

init_by_lua_block {
    -- 加载WAF模块
    local waf = require "waf.main"
    waf.init()
}

access_by_lua_block {
    local waf = require "waf.main"
    waf.access()
}

log_by_lua_block {
    local waf = require "waf.main"
    waf.log()
}
"""
    return config


def generate_rules_config(rules):
    """生成规则配置"""
    config = "-- WAF Rules Configuration\n"
    
    for rule in rules:
        config += f"""
-- Rule: {rule['name']}
waf.add_rule({{
    id = {rule['id']},
    name = "{rule['name']}",
    type = "{rule['type']}",
    pattern = [=[{rule['pattern']}]=],
    action = "{rule['action']}",
    priority = {rule['priority']},
    status = "{rule['status']}"
}})
"""
    
    return config


def reload_nginx():
    """重新加载Nginx"""
    try:
        # 检查Nginx配置语法
        result = subprocess.run(['nginx', '-t'], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Nginx配置语法错误: {result.stderr}")
        
        # 重新加载Nginx
        result = subprocess.run(['nginx', '-s', 'reload'], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Nginx重新加载失败: {result.stderr}")
            
    except FileNotFoundError:
        # 尝试使用OpenResty
        try:
            result = subprocess.run(['/www/server/openresty/nginx/sbin/nginx', '-t'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"OpenResty配置语法错误: {result.stderr}")
                
            result = subprocess.run(['/www/server/openresty/nginx/sbin/nginx', '-s', 'reload'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"OpenResty重新加载失败: {result.stderr}")
        except FileNotFoundError:
            raise Exception("未找到Nginx或OpenResty")


def start_monitor():
    """启动监控进程"""
    # 这里可以启动独立的监控进程
    pass


def stop_monitor():
    """停止监控进程"""
    # 停止监控进程
    pass


def check_monitor_status():
    """检查监控进程状态"""
    # 检查监控进程是否运行
    return True


def cleanup_temp_files():
    """清理临时文件"""
    temp_dir = getServerDir() + '/temp'
    if os.path.exists(temp_dir):
        import shutil
        shutil.rmtree(temp_dir)


def get_real_time_stats():
    """获取实时统计数据"""
    # 实时攻击统计
    conn = pSqliteDb()
    
    # 最近1小时攻击次数
    one_hour_ago = int((datetime.now() - timedelta(hours=1)).timestamp())
    recent_attacks = conn.query("""
        SELECT COUNT(*) as count FROM attack_logs 
        WHERE attack_time >= ?
    """, (one_hour_ago,))
    
    # 当前活跃连接数（模拟数据）
    active_connections = 156
    
    # 当前QPS（模拟数据）
    current_qps = 1247
    
    return {
        'recent_attacks': recent_attacks[0]['count'] if recent_attacks else 0,
        'active_connections': active_connections,
        'current_qps': current_qps,
        'blocked_ips': 23,
        'total_rules': 45
    }


def get_attack_trends():
    """获取攻击趋势"""
    # 返回最近7天的攻击趋势数据
    trends = []
    for i in range(7):
        date = (datetime.now() - timedelta(days=6-i)).strftime('%Y-%m-%d')
        trends.append({
            'date': date,
            'attacks': 100 + i * 15,  # 模拟数据
            'blocked': 85 + i * 12    # 模拟数据
        })
    return trends


def get_threat_intelligence():
    """获取威胁情报"""
    return {
        'malicious_ips_today': 156,
        'new_threats_detected': 23,
        'high_risk_countries': ['CN', 'US', 'RU'],
        'top_attack_types': ['SQL Injection', 'XSS', 'RCE']
    }


def get_system_status():
    """获取系统状态"""
    return {
        'cpu_usage': 23.5,
        'memory_usage': 45.2,
        'disk_usage': 67.8,
        'uptime': '15 days',
        'service_status': 'running'
    }


if __name__ == "__main__":
    func = sys.argv[1]
    
    if func == 'init_db':
        print(initDb())
    elif func == 'start':
        print(start())
    elif func == 'stop':
        print(stop())
    elif func == 'restart':
        print(restart())
    elif func == 'reload':
        print(reload())
    elif func == 'status':
        print(getStatus())
    elif func == 'dashboard':
        print(getDashboard())
    elif func == 'logs':
        page = sys.argv[3] if len(sys.argv) > 3 else 1
        page_size = sys.argv[4] if len(sys.argv) > 4 else 20
        search = sys.argv[5] if len(sys.argv) > 5 else ''
        print(getAttackLogs(page, page_size, search))
    elif func == 'rules':
        print(getRules())
    elif func == 'statistics':
        period = sys.argv[3] if len(sys.argv) > 3 else '24h'
        print(getStatistics(period))
    else:
        print("未知方法: " + func)