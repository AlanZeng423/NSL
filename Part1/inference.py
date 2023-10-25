import time
from user import Request, JOB_NUM



def simulate_forward(iteration_time, job, scheduler):
    if job.iter_count == 0:
        iteration_time = job.first_iter_time
        time.sleep(iteration_time)
        job.iter_count += 1
        job.to_id += 1
        print(f"THREAD-INFERENCE: Inferring Job{job.j_id}'s TOKEN No.{job.to_id}")
        scheduler.demoteRequest(job)
        return

    iteration_num = scheduler.quantum_list[job.priority]  # 获取当前任务在这次推理中需要执行多少轮

    if iteration_num >= job.output_length - job.iter_count:
        iteration_num = job.output_length - job.iter_count

        for i in range(iteration_num):
            time.sleep(iteration_time)  # ms
            job.iter_count += 1

        jct = time.time() - job.create_time
        scheduler.ave_jct.append(jct)
        # 输出请求的执行过程（每推理一个token输出一行：任务ID、生成token的编号）
        for i in range(iteration_num):
            job.to_id += 1
            print(f"THREAD-INFERENCE: Inferring Job{job.j_id}'s TOKEN No.{job.to_id}")
        print(f"-----------Finished Inference of Job {job.j_id} JCT={jct}-------------")

        scheduler.executed += 1
        print(f"EXECUTED: {scheduler.executed}")
        if scheduler.executed == JOB_NUM:
            print(f"THREAD-SCHEDULER: All Jobs Finished")
            print(f"THREAD-SCHEDULER: Average JCT = {sum(scheduler.ave_jct) / len(scheduler.ave_jct)}")
            print("====================================================================")

    else:
        for i in range(iteration_num):
            time.sleep(iteration_time)  # ms
            job.iter_count += 1

        for i in range(iteration_num):
            job.to_id += 1
            print(f"THREAD-INFERENCE: Inferring Job{job.j_id}'s TOKEN No.{job.to_id}")
        scheduler.demoteRequest(job)

