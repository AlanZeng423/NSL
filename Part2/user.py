import csv
import time
import threading
import numpy as np
import queue

JOB_NUM = 99  # 发送请求的个数

# 在opt-1.3B上的实验数据 单位: ms
x = [1.0, 4.0, 16.0, 64.0, 256.0, 512.0, 1024.0]
first_time = [5.88, 5.93, 6.57, 8.04, 23.8, 43.9, 98.5]
next_time = [5.13, 5.11, 5.16, 5.22, 5.52, 5.72, 5.82]

# 通过实验数据拟合每次迭代推理时间
z1 = np.polyfit(x, first_time, 1)
p1 = np.poly1d(z1)

z2 = np.polyfit(x, next_time, 1)
p2 = np.poly1d(z2)

request_queue = queue.Queue()


def fit_first_iter_time(prompt_length):
    # 使用一次多项式函数 p1 来估计推理时间
    return p1(prompt_length)


def fit_next_iter_time(prompt_length):
    # 使用一次多项式函数 p2 来估计推理时间
    return p2(prompt_length)


class Request:  # 推理请求，理论上输出长度未知，但为仿真实验，需要事先确定
    def __init__(self, j_id, prompt_length, output_length):
        self.j_id = j_id
        self.prompt_length = int(prompt_length)
        self.output_length = int(output_length)
        self.first_iter_time = fit_first_iter_time(float(self.prompt_length))
        self.next_iter_time = fit_next_iter_time(float(self.prompt_length))
        self.iter_count = 0  # 请求执行了几次迭代，iter_count==output_length时完成整个推理
        self.priority = -1  # 请求目前处于第几级队列
        self.to_id = 0

        self.create_time = time.time()  # 请求创建时间


class RequestGenerator(threading.Thread):

    def __init__(self, arrival_rate):
        super().__init__()
        self.arrival_rate = arrival_rate  # arrival rate = 1s / job interval

    def run(self):
        prompt_length_list = []
        output_length_list = []

        # 此处为读取orca数据集中的数据来构造request，可自行修改路径
        f = open('./simulation/orca_100k.csv', 'r')
        with f:
            reader = csv.reader(f)
            count = 0
            for row in reader:
                if count == 0:
                    count += 1
                    continue

                prompt_length_list.append(row[0])
                output_length_list.append(row[1])

        j_id = 0

        while j_id < JOB_NUM:
            output_ = output_length_list[j_id]
            input_ = prompt_length_list[j_id]
            request = Request(j_id, input_, output_)
            request_queue.put(request)
            print(f"THREAD-USER: Putting Task{j_id}")
            j_id += 1

            time.sleep(1 / self.arrival_rate)
