from typing import List, Optional, Dict
from src.schedulers.base import Scheduler, ProcessExecution
from src.process import Process, ProcessState, QueueLevel, QueueType

class MLQScheduler(Scheduler):
    def __init__(self, time_quantum: int = None, use_ipc: bool = False, 
                queue_algorithms: Dict[str, str] = None):
        super().__init__("Multi-Level Queue", use_ipc)
        self.time_quantum = time_quantum
        self.current_process = None
        # 각 레벨별 상태 관리
        self.level_states = {
            QueueLevel.A: {"current_process": None, "current_quantum": 0},
            QueueLevel.B: {"current_process": None, "current_quantum": 0},
            QueueLevel.C: {"current_process": None, "current_quantum": 0}
        }
        self.queues = {
            QueueLevel.A: [],
            QueueLevel.B: [],
            QueueLevel.C: []
        }
        self.queue_algorithms = queue_algorithms or {
            "A": "RR",
            "B": "FCFS",
            "C": "SJF"
        }

    def update_queues(self, ready_queue: List[Process]):
        """ready_queue의 프로세스들을 각각의 레벨 큐로 분류"""
        for level in QueueLevel:
            self.queues[level] = []
        for process in ready_queue:
            self.queues[process.queue_level].append(process)

    def get_next_process_by_algorithm(self, queue: List[Process], algorithm: str, level: QueueLevel) -> Optional[Process]:
        """지정된 알고리즘에 따라 다음 프로세스 선택"""
        if not queue:
            return None
            
        if algorithm == "FCFS":
            # FCFS 로직
            if self.use_ipc:
                for process in queue:
                    if process.can_execute(self.completed_processes):
                        return process
                return None
            return queue[0]
            
        elif algorithm == "SJF":
            # SJF 로직 - level_states 사용
            state = self.level_states[level]
            if state["current_process"] and state["current_process"] in queue:
                if self.use_ipc and not state["current_process"].can_execute(self.completed_processes):
                    state["current_process"] = None
                else:
                    return state["current_process"]
                    
            if self.use_ipc:
                eligible_processes = [p for p in queue if p.can_execute(self.completed_processes)]
                if not eligible_processes:
                    return None
                shortest_process = min(eligible_processes, key=lambda p: p.remaining_time)
            else:
                shortest_process = min(queue, key=lambda p: p.remaining_time)
                
            state["current_process"] = shortest_process
            return shortest_process
            
        elif algorithm == "RR":
            # RR 로직
            state = self.level_states[level]
            
            if (state["current_process"] is None or 
                state["current_quantum"] >= self.time_quantum or
                state["current_process"] not in queue):
                
                if len(queue) == 0:
                    return None
                    
                if state["current_process"] in queue:
                    queue.remove(state["current_process"])
                    queue.append(state["current_process"])
                
                for _ in range(len(queue)):
                    process = queue[0]
                    queue.append(queue.pop(0))
                    
                    if not self.use_ipc or process.can_execute(self.completed_processes):
                        state["current_process"] = process
                        state["current_quantum"] = 0
                        return process
                
                return None
                
            state["current_quantum"] += 1
            return state["current_process"]
    
    def get_next_process(self, ready_queue: List[Process]) -> Optional[Process]:
        """MLQ 방식으로 다음 실행할 프로세스를 선택"""
        self.update_queues(ready_queue)
        
        for level in QueueLevel:
            if self.queues[level]:
                algorithm = self.queue_algorithms[level.value]
                next_process = self.get_next_process_by_algorithm(
                    self.queues[level], 
                    algorithm,
                    level
                )
                if next_process:
                    return next_process
        
        return None