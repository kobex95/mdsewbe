#!/usr/bin/env python
# coding=utf-8

import sys
import io
import os
import time
import json
import yaml
import subprocess
from datetime import datetime

web_dir = os.getcwd() + "/web"
if os.path.exists(web_dir):
    sys.path.append(web_dir)
    os.chdir(web_dir)

import core.mw as mw
import core.db as db_module

# 切换到插件目录
cur_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(cur_dir)


def getPluginName():
    return 'docker_compose'


def getPluginDir():
    return cur_dir


def getServerDir():
    return '/www/server/docker_compose'


def getProjectsDir():
    return getServerDir() + '/projects'


def getTemplatesDir():
    return getServerDir() + '/templates'


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


def pSqliteDb(dbname='projects'):
    """获取插件自身的SQLite数据库连接"""
    file = getServerDir() + '/docker_compose.db'
    name = 'docker_compose'
    
    import_sql = mw.readFile(getPluginDir() + '/conf/docker_compose.sql')
    md5_sql = mw.md5(import_sql)
    
    import_sign = False
    save_md5_file = getServerDir() + '/import_sql.md5'
    if os.path.exists(save_md5_file):
        save_md5_sql = mw.readFile(save_md5_file)
        if save_md5_sql != md5_sql:
            import_sign = True
            mw.writeFile(save_md5_file, md5_sql)
    else:
        mw.writeFile(save_md5_file, md5_sql)
    
    if not os.path.exists(file) or import_sign:
        conn = db_module.Sql().dbPos(getServerDir(), name)
        csql_list = import_sql.split(';')
        for index in range(len(csql_list)):
            if csql_list[index].strip():
                conn.execute(csql_list[index], ())
    else:
        conn = db_module.Sql().dbPos(getServerDir(), name)
    
    return conn


def initDirs():
    """初始化必要的目录"""
    dirs = [getServerDir(), getProjectsDir(), getTemplatesDir()]
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d, mode=0o755)


def checkDockerCompose():
    """检查docker-compose是否可用"""
    try:
        result = subprocess.run(['docker-compose', '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False


def status():
    """检查插件状态"""
    try:
        initDirs()
        if not checkDockerCompose():
            return 'stop'
        
        conn = pSqliteDb()
        # 测试数据库连接
        result = conn.query("SELECT 1", ())
        if result:
            return 'start'
        return 'stop'
    except Exception as e:
        return 'stop'


def start():
    """启动插件"""
    if status() == 'start':
        return mw.returnData(True, 'Docker Compose插件已在运行')
    
    try:
        initDirs()
        if not checkDockerCompose():
            return mw.returnData(False, 'docker-compose命令不可用，请先安装Docker和Docker Compose')
        
        # 初始化数据库
        conn = pSqliteDb()
        conn.query("SELECT 1", ())
        return mw.returnData(True, 'Docker Compose插件启动成功')
    except Exception as e:
        return mw.returnData(False, '启动失败: ' + str(e))


def stop():
    """停止插件"""
    return mw.returnData(True, 'Docker Compose插件已停止')


def restart():
    """重启插件"""
    stop_result = stop()
    if not stop_result['status']:
        return stop_result
    
    time.sleep(1)
    start_result = start()
    return start_result


def getProjects():
    """获取项目列表"""
    try:
        conn = pSqliteDb()
        projects = conn.table('projects').field('*').select()
        return mw.returnData(True, 'success', projects)
    except Exception as e:
        return mw.returnData(False, f'获取项目列表失败: {str(e)}')


def createProject(name, template_id=None, description=''):
    """创建新项目"""
    try:
        initDirs()
        
        # 检查项目名是否已存在
        conn = pSqliteDb()
        existing = conn.table('projects').where('name=?', (name,)).find()
        if existing:
            return mw.returnData(False, f'项目 "{name}" 已存在')
        
        project_path = os.path.join(getProjectsDir(), name)
        if os.path.exists(project_path):
            return mw.returnData(False, f'项目目录 "{project_path}" 已存在')
        
        # 创建项目目录
        os.makedirs(project_path, mode=0o755)
        
        compose_content = ''
        if template_id:
            # 从模板创建
            template = conn.table('templates').where('id=?', (template_id,)).find()
            if template:
                compose_content = template['compose_content']
        else:
            # 创建默认compose文件
            compose_content = '''---
version: '3.8'
services:
  web:
    image: nginx:latest
    ports:
      - "8080:80"
'''
        
        # 写入docker-compose.yml
        compose_file = os.path.join(project_path, 'docker-compose.yml')
        mw.writeFile(compose_file, compose_content)
        
        # 添加到数据库
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        project_id = conn.table('projects').add(
            'name,path,description,status,created_time,updated_time,services_count',
            (name, project_path, description, 'stopped', now, now, 0)
        )
        
        if project_id:
            parseComposeFile(project_id, compose_file)
            return mw.returnData(True, '项目创建成功', {'id': project_id, 'path': project_path})
        else:
            return mw.returnData(False, '添加项目记录失败')
            
    except Exception as e:
        return mw.returnData(False, f'创建项目失败: {str(e)}')


def deleteProject(project_id):
    """删除项目"""
    try:
        conn = pSqliteDb()
        project = conn.table('projects').where('id=?', (project_id,)).find()
        
        if not project:
            return mw.returnData(False, '项目不存在')
        
        # 停止项目（如果正在运行）
        stopProject(project_id)
        
        # 删除项目目录
        if os.path.exists(project['path']):
            import shutil
            shutil.rmtree(project['path'])
        
        # 从数据库中删除
        conn.table('projects').where('id=?', (project_id,)).delete()
        conn.table('project_services').where('project_id=?', (project_id,)).delete()
        conn.table('project_logs').where('project_id=?', (project_id,)).delete()
        
        return mw.returnData(True, '项目删除成功')
    except Exception as e:
        return mw.returnData(False, f'删除项目失败: {str(e)}')


def parseComposeFile(project_id, compose_file):
    """解析docker-compose.yml文件"""
    try:
        if not os.path.exists(compose_file):
            return
        
        with open(compose_file, 'r', encoding='utf-8') as f:
            compose_data = yaml.safe_load(f)
        
        if not compose_data or 'services' not in compose_data:
            return
        
        conn = pSqliteDb()
        services = compose_data['services']
        
        # 清除旧的服务记录
        conn.table('project_services').where('project_id=?', (project_id,)).delete()
        
        # 添加新的服务记录
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for service_name, service_config in services.items():
            image = service_config.get('image', '')
            ports = json.dumps(service_config.get('ports', []))
            volumes = json.dumps(service_config.get('volumes', []))
            environment = json.dumps(service_config.get('environment', {}))
            
            conn.table('project_services').add(
                'project_id,service_name,image,ports,volumes,environment,created_time',
                (project_id, service_name, image, ports, volumes, environment, now)
            )
        
        # 更新项目的服务数量
        services_count = len(services)
        conn.table('projects').where('id=?', (project_id,)).save('services_count', (services_count,))
        
    except Exception as e:
        print(f'解析compose文件失败: {str(e)}')


def getProjectServices(project_id):
    """获取项目的服务列表"""
    try:
        conn = pSqliteDb()
        services = conn.table('project_services').where('project_id=?', (project_id,)).select()
        
        # 获取实际运行状态
        project = conn.table('projects').where('id=?', (project_id,)).find()
        if project and project['status'] == 'running':
            for service in services:
                service['actual_status'] = getServiceStatus(project['path'], service['service_name'])
        else:
            for service in services:
                service['actual_status'] = 'stopped'
        
        return mw.returnData(True, 'success', services)
    except Exception as e:
        return mw.returnData(False, f'获取服务列表失败: {str(e)}')


def getServiceStatus(project_path, service_name):
    """获取单个服务的实际状态"""
    try:
        cmd = f"cd {project_path} && docker-compose ps {service_name} --format json"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            if isinstance(data, list) and len(data) > 0:
                return data[0].get('State', 'unknown')
        return 'stopped'
    except:
        return 'unknown'


def startProject(project_id):
    """启动项目"""
    try:
        conn = pSqliteDb()
        project = conn.table('projects').where('id=?', (project_id,)).find()
        
        if not project:
            return mw.returnData(False, '项目不存在')
        
        if not os.path.exists(project['path']):
            return mw.returnData(False, '项目目录不存在')
        
        compose_file = os.path.join(project['path'], 'docker-compose.yml')
        if not os.path.exists(compose_file):
            return mw.returnData(False, 'docker-compose.yml文件不存在')
        
        # 启动项目
        cmd = f"cd {project['path']} && docker-compose up -d"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            # 更新状态
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            conn.table('projects').where('id=?', (project_id,)).save('status,updated_time', ('running', now))
            return mw.returnData(True, '项目启动成功')
        else:
            return mw.returnData(False, f'启动失败: {result.stderr}')
            
    except Exception as e:
        return mw.returnData(False, f'启动项目失败: {str(e)}')


def stopProject(project_id):
    """停止项目"""
    try:
        conn = pSqliteDb()
        project = conn.table('projects').where('id=?', (project_id,)).find()
        
        if not project:
            return mw.returnData(False, '项目不存在')
        
        if not os.path.exists(project['path']):
            return mw.returnData(False, '项目目录不存在')
        
        # 停止项目
        cmd = f"cd {project['path']} && docker-compose down"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            # 更新状态
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            conn.table('projects').where('id=?', (project_id,)).save('status,updated_time', ('stopped', now))
            return mw.returnData(True, '项目停止成功')
        else:
            return mw.returnData(False, f'停止失败: {result.stderr}')
            
    except Exception as e:
        return mw.returnData(False, f'停止项目失败: {str(e)}')


def getTemplates():
    """获取模板列表"""
    try:
        conn = pSqliteDb()
        templates = conn.table('templates').field('*').select()
        return mw.returnData(True, 'success', templates)
    except Exception as e:
        return mw.returnData(False, f'获取模板列表失败: {str(e)}')


def getProjectLogs(project_id, limit=100):
    """获取项目日志"""
    try:
        conn = pSqliteDb()
        logs = conn.table('project_logs').where('project_id=?', (project_id,)).limit(str(limit)).order('id desc').select()
        return mw.returnData(True, 'success', logs)
    except Exception as e:
        return mw.returnData(False, f'获取日志失败: {str(e)}')


def getConfig():
    """获取配置信息"""
    try:
        conn = pSqliteDb()
        configs = conn.table('config').field('*').select()
        config_dict = {item['key']: item['value'] for item in configs}
        return mw.returnData(True, 'success', config_dict)
    except Exception as e:
        return mw.returnData(False, f'获取配置失败: {str(e)}')


def setConfig(key, value):
    """设置配置"""
    try:
        conn = pSqliteDb()
        existing = conn.table('config').where('key=?', (key,)).find()
        
        if existing:
            conn.table('config').where('key=?', (key,)).save('value', (value,))
        else:
            conn.table('config').add('key,value', (key, value))
        
        return mw.returnData(True, '配置保存成功')
    except Exception as e:
        return mw.returnData(False, f'保存配置失败: {str(e)}')


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
    elif func == 'get_projects':
        print(getProjects())
    elif func == 'create_project':
        args = getArgs()
        print(createProject(args.get('name', ''), args.get('template_id'), args.get('description', '')))
    elif func == 'delete_project':
        args = getArgs()
        print(deleteProject(args.get('id')))
    elif func == 'get_services':
        args = getArgs()
        print(getProjectServices(args.get('project_id')))
    elif func == 'start_project':
        args = getArgs()
        print(startProject(args.get('project_id')))
    elif func == 'stop_project':
        args = getArgs()
        print(stopProject(args.get('project_id')))
    elif func == 'get_templates':
        print(getTemplates())
    elif func == 'get_logs':
        args = getArgs()
        print(getProjectLogs(args.get('project_id'), args.get('limit', 100)))
    elif func == 'get_config':
        print(getConfig())
    elif func == 'set_config':
        args = getArgs()
        print(setConfig(args.get('key'), args.get('value')))
    else:
        print('error')