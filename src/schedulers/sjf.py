from typing import List, Optional
from src.schedulers.base import Scheduler, ProcessExecution
from src.process import Process, ProcessState

class SJFScheduler(Scheduler):
    def __init__(self, use_ipc: bool = False):
        super().__init__("SJF", use_ipc)
        self.current_process = None
    
    def get_next_process(self, ready_queue: List[Process]) -> Optional[Process]:
        if not ready_queue:
            return None
            
        # 현재 실행 중인 프로세스가 있다면 계속 실행
        if self.current_process and self.current_process in ready_queue:
            if self.use_ipc and not self.current_process.can_execute(self.completed_processes):
                self.current_process = None
            else:
                return self.current_process
            
        if self.use_ipc:
            # IPC 모드
            eligible_processes = [p for p in ready_queue if p.can_execute(self.completed_processes)]
            if not eligible_processes:
                return None
            shortest_process = min(eligible_processes, key=lambda p: p.remaining_time)
        else:
            # Non-IPC 모드
            shortest_process = min(ready_queue, key=lambda p: p.remaining_time)
            
        self.current_process = shortest_process
        return shortest_process