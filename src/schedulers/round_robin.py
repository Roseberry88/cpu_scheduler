from typing import List, Optional
from src.schedulers.base import Scheduler, ProcessExecution
from src.process import Process, ProcessState

class RoundRobinScheduler(Scheduler):
    def __init__(self, time_quantum: int = None, use_ipc: bool = False):
        super().__init__("Round Robin", use_ipc)
        self.time_quantum = time_quantum if time_quantum is not None else random.randint(1, 10)
        self.current_process = None
        self.current_quantum = 0
    
    def get_next_process(self, ready_queue: List[Process]) -> Optional[Process]:
        if not ready_queue:
            return None
            
        # time quantum을 다 사용했거나 현재 프로세스가 없는 경우
        if (self.current_process is None or 
            self.current_quantum >= self.time_quantum or
            self.current_process not in ready_queue):
            
            if self.use_ipc:
                # IPC 모드
                if self.current_process in ready_queue:
                    # 현재 프로세스를 큐의 맨 뒤로
                    ready_queue.remove(self.current_process)
                    ready_queue.append(self.current_process)
                
                # 실행 가능한 프로세스 찾기
                for _ in range(len(ready_queue)):
                    process = ready_queue[0]
                    if process.can_execute(self.completed_processes):
                        self.current_process = process
                        self.current_quantum = 0
                        return process
                    ready_queue.append(ready_queue.pop(0))
                return None
            else:
                # Non-IPC 모드
                if self.current_process in ready_queue:
                    # 현재 프로세스를 큐의 맨 뒤로
                    ready_queue.remove(self.current_process)
                    ready_queue.append(self.current_process)
                
                self.current_process = ready_queue[0]
                self.current_quantum = 0
                return self.current_process
        
        # time quantum이 남아있으면 현재 프로세스 계속 실행
        self.current_quantum += 1
        return self.current_process