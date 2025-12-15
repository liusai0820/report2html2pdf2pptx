#!/usr/bin/env python3
"""验证项目结构完整性"""
import os
from pathlib import Path

def check_file(path, description):
    """检查文件是否存在"""
    if Path(path).exists():
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description}: {path} (缺失)")
        return False

def check_directory(path, description):
    """检查目录是否存在"""
    if Path(path).is_dir():
        print(f"✅ {description}: {path}/")
        return True
    else:
        print(f"❌ {description}: {path}/ (缺失)")
        return False

def main():
    print("🔍 验证项目结构...\n")
    
    checks = []
    
    # 核心目录
    print("📁 核心目录:")
    checks.append(check_directory("src", "源代码目录"))
    checks.append(check_directory("config", "配置目录"))
    checks.append(check_directory("docs", "文档目录"))
    checks.append(check_directory("tests", "测试目录"))
    checks.append(check_directory("input", "输入目录"))
    checks.append(check_directory("output", "输出目录"))
    
    # 核心文件
    print("\n📄 核心文件:")
    checks.append(check_file("run.py", "项目入口"))
    checks.append(check_file("README.md", "项目说明"))
    checks.append(check_file("requirements.txt", "Python依赖"))
    checks.append(check_file("package.json", "Node.js依赖"))
    checks.append(check_file("setup.py", "包配置"))
    checks.append(check_file("Makefile", "便捷命令"))
    checks.append(check_file("LICENSE", "许可证"))
    
    # 源代码文件
    print("\n🐍 源代码文件:")
    src_files = [
        "cli.py", "config.py", "ai_client.py", "slide_generator.py",
        "document_parser.py", "template_merger.py", "pdf_generator.py",
        "adobe_integration.py", "context_manager.py"
    ]
    for f in src_files:
        checks.append(check_file(f"src/{f}", f))
    
    # 配置文件
    print("\n⚙️ 配置文件:")
    checks.append(check_file("config/.env.example", "环境变量示例"))
    checks.append(check_file("config/.gitignore", "配置忽略规则"))
    
    # 文档文件
    print("\n📚 文档文件:")
    doc_files = [
        "API.md", "ARCHITECTURE.md", "CONTRIBUTING.md", 
        "QUICKSTART.md", "MIGRATION.md"
    ]
    for f in doc_files:
        checks.append(check_file(f"docs/{f}", f))
    
    # 测试文件
    print("\n🧪 测试文件:")
    checks.append(check_file("tests/test_config.py", "配置测试"))
    
    # 统计
    print("\n" + "="*50)
    passed = sum(checks)
    total = len(checks)
    percentage = (passed / total) * 100
    
    print(f"\n📊 验证结果: {passed}/{total} ({percentage:.1f}%)")
    
    if passed == total:
        print("✅ 项目结构完整！")
        return 0
    else:
        print(f"⚠️  有 {total - passed} 个项目缺失")
        return 1

if __name__ == "__main__":
    exit(main())
