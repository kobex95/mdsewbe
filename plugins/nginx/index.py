#!/usr/bin/env python
# coding=utf-8

import sys
import io
import os
import time
import subprocess
import re
import json

web_dir = os.getcwd() + "/web"
if os.path.exists(web_dir):
    sys.path.append(web_dir)
    os.chdir(web_dir)

import core.mw as mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'nginx'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile():
    current_os = mw.getOs()
    if current_os == 'darwin':
        return '/tmp/' + getPluginName()

    if current_os.startswith('freebsd'):
        return '/etc/rc.d/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getArgs():
    args = sys.argv[2:]
    tmp = {}
    args_len = len(args)
    if args_len == 1:
        t = args[0].strip('{').strip('}')
        if t.strip() == '':
            tmp = []
        else:
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


def getConf():
    path = getServerDir() + '/conf/nginx.conf'
    return path


def getPidFile():
    file = getConf()
    content = mw.readFile(file)
    rep = r'pid\s*(.*);'
    tmp = re.search(rep, content)
    if tmp:
        return tmp.groups()[0].strip()
    return getServerDir() + '/logs/nginx.pid'


def getErrorLogsFile():
    file = getConf()
    content = mw.readFile(file)
    rep = r'error_log\s*(.*);'
    tmp = re.search(rep, content)
    if tmp:
        return tmp.groups()[0].strip()
    return getServerDir() + '/logs/error.log'


def getAccessLogsFile():
    file = getConf()
    content = mw.readFile(file)
    rep = r'access_log\s*(.*);'
    tmp = re.search(rep, content)
    if tmp:
        return tmp.groups()[0].strip()
    return getServerDir() + '/logs/access.log'


def status():
    pid_file = getPidFile()
    if not os.path.exists(pid_file):
        return 'stop'
    
    pid = mw.readFile(pid_file)
    if pid:
        pid = pid.strip()
        if mw.isProcessExists('nginx', pid):
            return 'start'
    return 'stop'


def start():
    if status() == 'start':
        return mw.returnData(True, 'nginx已启动')

    # 检查配置文件语法
    check_cmd = getServerDir() + '/sbin/nginx -t -c ' + getConf()
    result = mw.execShell(check_cmd)
    if result[1] != '':
        return mw.returnData(False, '配置文件语法错误: ' + result[1])

    # 启动nginx
    cmd = getServerDir() + '/sbin/nginx -c ' + getConf()
    result = mw.execShell(cmd)
    if result[1] != '':
        return mw.returnData(False, '启动失败: ' + result[1])
    
    time.sleep(1)
    if status() == 'start':
        return mw.returnData(True, 'nginx启动成功')
    return mw.returnData(False, 'nginx启动失败')


def stop():
    if status() == 'stop':
        return mw.returnData(True, 'nginx已停止')
    
    pid_file = getPidFile()
    if not os.path.exists(pid_file):
        return mw.returnData(False, '找不到PID文件')
    
    pid = mw.readFile(pid_file)
    if not pid:
        return mw.returnData(False, 'PID文件为空')
    
    pid = pid.strip()
    cmd = 'kill ' + pid
    result = mw.execShell(cmd)
    if result[1] != '':
        return mw.returnData(False, '停止失败: ' + result[1])
    
    # 等待进程完全退出
    time.sleep(2)
    if status() == 'stop':
        return mw.returnData(True, 'nginx停止成功')
    return mw.returnData(False, 'nginx停止失败')


def restart():
    stop_result = stop()
    if not stop_result['status']:
        return stop_result
    
    time.sleep(1)
    start_result = start()
    return start_result


def reload():
    if status() == 'stop':
        return mw.returnData(False, 'nginx未启动')
    
    # 检查配置文件语法
    check_cmd = getServerDir() + '/sbin/nginx -t -c ' + getConf()
    result = mw.execShell(check_cmd)
    if result[1] != '':
        return mw.returnData(False, '配置文件语法错误: ' + result[1])
    
    # 重新加载配置
    cmd = getServerDir() + '/sbin/nginx -s reload'
    result = mw.execShell(cmd)
    if result[1] != '':
        return mw.returnData(False, '重新加载失败: ' + result[1])
    
    return mw.returnData(True, 'nginx配置重新加载成功')


def initdStatus():
    if mw.isAppleSystem():
        return "Apple Computer does not support"
    
    shell_cmd = 'systemctl status ' + getPluginName() + ' | grep loaded | grep "enabled;"'
    data = mw.execShell(shell_cmd)
    if data[0] == '':
        return 'fail'
    return 'ok'


def initdInstall():
    if mw.isAppleSystem():
        return "Apple Computer does not support"
    
    # 复制启动脚本
    initd_file = getInitDFile()
    if not os.path.exists(initd_file):
        source_initd = getPluginDir() + '/init.d/nginx.init'
        mw.execShell('cp -f ' + source_initd + ' ' + initd_file)
        mw.execShell('chmod +x ' + initd_file)
    
    # 设置开机启动
    mw.execShell('systemctl enable ' + getPluginName())
    return 'ok'


def initdUinstall():
    if mw.isAppleSystem():
        return "Apple Computer does not support"
    
    # 取消开机启动
    mw.execShell('systemctl disable ' + getPluginName())
    return 'ok'


def runInfo():
    """获取Nginx运行状态信息"""
    if status() == 'stop':
        return mw.returnJson(False, "Nginx未启动!")
    
    try:
        # 获取基本状态信息
        pid_file = getPidFile()
        pid = mw.readFile(pid_file).strip() if os.path.exists(pid_file) else ""
        
        # 获取版本信息
        version_cmd = getServerDir() + '/sbin/nginx -v'
        version_result = mw.execShell(version_cmd)
        version = version_result[1].strip() if version_result[1] else "unknown"
        
        # 获取工作进程数
        worker_processes = "unknown"
        conf_content = mw.readFile(getConf())
        if conf_content:
            worker_match = re.search(r'worker_processes\s+(\w+);', conf_content)
            if worker_match:
                worker_processes = worker_match.group(1)
        
        # 获取监听端口
        ports = []
        if conf_content:
            port_matches = re.findall(r'listen\s+(\d+);', conf_content)
            ports = list(set(port_matches))  # 去重
        
        data = {
            'status': 'running',
            'pid': pid,
            'version': version,
            'worker_processes': worker_processes,
            'listen_ports': ports,
            'start_time': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return mw.getJson(data)
    except Exception as e:
        return mw.returnJson(False, "获取状态信息失败: " + str(e))


def getErrorLogs():
    """获取错误日志"""
    log_file = getErrorLogsFile()
    if not os.path.exists(log_file):
        return mw.returnJson(False, "错误日志文件不存在")
    
    # 读取最近100行日志
    cmd = 'tail -n 100 ' + log_file
    result = mw.execShell(cmd)
    return result[0]


def getAccessLogs():
    """获取访问日志"""
    log_file = getAccessLogsFile()
    if not os.path.exists(log_file):
        return mw.returnJson(False, "访问日志文件不存在")
    
    # 读取最近100行日志
    cmd = 'tail -n 100 ' + log_file
    result = mw.execShell(cmd)
    return result[0]


def getConfig():
    """获取配置文件内容"""
    conf_file = getConf()
    if not os.path.exists(conf_file):
        return mw.returnJson(False, "配置文件不存在")
    
    content = mw.readFile(conf_file)
    return content


def setConfig(content):
    """保存配置文件"""
    conf_file = getConf()
    
    # 备份原配置文件
    backup_file = conf_file + '.bak.' + time.strftime('%Y%m%d_%H%M%S')
    mw.execShell('cp ' + conf_file + ' ' + backup_file)
    
    # 写入新配置
    result = mw.writeFile(conf_file, content)
    if not result:
        return mw.returnJson(False, "保存配置文件失败")
    
    return mw.returnJson(True, "配置文件保存成功")


def testConfig():
    """测试配置文件语法"""
    cmd = getServerDir() + '/sbin/nginx -t -c ' + getConf()
    result = mw.execShell(cmd)
    if result[1] == '':
        return mw.returnJson(True, "配置文件语法正确")
    return mw.returnJson(False, result[1])


def getVhosts():
    """获取虚拟主机列表"""
    vhost_dir = getServerDir() + '/conf/vhost'
    if not os.path.exists(vhost_dir):
        return []
    
    vhosts = []
    for file in os.listdir(vhost_dir):
        if file.endswith('.conf'):
            file_path = os.path.join(vhost_dir, file)
            content = mw.readFile(file_path)
            if content:
                # 解析域名
                server_names = re.findall(r'server_name\s+([^;]+);', content)
                domains = []
                for sn in server_names:
                    domains.extend(sn.strip().split())
                
                # 解析端口
                ports = re.findall(r'listen\s+(\d+)', content)
                
                vhost = {
                    'name': file.replace('.conf', ''),
                    'file': file,
                    'domains': domains,
                    'ports': list(set(ports)),
                    'status': 'active' if 'server' in content else 'inactive'
                }
                vhosts.append(vhost)
    
    return vhosts


if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print(status())
    elif func == 'start':
        print(start())
    elif func == 'stop':
        print(stop())
    elif func == 'restart':
        print(restart())
    elif func == 'reload':
        print(reload())
    elif func == 'initd_status':
        print(initdStatus())
    elif func == 'initd_install':
        print(initdInstall())
    elif func == 'initd_uninstall':
        print(initdUinstall())
    elif func == 'conf':
        print(getConf())
    elif func == 'run_info':
        print(runInfo())
    elif func == 'error_logs':
        print(getErrorLogs())
    elif func == 'access_logs':
        print(getAccessLogs())
    elif func == 'get_config':
        print(getConfig())
    elif func == 'test_config':
        print(testConfig())
    elif func == 'get_vhosts':
        print(json.dumps(getVhosts()))
    else:
        print('error')