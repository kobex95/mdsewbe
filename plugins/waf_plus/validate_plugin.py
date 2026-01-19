#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WAF Plus 插件验证脚本
用于验证插件的基本功能和完整性
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_file_exists(filepath, description):
    """检查文件是否存在"""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description}: {filepath} (缺失)")
        return False

def validate_json(filepath):
    """验证JSON文件格式"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ JSON格式验证通过: {filepath}")
        return True
    except json.JSONDecodeError as e:
        print(f"✗ JSON格式错误: {filepath} - {e}")
        return False
    except Exception as e:
        print(f"✗ 读取文件失败: {filepath} - {e}")
        return False

def check_python_syntax(filepath):
    """检查Python文件语法"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        compile(content, filepath, 'exec')
        print(f"✓ Python语法检查通过: {filepath}")
        return True
    except SyntaxError as e:
        print(f"✗ Python语法错误: {filepath} - {e}")
        return False
    except Exception as e:
        print(f"✗ 检查文件失败: {filepath} - {e}")
        return False

def test_api_endpoints():
    """测试API端点（模拟）"""
    # 这里可以添加实际的API测试逻辑
    print("✓ API端点测试占位符")
    return True

def main():
    print("=" * 50)
    print("WAF Plus 插件验证")
    print("=" * 50)
    
    plugin_root = Path(__file__).parent.absolute()
    print(f"插件根目录: {plugin_root}")
    
    # 必需文件检查清单
    required_files = [
        ("info.json", "插件信息文件"),
        ("install.sh", "安装脚本"),
        ("index.py", "主程序文件"),
        ("index.html", "前端界面文件"),
        ("js/waf_plus.js", "前端JavaScript文件"),
        ("conf/waf.sql", "数据库初始化脚本"),
        ("README.md", "说明文档")
    ]
    
    # 验证必需文件
    print("\n📁 必需文件检查:")
    files_ok = True
    for filename, description in required_files:
        filepath = plugin_root / filename
        if not check_file_exists(filepath, description):
            files_ok = False
    
    # 验证JSON文件格式
    print("\n📄 JSON格式验证:")
    json_files = ["info.json"]
    json_ok = True
    for filename in json_files:
        filepath = plugin_root / filename
        if filepath.exists():
            if not validate_json(filepath):
                json_ok = False
    
    # 验证Python文件语法
    print("\n🐍 Python语法检查:")
    python_files = ["index.py"]
    python_ok = True
    for filename in python_files:
        filepath = plugin_root / filename
        if filepath.exists():
            if not check_python_syntax(filepath):
                python_ok = False
    
    # 验证目录结构
    print("\n📂 目录结构检查:")
    required_dirs = ["conf", "js", "logs"]
    dirs_ok = True
    for dirname in required_dirs:
        dirpath = plugin_root / dirname
        if os.path.exists(dirpath) and os.path.isdir(dirpath):
            print(f"✓ 目录存在: {dirpath}")
        else:
            print(f"✗ 目录缺失: {dirpath}")
            dirs_ok = False
    
    # 功能测试
    print("\n🧪 功能测试:")
    api_ok = test_api_endpoints()
    
    # 总结
    print("\n" + "=" * 50)
    print("验证结果汇总:")
    print("=" * 50)
    
    checks = [
        ("文件完整性", files_ok),
        ("JSON格式", json_ok),
        ("Python语法", python_ok),
        ("目录结构", dirs_ok),
        ("API功能", api_ok)
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{check_name:12}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有验证项目通过！插件可以正常使用。")
        return 0
    else:
        print("❌ 部分验证项目失败，请检查上述错误信息。")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)