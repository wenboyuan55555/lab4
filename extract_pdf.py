import fitz

# 打开PDF文件
doc = fitz.open('实验任务书.pdf')

# 提取文本
text = ""
for page in doc:
    text += page.get_text()

# 将文本内容保存到文件
with open('task_content.txt', 'w', encoding='utf-8') as f:
    f.write(text)

print("已将PDF内容提取到task_content.txt文件") 