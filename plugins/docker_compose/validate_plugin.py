#!/usr/bin/env python
# coding=utf-8
"""
Docker Compose插件结构验证脚本
用于验证插件文件结构和基本功能
"""

import os
import json

def check_plugin_structure():
    """检查插件目录结构"""
    print("=== Docker Compose插件结构检查 ===")
    
    required_files = [
        'info.json',
        'index.py', 
        'index.html',
        'js/docker_compose.js',
        'conf/docker_compose.sql',
        'README.md'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 缺少以下文件:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    else:
        print("✅ 所有必需文件都存在")
        return True

def check_info_json():
    """检查info.json配置"""
    print("\n=== info.json配置检查 ===")
    
    try:
        with open('info.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        required_fields = ['name', 'title', 'versions', 'type']
        missing_fields = []
        
        for field in required_fields:
            if field not in config:
                missing_fields.append(field)
        
        if missing_fields:
            print("❌ 缺少必要字段:", missing_fields)
            return False
            
        print("✅ info.json配置完整")
        print(f"  插件名称: {config.get('name')}")
        print(f"  显示标题: {config.get('title')}")
        print(f"  插件类型: {config.get('type')}")
        print(f"  支持版本: {config.get('versions')}")
        return True
        
    except Exception as e:
        print(f"❌ info.json解析失败: {e}")
        return False

def check_python_syntax():
    """检查Python文件语法"""
    print("\n=== Python语法检查 ===")
    
    python_files = ['index.py']
    
    try:
        for file_path in python_files:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 检查基本结构
                    required_functions = ['getPluginName', 'status', 'start', 'stop', 'getProjects']
                    missing_functions = []
                    
                    for func in required_functions:
                        if f'def {func}' not in content:
                            missing_functions.append(func)
                    
                    if missing_functions:
                        print(f"⚠️  {file_path} 缺少必要函数: {missing_functions}")
                    else:
                        print(f"✅ {file_path} 包含必要函数")
                        
                    # 检查导入语句
                    required_imports = ['subprocess', 'yaml']
                    missing_imports = []
                    for imp in required_imports:
                        if f'import {imp}' not in content and f'from {imp}' not in content:
                            missing_imports.append(imp)
                    
                    if missing_imports:
                        print(f"⚠️  {file_path} 可能缺少必要导入: {missing_imports}")
                    else:
                        print(f"✅ {file_path} 包含必要导入")
            else:
                print(f"❌ {file_path} 不存在")
                return False
        return True
    except Exception as e:
        print(f"❌ Python文件检查出错: {e}")
        return False

def check_javascript_files():
    """检查JavaScript文件"""
    print("\n=== JavaScript文件检查 ===")
    
    js_files = ['js/docker_compose.js']
    
    try:
        for file_path in js_files:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 检查基本函数
                    required_functions = ['dockerComposePost', 'dockerComposePluginService']
                    missing_functions = []
                    
                    for func in required_functions:
                        if func not in content:
                            missing_functions.append(func)
                    
                    if missing_functions:
                        print(f"⚠️  {file_path} 缺少必要函数: {missing_functions}")
                    else:
                        print(f"✅ {file_path} 包含必要函数")
            else:
                print(f"❌ {file_path} 不存在")
                return False
        return True
    except Exception as e:
        print(f"❌ JavaScript文件检查出错: {e}")
        return False

def check_sql_file():
    """检查SQL文件"""
    print("\n=== SQL文件检查 ===")
    
    sql_file = 'conf/docker_compose.sql'
    
    try:
        if os.path.exists(sql_file):
            with open(sql_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 检查必要表
                required_tables = ['projects', 'project_services', 'templates']
                missing_tables = []
                
                for table in required_tables:
                    if f'CREATE TABLE IF NOT EXISTS {table}' not in content:
                        missing_tables.append(table)
                
                if missing_tables:
                    print(f"⚠️  SQL文件缺少必要表: {missing_tables}")
                else:
                    print("✅ SQL文件包含必要表结构")
                
                print(f"✅ {sql_file} 文件存在")
                return True
        else:
            print(f"❌ {sql_file} 不存在")
            return False
    except Exception as e:
        print(f"❌ SQL文件检查出错: {e}")
        return False

def main():
    """主检查函数"""
    print("Docker Compose插件完整性验证")
    print("=" * 50)
    
    checks = [
        check_plugin_structure,
        check_info_json,
        check_python_syntax,
        check_javascript_files,
        check_sql_file
    ]
    
    passed = 0
    total = len(checks)
    
    for check_func in checks:
        if check_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"检查结果: {passed}/{total} 项通过")
    
    if passed == total:
        print("🎉 Docker Compose插件结构完整，可以在Linux环境中部署使用！")
        print("\n功能特性:")
        print("• Docker Compose项目创建、删除管理")
        print("• 项目模板库（WordPress、NextCloud等）")
        print("• 服务启动/停止控制")
        print("• 实时服务状态监控")
        print("• 项目日志查看")
        print("• 图形化管理界面")
    else:
        print("❌ 插件结构存在问题，请根据上面的提示进行修正")

if __name__ == "__main__":
    main()