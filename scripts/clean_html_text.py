import re
import sys

file_path = "/Users/qibaoba/report2html2pdf2pptx/input/outputs_2026_01_05_二零二五年述职报告_061207_v2_presentation.html"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 去掉 **
content = content.replace('**', '')

# 2. 去掉特定的 " / English" 模式
content = re.sub(r' / [A-Za-z ]+(?=<)', '', content)
content = re.sub(r' / [A-Za-z ]+(?=")', '', content) # 针对某些可能在属性里的（虽然较少）

# 3. 去掉封面上的 ANNUAL_REVIEW
content = re.sub(r'<div class="cover-subtitle">\s*ANNUAL_REVIEW\s*</div>', '', content)

# 4. 去掉目录中的英文说明
# 匹配类似 <span style="...">ENGLISH DESCRIPTION</span> 且全是英文和大写的情况
content = re.sub(r'<span[^>]*style="[^"]*color:\s*#9ca3af;[^"]*"[^>]*>[A-Z0-9 ]+</span>', '', content)

# 5. 针对 汇报单位 / Organization 等
content = content.replace('汇报单位 / Organization', '汇报单位')
content = content.replace('日期 / Date', '日期')
content = content.replace('汇报人 / Speaker', '汇报人')
content = content.replace('目录 / CONTENTS', '目录')

# 6. 继续清理其他可能的英文小字
# 匹配标签内全是英文大写字母和空格的内容，通常是装饰性的英文
def clean_caps(match):
    text = match.group(2)
    # 如果全是英文大写、数字、空格、且长度大于3
    if re.fullmatch(r'[A-Z0-9\s_/]+', text) and len(text.strip()) > 3:
        return match.group(1) + match.group(3)
    return match.group(0)

# 针对常见的 span 和 div
content = re.sub(r'(<span[^>]*>)([^<]+)(</span>)', clean_caps, content)
content = re.sub(r'(<div[^>]*>)([^<]+)(</div>)', clean_caps, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Processing complete.")
