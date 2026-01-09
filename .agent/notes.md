# Notes: 图片内容理解优化研究

## 问题复现

### 原图内容（企业客户画像）
根据用户反馈，原图包含：
- 五颗星客户：深投控、特建发、特建工、各区投、上海市北高新
- 四颗星客户：政府智库机构、第三方咨询机构、大型国央企研究部门
- 三颗星客户：产业地产开发与园区招商管理企业、金融公司
- 一/二颗星客户：投资机构、产业链企业
- 免费用户：深圳市内IP免费使用部分功能

### 生成结果
缺少具体的企业名称列表

### 差距分析
预解析描述中应该包含这些内容，但：
1. 可能描述不够详细
2. AI 在正文生成时没有"验证参照物"

## 当前代码流程

### 1. 图片预解析 (analyze_images)
```python
# 对每张图片调用 AI 提取内容
response = await self._call_ai(prompt, images=[img])
```

### 2. 大纲生成 (generate_outline)
```python
# 使用预解析描述，不发送图片
response = await self._call_ai(prompt, use_reasoning=True)
# 之前: images=context.images  ← 发送图片
# 现在: 不发送图片
```

### 3. 正文页生成 (generate_page)
```python
# 只使用描述，不发送图片
html = await self._call_ai(prompt)
# 之前: images=images_to_pass  ← 发送图片
# 现在: 不发送图片
```

## 优化方案分析

### 方案 C 实施细节

修改 `generate_page` 方法：
1. 检查该页是否有 `image_indices`
2. 如果有，同时传递：
   - 预解析的图片描述（在 prompt 中）
   - 原始图片（通过 images 参数）
3. AI 可以"看图 + 读描述"双重验证

### 预期效果
- 描述告诉 AI："这张图包含五颗星客户：深投控、特建发..."
- 图片让 AI 能验证："确实是这些内容"
- 生成结果更精确

## 代码修改位置

文件: `/Users/qibaoba/report2html2pdf2pptx/src/v2/ai_designer.py`

需要修改的函数: `generate_page`

修改内容:
1. 恢复 `images_to_pass` 逻辑
2. 同时保留描述在 prompt 中
3. 调用时传递 `images=images_to_pass`
