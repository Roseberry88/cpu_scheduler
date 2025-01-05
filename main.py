import random
from src.process import create_processes
from src.schedulers.fcfs import FCFSScheduler
from src.schedulers.sjf import SJFScheduler
from src.schedulers.round_robin import RoundRobinScheduler
from src.schedulers.priority import PriorityScheduler
from src.schedulers.mlq import MLQScheduler
from src.schedulers.ipc import IPCScheduler
from src.visualizer.gantt import GanttVisualizer
from src.visualizer.timeline import TimelineVisualizer

def main():
    # 프로세스 생성
    processes, scheduler_settings = create_processes(num_processes=10)
    time_quantum = scheduler_settings.get("time_quantum", 4)
    mlq_algorithms = scheduler_settings.get("mlq_algorithms", {
        "A": "RR",
        "B": "FCFS",
        "C": "SJF"
    })

    # MLQ 스케줄러 생성 시 time_quantum과 algorithms 전달
    mlq_scheduler = MLQScheduler(
        time_quantum=time_quantum,  # json에서 가져온 값 사용
        use_ipc=True,
        queue_algorithms=mlq_algorithms
    )
    
    # 프로세스 정보 출력
    print("Initial Process Settings:")
    print("=" * 100)
    print(f"{'Process ID':^10} | {'Arrival':^10} | {'Burst':^10} | {'Priority':^10} | {'Queue Level':^12} | {'Dependencies':^20}")
    print("-" * 90)
    for p in processes:
        print(f"{p.process_id:^10} | {p.arrival_time:^10} | {p.burst_time:^10} | {p.priority:^10} | {p.queue_level.value:^12} | {str(p.dependencies):^20}")
    print("=" * 100)
    print()

    # 스케줄러 설정
    print("Scheduler Settings:")
    print("=" * 50)
    print("FCFS: First-Come, First-Served")
    print("SJF: Shortest Job First")
    print(f"Round Robin: Time Quantum = {time_quantum}")
    print("Priority: Preemptive Priority Scheduling")
    print("MLQ: Multi-Level Queue (A-B-C order)")
    print("-" * 30)
    print("MLQ Queue Settings:")
    for level, algorithm in mlq_algorithms.items():
        print(f"Level {level}: {algorithm}")
    print("-" * 30)
    print("IPC: Inter-Process Communication Scheduler")
    print("-" * 50)
    print()
    
    # 스케줄러 인스턴스 생성
    ipc_schedulers = [
        FCFSScheduler(use_ipc=True),
        SJFScheduler(use_ipc=True),
        RoundRobinScheduler(time_quantum=time_quantum, use_ipc=True),
        PriorityScheduler(use_ipc=True),
        MLQScheduler(time_quantum=time_quantum, use_ipc=True, 
                    queue_algorithms=mlq_algorithms)
    ]

    non_ipc_schedulers = [
        FCFSScheduler(use_ipc=False),
        SJFScheduler(use_ipc=False),
        RoundRobinScheduler(time_quantum=time_quantum, use_ipc=False),
        PriorityScheduler(use_ipc=False),
        MLQScheduler(time_quantum=time_quantum, use_ipc=False, 
                    queue_algorithms=mlq_algorithms)
    ]
    
    # 각 스케줄러 실행 및 결과 수집
    ipc_results = {}
    non_ipc_results = {}
    detailed_calculations = []
    
    # IPC 버전 실행
    for scheduler in ipc_schedulers:
        process_copy = [p.copy() for p in processes]
        execution_history = scheduler.schedule(process_copy)
        metrics = scheduler.calculate_metrics()
        ipc_results[scheduler.__class__.__name__] = (execution_history, metrics)

    # Non-IPC 버전 실행
    for scheduler in non_ipc_schedulers:
        process_copy = [p.copy() for p in processes]
        execution_history = scheduler.schedule(process_copy)
        metrics = scheduler.calculate_metrics()
        non_ipc_results[scheduler.__class__.__name__] = (execution_history, metrics)
    
    # 시각화
    visualizer = GanttVisualizer()
    timeline_viz = TimelineVisualizer()
    # 시각화 부분 수정 필요
    visualizer.plot_all_schedulers_with_ipc(ipc_results, non_ipc_results, save_path='gantt_chart.png')
    visualizer.create_performance_comparison_with_ipc(ipc_results, non_ipc_results, save_path='performance_comparison.png')
    timeline_viz.create_timeline_view_with_ipc(ipc_results, non_ipc_results, save_path='timeline_view.png')

    def format_scheduler_name(name):
        """스케줄러 이름을 포맷팅"""
        if name == "MLQScheduler":
            return "MLQ_Scheduler"
        elif name == "FCFSScheduler":
            return "FCFS_Scheduler"
        elif name == "SJFScheduler":
            return "SJF_Scheduler"
        elif name == "RoundRobinScheduler":
            return "Round_Robin_Scheduler"
        elif name == "PriorityScheduler":
            return "Priority_Scheduler"
        return name
    
    # 상세 계산 과정 출력
    print("\n상세 계산 과정:")
    print("=" * 50)
    for calculation in detailed_calculations:
        print(calculation)
    
    # 상세 계산 과정 출력 (IPC와 Non-IPC 결과 모두 출력)
    print("\nIPC 모드 상세 정보:")
    print("=" * 50)
    for scheduler_name, (_, metrics) in ipc_results.items():
        print(f"{format_scheduler_name(scheduler_name)} (with IPC):")
        print(f"Average Waiting Time: {metrics['avg_waiting_time']:.2f}")
        print(f"Average Turnaround Time: {metrics['avg_turnaround_time']:.2f}")
        print(f"CPU Utilization: {metrics['cpu_utilization']:.1f}%")
        print(f"Context Switches: {metrics['context_switches']}")
        print("-" * 30)
            
    print("\nNon-IPC 모드 상세 정보:")
    print("=" * 50)
    for scheduler_name, (_, metrics) in non_ipc_results.items():
        print(f"{format_scheduler_name(scheduler_name)} (without IPC):")
        print(f"Average Waiting Time: {metrics['avg_waiting_time']:.2f}")
        print(f"Average Turnaround Time: {metrics['avg_turnaround_time']:.2f}")
        print(f"CPU Utilization: {metrics['cpu_utilization']:.1f}%")
        print(f"Context Switches: {metrics['context_switches']}")
        print("-" * 30)

if __name__ == "__main__":
    main()