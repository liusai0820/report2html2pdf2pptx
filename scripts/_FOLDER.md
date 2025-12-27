# /scripts - 脚本工具目录

> ⚠️ **一旦我所属的文件夹有所变化，请更新我。**

## 架构 (3 行)

```
维护与工具脚本集合 ── 批处理、修复、测试、验证脚本
       │
       └── 独立运行的工具脚本，用于开发调试和批量处理
```

## 文件清单

| 文件                         | 地位 | 功能                       |
| ---------------------------- | ---- | -------------------------- |
| `batch_fix_pages.py`         | 修复 | 批量修复已生成的 HTML 页面 |
| `fix_existing_html_fonts.py` | 修复 | 修复已有 HTML 中的字体问题 |
| `convert_existing_pages.py`  | 转换 | 批量转换已有页面格式       |
| `test_font_fix.py`           | 测试 | 测试字体修复功能           |
| `test_punctuation_fix.py`    | 测试 | 测试标点符号修复功能       |
| `verify_structure.py`        | 验证 | 验证项目结构完整性         |
| `__init__.py`                | 模块 | 包初始化                   |

## 使用方式

```bash
# 批量修复字体
python scripts/fix_existing_html_fonts.py

# 验证项目结构
python scripts/verify_structure.py
```

---

_遵循分形规则：修改任何文件后，请更新此文档_
