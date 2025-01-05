from typing import List, Optional
from src.schedulers.base import Scheduler, ProcessExecution
from src.process import Process, ProcessState

class FCFSScheduler(Scheduler):
    def __init__(self, use_ipc: bool = False):
        super().__init__("FCFS", use_ipc)
    
    def get_next_process(self, ready_queue: List[Process]) -> Optional[Process]:
        """FCFS는 큐의 맨 앞에 있는 프로세스를 선택"""
        if not ready_queue:
            return None
            
        if self.use_ipc:
            # IPC 모드에서는 의존성 체크
            for process in ready_queue:
                if process.can_execute(self.completed_processes):
                    return process
            return None
        else:
            # Non-IPC 모드에서는 단순히 첫 번째 프로세스 반환
            return ready_queue[0]