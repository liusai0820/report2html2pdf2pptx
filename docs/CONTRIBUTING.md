# 贡献指南

感谢你对本项目的关注！

## 开发环境设置

1. **克隆仓库**
```bash
git clone <repository-url>
cd ai-presentation-generator
```

2. **安装依赖**
```bash
make install
# 或者
pip install -r requirements.txt
npm install
```

3. **配置环境**
```bash
cp config/.env.example config/.env
# 编辑 config/.env 填入你的 API 密钥
```

4. **运行测试**
```bash
python tests/test_config.py
```

## 代码规范

### Python 代码

- 遵循 PEP 8 规范
- 使用类型提示
- 编写清晰的文档字符串
- 函数名使用 snake_case
- 类名使用 PascalCase

示例：
```python
def generate_slide(title: str, content: str) -> dict:
    """生成单个幻灯片
    
    Args:
        title: 幻灯片标题
        content: 幻灯片内容
        
    Returns:
        包含生成结果的字典
    """
    return {'title': title, 'content': content}
```

### 提交规范

使用语义化提交信息：

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建/工具相关

示例：
```
feat: 添加批量处理功能
fix: 修复 PDF 生成时的内存泄漏
docs: 更新 API 文档
```

## 项目结构

```
src/                    # 核心代码
├── cli.py             # 命令行入口
├── config.py          # 配置管理
├── ai_client.py       # AI 客户端
├── slide_generator.py # 生成器
├── document_parser.py # 文档解析
├── template_merger.py # 模板合并
├── pdf_generator.py   # PDF 生成
└── adobe_integration.py # Adobe 集成

config/                # 配置文件
├── .env.example       # 环境变量示例
└── .gitignore         # 配置忽略规则

docs/                  # 文档
├── API.md            # API 文档
├── ARCHITECTURE.md   # 架构设计
└── CONTRIBUTING.md   # 本文件

tests/                 # 测试
└── test_config.py    # 配置测试
```

## 添加新功能

1. **创建分支**
```bash
git checkout -b feature/your-feature-name
```

2. **编写代码**
   - 在 `src/` 目录下添加或修改代码
   - 保持代码简洁、可读
   - 添加必要的注释

3. **编写测试**
   - 在 `tests/` 目录下添加测试
   - 确保测试覆盖主要功能

4. **更新文档**
   - 更新 README.md（如果需要）
   - 更新 API.md（如果添加了新 API）
   - 更新 CHANGELOG.md

5. **提交代码**
```bash
git add .
git commit -m "feat: 添加新功能"
git push origin feature/your-feature-name
```

6. **创建 Pull Request**

## 调试技巧

### 启用详细日志

在代码中添加：
```python
from rich.console import Console
console = Console()
console.print("[cyan]调试信息[/cyan]")
```

### 测试单个模块

```bash
python -c "from src.ai_client import AIClient; print('导入成功')"
```

### 使用 Python 调试器

```python
import pdb; pdb.set_trace()
```

## 常见问题

### 导入错误

确保 `src/` 在 Python 路径中：
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))
```

### 配置文件找不到

检查 `config/.env` 是否存在，路径是否正确。

### API 调用失败

- 检查 API 密钥是否正确
- 检查网络连接
- 查看错误日志

## 发布流程

1. 更新版本号（setup.py, package.json）
2. 更新 CHANGELOG.md
3. 创建 git tag
4. 推送到远程仓库

## 联系方式

如有问题，请：
- 提交 Issue
- 发送邮件到 [email]
- 加入讨论群 [link]
