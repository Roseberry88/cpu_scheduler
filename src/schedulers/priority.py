from typing import List, Optional
from src.schedulers.base import Scheduler, ProcessExecution
from src.process import Process, ProcessState

class PriorityScheduler(Scheduler):
    def __init__(self, use_ipc: bool = False):
        super().__init__("Priority", use_ipc)
        self.current_process = None
    
    def get_next_process(self, ready_queue: List[Process]) -> Optional[Process]:
        if not ready_queue:
            return None
            
        if self.use_ipc:
            # IPC 모드
            eligible_processes = [p for p in ready_queue if p.can_execute(self.completed_processes)]
            if not eligible_processes:
                return None
            highest_priority_process = min(eligible_processes, key=lambda p: p.priority)
        else:
            # Non-IPC 모드
            highest_priority_process = min(ready_queue, key=lambda p: p.priority)
        
        if (self.current_process and 
            self.current_process in ready_queue and 
            self.current_process.priority < highest_priority_process.priority):
            return self.current_process
            
        self.current_process = highest_priority_process
        return highest_priority_process