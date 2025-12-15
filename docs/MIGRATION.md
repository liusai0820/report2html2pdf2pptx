# 迁移指南

## 从旧版本迁移到 v1.0.0

如果你之前使用的是 `tools/ai-generator/` 结构，本指南将帮助你迁移到新的项目结构。

## 主要变更

### 1. 目录结构变更

| 旧路径 | 新路径 | 说明 |
|--------|--------|------|
| `tools/ai-generator/*.py` | `src/*.py` | 核心代码移至 src |
| `tools/ai-generator/.env` | `config/.env` | 配置集中管理 |
| `tools/ai-generator/templates/` | `src/templates/` | 模板随代码 |
| `tools/ai-generator/requirements.txt` | `requirements.txt` | 依赖合并 |

### 2. 启动方式变更

**旧方式**:
```bash
cd tools/ai-generator
python cli.py
```

**新方式**:
```bash
python run.py
# 或
make run
```

### 3. 导入路径变更

**旧代码**:
```python
from cli import main
from config import OPENROUTER_API_KEY
from slide_generator import SlideGenerator
```

**新代码**:
```python
from src.cli import main
from src.config import OPENROUTER_API_KEY
from src.slide_generator import SlideGenerator
```

或者使用 `run.py` 自动处理路径：
```python
# run.py 已经设置好路径
from cli import main  # 直接导入
```

## 迁移步骤

### 步骤 1: 备份配置

```bash
# 备份旧的配置文件
cp tools/ai-generator/.env config/.env.backup
cp pdfservices-api-credentials.json config/pdfservices-api-credentials.json.backup
```

### 步骤 2: 复制配置

```bash
# 复制到新位置
cp tools/ai-generator/.env config/.env
cp pdfservices-api-credentials.json config/pdfservices-api-credentials.json
```

### 步骤 3: 更新依赖

```bash
# 重新安装依赖
pip install -r requirements.txt
npm install
```

### 步骤 4: 测试

```bash
# 运行测试确保配置正确
python tests/test_config.py

# 尝试运行
python run.py --help
```

### 步骤 5: 清理旧文件（可选）

```bash
# 确认新版本工作正常后，可以删除旧目录
rm -rf tools/
```

## 配置文件迁移

### .env 文件

配置项保持不变，只需移动位置：

```bash
# 从
tools/ai-generator/.env

# 到
config/.env
```

内容无需修改：
```env
OPENROUTER_API_KEY=xxx
DEFAULT_MODEL=anthropic/claude-3.5-haiku
# ... 其他配置保持不变
```

### Adobe 凭证

```bash
# 从
pdfservices-api-credentials.json

# 到
config/pdfservices-api-credentials.json
```

## 代码迁移

### 如果你有自定义脚本

**旧代码**:
```python
import sys
sys.path.append('tools/ai-generator')

from slide_generator import SlideGenerator

generator = SlideGenerator()
```

**新代码**:
```python
import sys
from pathlib import Path

# 添加 src 到路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from slide_generator import SlideGenerator

generator = SlideGenerator()
```

### 如果你导入了配置

**旧代码**:
```python
from config import OPENROUTER_API_KEY
```

**新代码**:
```python
# 方式 1: 使用 run.py 的路径设置
from config import OPENROUTER_API_KEY

# 方式 2: 手动设置路径
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))
from config import OPENROUTER_API_KEY
```

## 常见问题

### Q: 旧的输出文件怎么办？

A: 输出文件位置没有变化，仍在 `output/` 目录。

### Q: 我的自定义模板怎么办？

A: 将自定义模板复制到 `src/templates/` 目录。

### Q: 导入错误怎么办？

A: 确保使用 `python run.py` 启动，或手动设置 Python 路径：
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))
```

### Q: 配置文件找不到？

A: 检查 `config/.env` 是否存在：
```bash
ls -la config/.env
```

如果不存在，从示例创建：
```bash
cp config/.env.example config/.env
```

### Q: 旧版本的命令还能用吗？

A: 不能。请使用新的启动方式：
```bash
# 旧: cd tools/ai-generator && python cli.py
# 新: python run.py
```

## 功能对比

| 功能 | 旧版本 | 新版本 | 说明 |
|------|--------|--------|------|
| 交互式模式 | ✅ | ✅ | 保持不变 |
| 批量处理 | ✅ | ✅ | 保持不变 |
| PDF 转 PPTX | ✅ | ✅ | 保持不变 |
| 配置管理 | 分散 | 集中 | 更清晰 |
| 项目结构 | 嵌套 | 扁平 | 更标准 |
| 文档 | 简单 | 完善 | 新增多个文档 |
| 测试 | 无 | 有 | 新增测试 |

## 优势

新版本的优势：

1. **更清晰的结构**: 符合 Python 项目标准
2. **更好的维护性**: 代码组织更合理
3. **更完善的文档**: 多个详细文档
4. **更方便的使用**: 统一的入口点
5. **更好的扩展性**: 易于添加新功能

## 回滚

如果需要回滚到旧版本：

```bash
# 恢复旧的 tools 目录（如果还在）
git checkout HEAD -- tools/

# 或从备份恢复
# ...
```

## 获取帮助

如果迁移过程中遇到问题：

1. 查看 [QUICKSTART.md](QUICKSTART.md)
2. 查看 [README.md](../README.md)
3. 提交 Issue
4. 联系维护者

---

**迁移完成后，建议删除本文档或标记为已完成。**
