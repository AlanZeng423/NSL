# Define class
import queue
import threading
import time

from inference import simulate_forward
from user import Request, JOB_NUM
from user import request_queue

from concurrent.futures import ThreadPoolExecutor


max_threads = 4
thread_pool = ThreadPoolExecutor(max_threads)


def find(sorted_list, x):
    # 使用二分查找算法
    low = 0
    high = len(sorted_list) - 1
    result = None

    while low <= high:
        mid = (low + high) // 2
        if sorted_list[mid] >= x:
            result = mid
            high = mid - 1  # 继续查找左半部分
        else:
            low = mid + 1  # 继续查找右半部分

    return result


class SkipJoinMLFQScheduler(threading.Thread):
    """
    多级队列包含三个参数，Queue_num, Quantum和Quantum_rate，
    - Queue_num代表多级队列一共有多少级，即包含了多少个队列；
    - Quantum需要设置为自回归阶段生成一个token的时间，
    - 而Quantum_rate则需要手动设置，它代表队列之间能够推理自回归阶段token数量的倍数。
    例如Quantum=1, Quantum_rate=2时，二级队列的Quantum即为2，
    代表在自回归阶段可以一次生成两个token，三级队列可以一次生成4个token。
    """

    def __init__(self, first_quantum=6, quantum_rate=4, queue_num=6):
        super().__init__()
        self.quantum_list = []
        self.multi_level_priority_queue = []
        self.executed = 0  # 已经完成的请求数量

        # first quantum/Q1 is the min iteration time
        for i in range(queue_num):
            # self.quantum_list.append(first_quantum * quantum_rate ** i)
            self.quantum_list.append(quantum_rate ** i)
            # [1, 4, 16, 64]
            temp_q = queue.Queue(-1)
            self.multi_level_priority_queue.append(temp_q)

        self.ave_jct = []

    def getNewRequest(self, request: Request):
        # Todo: 处理缓冲区中新到达的request，根据他们的输入长度放入多级队列中
        # ft = request.first_iter_time
        length = request.prompt_length
        # print(f"THREAD-SCHEDULER:length = {length}")
        index = 0
        # for x in self.quantum_list:
        #     if x >= ft:
        #         index = self.quantum_list.index(x)
        #         break
        index = find(self.quantum_list, length)
        print(f"THREAD-SCHEDULER:putting request{request.j_id} (length = {length})into queue{index}")
        self.multi_level_priority_queue[index].put(request)
        request.priority = index
        pass
    #
    def demoteRequest(self, job: Request):
        # Todo: 将完成了推理但还没生成完毕的请求放入下一级队列
        if job.priority == len(self.multi_level_priority_queue) - 1:
            # 如果已经在最后一级队列，则不再降级
            return
        job.priority += 1
        self.multi_level_priority_queue[job.priority].put(job)

        pass

    def getInferenceJob(self):
        # Todo: 返回在最高优先级的队列中的队首请求
        i = 0
        while i < len(self.multi_level_priority_queue) and self.multi_level_priority_queue[i].empty():
            i = i + 1

        if i < len(self.multi_level_priority_queue):
            first_non_empty_queue = self.multi_level_priority_queue[i]
            first_element = first_non_empty_queue.get()
            print(f"THREAD-SCHEDULER: Getting Job{first_element.j_id} from queue{first_element.priority}")
            return first_element
        else:
            return None

        pass

    # 推理线程
    def run(self):
        print(f"THREAD-SCHEDULER:requestQueue's len = {request_queue.qsize()}")
        # if(request_queue!=None):
        # time.sleep(10)
        while self.executed != JOB_NUM:
            # if request_queue.qsize() == 0:
            #     continue
            # print(f"THREAD-SCHEDULER:requestQueue's len = {request_queue.qsize()}")
            # 将缓存中的任务加入到scheduler的多级队列中
            for i in range(request_queue.qsize()):
                req = request_queue.get()
                self.getNewRequest(req)

            # 找到当前执行的任务
            job = self.getInferenceJob()
            if job is None:
                continue
            print(f"THREAD-SCHEDULER: Submitting Job{job.j_id}")
            if job.iter_count == 0:
                iter_time = job.first_iter_time
            else:
                iter_time = job.next_iter_time

            args = [iter_time, job, self]
            # task_queue.put(args)
            # 调用模拟推理线程
            temp_thread = thread_pool.submit(lambda p: simulate_forward(*p), args)
            temp_thread.result()


