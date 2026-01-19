#!/usr/bin/env python
# coding=utf-8

import sys
import io
import os
import time
import sqlite3
import json
import shutil
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
    return 'sqlite'


def getPluginDir():
    return cur_dir


def getServerDir():
    return '/www/server/sqlite'


def getDatabasesDir():
    return getServerDir() + '/databases'


def getBackupsDir():
    return getServerDir() + '/backups'


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


def pSqliteDb(dbname='databases'):
    """获取插件自身的SQLite数据库连接"""
    file = getServerDir() + '/sqlite.db'
    name = 'sqlite'
    
    import_sql = mw.readFile(getPluginDir() + '/conf/sqlite.sql')
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
    dirs = [getServerDir(), getDatabasesDir(), getBackupsDir()]
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d, mode=0o755)


def status():
    """检查插件状态"""
    try:
        initDirs()
        conn = pSqliteDb()
        # 尝试执行简单查询来验证数据库连接
        result = conn.query("SELECT 1", ())
        if result:
            return 'start'
        return 'stop'
    except Exception as e:
        return 'stop'


def start():
    """启动插件"""
    if status() == 'start':
        return mw.returnData(True, 'SQLite插件已在运行')
    
    try:
        initDirs()
        # 初始化数据库
        conn = pSqliteDb()
        # 测试连接
        conn.query("SELECT 1", ())
        return mw.returnData(True, 'SQLite插件启动成功')
    except Exception as e:
        return mw.returnData(False, '启动失败: ' + str(e))


def stop():
    """停止插件"""
    # SQLite是嵌入式的，不需要真正的停止
    return mw.returnData(True, 'SQLite插件已停止')


def restart():
    """重启插件"""
    stop_result = stop()
    if not stop_result['status']:
        return stop_result
    
    time.sleep(1)
    start_result = start()
    return start_result


def getDatabaseConnection(db_path):
    """获取指定数据库的连接"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
        return conn
    except Exception as e:
        raise Exception(f"无法连接数据库 {db_path}: {str(e)}")


def getDatabases():
    """获取数据库列表"""
    try:
        conn = pSqliteDb()
        databases = conn.table('databases').field('*').select()
        return mw.returnData(True, 'success', databases)
    except Exception as e:
        return mw.returnData(False, f'获取数据库列表失败: {str(e)}')


def addDatabase(name, path='', description=''):
    """添加新数据库"""
    try:
        initDirs()
        
        if not path:
            path = os.path.join(getDatabasesDir(), f"{name}.db")
        else:
            # 确保路径在允许的目录内
            if not path.startswith(getDatabasesDir()):
                path = os.path.join(getDatabasesDir(), os.path.basename(path))
        
        # 检查数据库是否已存在
        if os.path.exists(path):
            return mw.returnData(False, f'数据库文件 {path} 已存在')
        
        # 创建新的SQLite数据库
        db_conn = getDatabaseConnection(path)
        db_conn.execute("CREATE TABLE IF NOT EXISTS __metadata (created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        db_conn.commit()
        db_conn.close()
        
        # 添加到管理列表
        conn = pSqliteDb()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db_id = conn.table('databases').add(
            'name,path,size,tables_count,created_time,updated_time,description,status',
            (name, path, 0, 0, now, now, description, 'active')
        )
        
        if db_id:
            updateDatabaseStats(db_id)
            return mw.returnData(True, '数据库创建成功', {'id': db_id, 'path': path})
        else:
            return mw.returnData(False, '添加数据库记录失败')
            
    except Exception as e:
        return mw.returnData(False, f'创建数据库失败: {str(e)}')


def deleteDatabase(db_id):
    """删除数据库"""
    try:
        conn = pSqliteDb()
        database = conn.table('databases').where('id=?', (db_id,)).find()
        
        if not database:
            return mw.returnData(False, '数据库不存在')
        
        # 删除数据库文件
        if os.path.exists(database['path']):
            os.remove(database['path'])
        
        # 从管理列表中删除
        conn.table('databases').where('id=?', (db_id,)).delete()
        conn.table('database_tables').where('db_id=?', (db_id,)).delete()
        conn.table('queries_history').where('db_id=?', (db_id,)).delete()
        
        return mw.returnData(True, '数据库删除成功')
    except Exception as e:
        return mw.returnData(False, f'删除数据库失败: {str(e)}')


def executeQuery(db_id, query):
    """执行SQL查询"""
    try:
        conn = pSqliteDb()
        database = conn.table('databases').where('id=?', (db_id,)).find()
        
        if not database:
            return mw.returnData(False, '数据库不存在')
        
        if not os.path.exists(database['path']):
            return mw.returnData(False, '数据库文件不存在')
        
        start_time = time.time()
        
        # 连接数据库并执行查询
        db_conn = getDatabaseConnection(database['path'])
        cursor = db_conn.cursor()
        
        # 执行查询
        cursor.execute(query)
        
        # 获取结果
        if query.strip().upper().startswith(('SELECT', 'PRAGMA')):
            # 查询语句
            columns = [description[0] for description in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            result_data = [dict(zip(columns, row)) for row in rows]
            result_rows = len(rows)
        else:
            # 执行语句
            db_conn.commit()
            result_data = []
            result_rows = cursor.rowcount
        
        execution_time = time.time() - start_time
        db_conn.close()
        
        # 记录查询历史
        history_conn = pSqliteDb()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        history_conn.table('queries_history').add(
            'db_id,query_text,execution_time,result_rows,executed_time',
            (db_id, query, execution_time, result_rows, now)
        )
        
        # 更新数据库统计信息
        updateDatabaseStats(db_id)
        
        return mw.returnData(True, '查询执行成功', {
            'data': result_data,
            'columns': columns if 'columns' in locals() else [],
            'rows_count': result_rows,
            'execution_time': round(execution_time, 4)
        })
        
    except Exception as e:
        return mw.returnData(False, f'查询执行失败: {str(e)}')


def getDatabaseTables(db_id):
    """获取数据库中的表列表"""
    try:
        conn = pSqliteDb()
        database = conn.table('databases').where('id=?', (db_id,)).find()
        
        if not database:
            return mw.returnData(False, '数据库不存在')
        
        if not os.path.exists(database['path']):
            return mw.returnData(False, '数据库文件不存在')
        
        db_conn = getDatabaseConnection(database['path'])
        cursor = db_conn.cursor()
        
        # 查询所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [{'name': row[0]} for row in cursor.fetchall()]
        
        # 获取每个表的信息
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table['name']})")
            columns = cursor.fetchall()
            table['columns_count'] = len(columns)
            
            cursor.execute(f"SELECT COUNT(*) FROM {table['name']}")
            table['rows_count'] = cursor.fetchone()[0]
        
        db_conn.close()
        
        return mw.returnData(True, 'success', tables)
        
    except Exception as e:
        return mw.returnData(False, f'获取表列表失败: {str(e)}')


def updateDatabaseStats(db_id):
    """更新数据库统计信息"""
    try:
        conn = pSqliteDb()
        database = conn.table('databases').where('id=?', (db_id,)).find()
        
        if not database or not os.path.exists(database['path']):
            return
        
        # 获取文件大小
        size = os.path.getsize(database['path'])
        
        # 获取表数量
        db_conn = getDatabaseConnection(database['path'])
        cursor = db_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables_count = cursor.fetchone()[0]
        db_conn.close()
        
        # 更新记录
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.table('databases').where('id=?', (db_id,)).save(
            'size,tables_count,updated_time',
            (size, tables_count, now)
        )
        
    except Exception as e:
        pass  # 静默处理统计更新错误


def backupDatabase(db_id):
    """备份数据库"""
    try:
        conn = pSqliteDb()
        database = conn.table('databases').where('id=?', (db_id,)).find()
        
        if not database:
            return mw.returnData(False, '数据库不存在')
        
        if not os.path.exists(database['path']):
            return mw.returnData(False, '数据库文件不存在')
        
        # 创建备份目录
        backup_dir = getBackupsDir()
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir, mode=0o755)
        
        # 生成备份文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"{database['name']}_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # 复制数据库文件
        shutil.copy2(database['path'], backup_path)
        
        return mw.returnData(True, '备份成功', {
            'backup_path': backup_path,
            'backup_filename': backup_filename
        })
        
    except Exception as e:
        return mw.returnData(False, f'备份失败: {str(e)}')


def getQueriesHistory(db_id, limit=50):
    """获取查询历史"""
    try:
        conn = pSqliteDb()
        condition = 'db_id=?' if db_id else ''
        params = (db_id,) if db_id else ()
        
        history = conn.table('queries_history')\
                  .where(condition, params)\
                  .field('id,query_text,execution_time,result_rows,executed_time')\
                  .limit(str(limit))\
                  .order('id desc')\
                  .select()
        
        return mw.returnData(True, 'success', history)
        
    except Exception as e:
        return mw.returnData(False, f'获取查询历史失败: {str(e)}')


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
    elif func == 'get_databases':
        print(getDatabases())
    elif func == 'add_database':
        args = getArgs()
        print(addDatabase(args.get('name', ''), args.get('path', ''), args.get('description', '')))
    elif func == 'delete_database':
        args = getArgs()
        print(deleteDatabase(args.get('id')))
    elif func == 'execute_query':
        args = getArgs()
        print(executeQuery(args.get('db_id'), args.get('query')))
    elif func == 'get_tables':
        args = getArgs()
        print(getDatabaseTables(args.get('db_id')))
    elif func == 'backup_database':
        args = getArgs()
        print(backupDatabase(args.get('db_id')))
    elif func == 'get_history':
        args = getArgs()
        print(getQueriesHistory(args.get('db_id')))
    elif func == 'get_config':
        print(getConfig())
    elif func == 'set_config':
        args = getArgs()
        print(setConfig(args.get('key'), args.get('value')))
    else:
        print('error')