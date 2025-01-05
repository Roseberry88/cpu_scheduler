from typing import List, Optional, Dict, Set
from src.schedulers.base import Scheduler, ProcessExecution
from src.process import Process, ProcessState

class IPCScheduler(Scheduler):
    def __init__(self):
        super().__init__("IPC")
        self.dependency_graph: Dict[int, Set[int]] = {}  # process_id -> set of dependent process ids
        self.process_info: Dict[int, Process] = {}  # process_id -> Process object
        
    def build_dependency_graph(self, processes: List[Process]):
        """프로세스 간의 의존성 그래프 구축"""
        self.dependency_graph.clear()
        self.process_info.clear()
        
        # 각 프로세스의 정보와 의존성 관계 기록
        for process in processes:
            self.dependency_graph[process.process_id] = set()
            self.process_info[process.process_id] = process
            
        # 의존성 그래프 구축
        for process in processes:
            for dep_id in process.dependencies:
                if dep_id in self.dependency_graph:
                    self.dependency_graph[dep_id].add(process.process_id)
    
    def get_dependency_chain_length(self, process_id: int, visited: Set[int]) -> int:
        """특정 프로세스에 의존하는 전체 체인의 길이를 계산"""
        if process_id in visited:
            return 0
        visited.add(process_id)
        
        max_chain = 0
        for dependent_id in self.dependency_graph[process_id]:
            chain_length = self.get_dependency_chain_length(dependent_id, visited)
            max_chain = max(max_chain, chain_length)
        
        return max_chain + 1
    
    def get_next_process(self, ready_queue: List[Process]) -> Optional[Process]:
        """
        다음에 실행할 프로세스를 선택
        1. 의존성이 없는 프로세스 우선
        2. 의존성이 있는 프로세스 중 모든 선행 프로세스가 완료된 것
        3. 가장 긴 의존성 체인을 가진 프로세스 우선
        4. 도착 시간이 빠른 순서
        """
        if not ready_queue:
            return None
            
        # 실행 가능한 프로세스들 찾기
        eligible_processes = [
            p for p in ready_queue 
            if p.can_execute(self.completed_processes)
        ]
        
        if not eligible_processes:
            return None
        
        # 1. 의존성이 없는 프로세스들 찾기
        independent_processes = [p for p in eligible_processes if not p.dependencies]
        
        if independent_processes:
            # 의존성이 없는 프로세스 중에서:
            # 1) 자신에게 의존하는 프로세스의 수가 많은 순
            # 2) 도착 시간이 빠른 순
            return max(
                independent_processes,
                key=lambda p: (
                    len(self.dependency_graph[p.process_id]),
                    -p.arrival_time
                )
            )
        
        # 2. 의존성이 있는 프로세스 중에서 선택
        # 의존성 체인의 길이가 가장 긴 프로세스 선택
        return max(
            eligible_processes,
            key=lambda p: (
                self.get_dependency_chain_length(p.process_id, set()),
                len(self.dependency_graph[p.process_id]),
                -p.arrival_time
            )
        )
    
    def schedule(self, processes: List[Process]) -> List[ProcessExecution]:
        """의존성 그래프를 구축하고 스케줄링 수행"""
        self.build_dependency_graph(processes)
        return super().schedule(processes)