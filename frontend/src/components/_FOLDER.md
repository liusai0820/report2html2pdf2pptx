# /frontend/src/components - UI 组件库

> ⚠️ **一旦我所属的文件夹有所变化，请更新我。**

## 架构 (3 行)

```
React UI组件集合 ── 从文件上传到结果展示的完整用户界面
       │
       └── 每个组件职责单一，通过props和回调与父组件通信
```

## 文件清单

| 文件                        | 地位     | 功能                                     |
| --------------------------- | -------- | ---------------------------------------- |
| `UploadZone.jsx`            | 入口     | 文件上传区域，支持拖拽和点击上传         |
| `ConfigPanel.jsx`           | 配置     | 配置面板，选择场景、主题、自定义指令     |
| `ScenarioSelector.jsx`      | 配置     | 场景选择器，选择咨询/政务/学术等场景     |
| `ResultView.jsx`            | **核心** | 结果展示，幻灯片预览、网格视图、全屏模式 |
| `Hero.jsx`                  | 展示     | 首页 Hero 区域                           |
| `AuthPage.jsx`              | 认证     | 用户登录/注册页面                        |
| `UserHistoryPanel.jsx`      | 历史     | 用户历史记录面板                         |
| `HistoryOutputSelector.jsx` | 历史     | 历史输出选择器                           |

## 组件依赖关系

```
App.jsx
   ├── UploadZone.jsx
   ├── ConfigPanel.jsx
   │      └── ScenarioSelector.jsx
   ├── ResultView.jsx (核心展示)
   ├── AuthPage.jsx
   └── UserHistoryPanel.jsx
          └── HistoryOutputSelector.jsx
```

---

_遵循分形规则：修改任何文件后，请更新此文档_
