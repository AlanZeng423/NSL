import queue
import threading
import sys

from scheduler import SkipJoinMLFQScheduler, FCFS_Scheduler
from user import RequestGenerator

request_queue = queue.Queue()

if __name__ == '__main__':
    # 保存原始的标准输出流
    # original_stdout = sys.stdout
    output_file_name = "output_16.txt"
    with open(output_file_name, "w") as output_file:
        sys.stdout = output_file

        arrival_rate = 10
        user_thread = RequestGenerator(arrival_rate)
        # scheduler_thread = SkipJoinMLFQScheduler(6, 2, 12)

    # print(scheduler.multi_level_priority_queue)
    #     scheduler_thread = SkipJoinMLFQScheduler(6, 4, 8)  # 85
    # scheduler_thread = FCFS_Scheduler()
    #     scheduler_thread = SkipJoinMLFQScheduler(6, 8, 6)  # 78
        scheduler_thread = SkipJoinMLFQScheduler(6, 16, 6)  # 78
    # scheduler_thread = SkipJoinMLFQScheduler(6, 10, 6) # 74
    # scheduler_thread = SkipJoinMLFQScheduler(6, 12, 6) # 74
    # scheduler_thread = SkipJoinMLFQScheduler(6, 7, 6)  # 80

        print("start")
        print("scheduler: ")
        # print(scheduler_thread.quantum_list)

    # my_thread = threading.Thread(target=run(scheduler))
    # my_thread = threading.Thread(target=run, args=(scheduler,))
    # my_thread.start()
        user_thread.start()
        scheduler_thread.start()
        user_thread.join()
        scheduler_thread.join()
    # my_thread.join()
