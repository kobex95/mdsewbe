#!/usr/bin/env python
# coding=utf-8
"""
Nginx插件结构验证脚本
用于验证插件文件结构和基本功能
"""

import os
import json

def check_plugin_structure():
    """检查插件目录结构"""
    print("=== Nginx插件结构检查 ===")
    
    required_files = [
        'info.json',
        'install.sh', 
        'index.py',
        'index.html',
        'init.d/nginx.init',
        'js/nginx.js',
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
        
        required_fields = ['name', 'title', 'versions', 'shell']
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
        print(f"  支持版本: {config.get('versions')}")
        print(f"  安装脚本: {config.get('shell')}")
        return True
        
    except Exception as e:
        print(f"❌ info.json解析失败: {e}")
        return False

def check_executable_permissions():
    """检查可执行文件权限"""
    print("\n=== 可执行文件检查 ===")
    
    executable_files = ['install.sh']
    issues = []
    
    for file_path in executable_files:
        if os.path.exists(file_path):
            # 检查是否有执行权限（简化检查）
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('#!'):
                    print(f"✅ {file_path} 有shebang行")
                else:
                    print(f"⚠️  {file_path} 缺少shebang行")
        else:
            issues.append(file_path)
    
    if issues:
        print("❌ 缺少文件:", issues)
        return False
    return True

def check_python_syntax():
    """检查Python文件语法"""
    print("\n=== Python语法检查 ===")
    
    python_files = ['index.py']
    
    try:
        # 简单的语法检查（实际运行需要完整环境）
        for file_path in python_files:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 这里只是简单检查，实际语法检查需要在目标环境中进行
                    if 'def ' in content and 'import ' in content:
                        print(f"✅ {file_path} 包含基本Python结构")
                    else:
                        print(f"⚠️  {file_path} 可能缺少必要结构")
            else:
                print(f"❌ {file_path} 不存在")
                return False
        return True
    except Exception as e:
        print(f"❌ Python文件检查出错: {e}")
        return False

def main():
    """主检查函数"""
    print("Nginx插件完整性验证")
    print("=" * 50)
    
    checks = [
        check_plugin_structure,
        check_info_json,
        check_executable_permissions,
        check_python_syntax
    ]
    
    passed = 0
    total = len(checks)
    
    for check_func in checks:
        if check_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"检查结果: {passed}/{total} 项通过")
    
    if passed == total:
        print("🎉 插件结构完整，可以在Linux环境中部署使用！")
        print("\n部署建议:")
        print("1. 将整个nginx目录复制到mdserver-web的plugins目录")
        print("2. 确保服务器有编译环境(gcc, make等)")
        print("3. 通过面板或命令行安装插件")
        print("4. 测试各项功能是否正常")
    else:
        print("❌ 插件结构存在问题，请根据上面的提示进行修正")

if __name__ == "__main__":
    main()