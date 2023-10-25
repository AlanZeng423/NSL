import re
import matplotlib.pyplot as plt

# 用于匹配目标文本的正则表达式
pattern = r"Finished Inference of Job (\d+) JCT=([\d.]+)"

# 输入文件名
input_file = "output.txt"

# 初始化存储提取结果的列表
job_numbers = []
jct_values = []

# 打开输入文件并提取数据
with open(input_file, "r") as input_file:
    for line in input_file:
        match = re.search(pattern, line)
        if match:
            job = int(match.group(1))
            jct = float(match.group(2))
            job_numbers.append(job)
            jct_values.append(jct)

# 创建柱状图
plt.figure(figsize=(10, 6))
plt.bar(job_numbers, jct_values, color='b', alpha=0.7)
plt.xlabel('Job Number')
plt.ylabel('JCT (Job Completion Time)')
plt.title('Job Completion Time for Each Job')
plt.grid(True)

# 显示柱状图
plt.show()
