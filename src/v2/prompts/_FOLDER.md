# /src/v2/prompts - Prompt 原子化模块

> **⚠️ 一旦本文件夹有所变化，请更新我。**

将 Prompt 从 ai_designer.py 中抽离，按功能分离到独立文件，便于维护和更新。

---

## 文件清单

| 文件                  | 地位   | 功能                                       |
| --------------------- | ------ | ------------------------------------------ |
| `__init__.py`         | 入口   | 导出所有 Prompt 相关函数和配置             |
| `scenario_prompts.py` | 核心   | 场景专属 Prompt (咨询/述职/学术/政府等)    |
| `speech_prompt.py`    | 核心   | 演讲稿生成 Prompt                          |

## 使用方式

```python
from v2.prompts import get_scenario_prompts, build_speech_prompt, get_detail_config

# 获取场景专属 Prompt
prompts = get_scenario_prompts("consulting")
outline_guide = prompts["outline_guide"]
content_style = prompts["content_style"]
speech_tone = prompts["speech_tone"]

# 构建演讲稿 Prompt
prompt = build_speech_prompt(
    document_content=doc,
    slides_text=slides,
    organization="某公司",
    scenario="consulting",
    estimated_minutes=15,
    detail_level="适中",
    detail_guide="...",
    scenario_guide=speech_tone
)
```

---

_遵循分形规则：修改任何文件后，请更新此文档_
_最后更新: 2026-01-11_
