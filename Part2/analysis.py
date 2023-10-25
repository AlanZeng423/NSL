import re

# 用于匹配目标文本的正则表达式
pattern = r"Finished Inference of Job (\d+) JCT=([\d.]+)"

# 输入文件名和输出文件名
input_file = "output.txt"
output_file = "output2.txt"

# 打开输入文件和输出文件
with open(input_file, "r") as input_file, open(output_file, "w") as output_file:
    # 遍历输入文件的每一行
    for line in input_file:
        # 使用正则表达式查找匹配的内容
        match = re.search(pattern, line)
        if match:
            # 提取Job和JCT的值
            job = match.group(1)
            jct = match.group(2)
            # 将匹配行写入输出文件
            output_file.write(f"Job {job} JCT={jct}\n")

# 打印完成消息
print("提取完成，结果已保存到output2.txt文件。")
