from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from src.process import Process, ProcessState

@dataclass
class ProcessExecution:
    """프로세스 실행 기록을 저장하는 클래스"""
    process_id: int
    start_time: int
    end_time: int
    state: ProcessState

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
from src.process import Process, ProcessState

@dataclass
class ProcessExecution:
    """프로세스 실행 기록을 저장하는 클래스"""
    process_id: int
    start_time: int
    end_time: int
    state: ProcessState

class Scheduler(ABC):
    def __init__(self, name: str, use_ipc: bool = False):
        self.name = name
        self.use_ipc = use_ipc
        self.current_time = 0
        self.execution_history = []
        self.ready_queue = []
        self.completed_processes = []
        self.context_switches = 0
        self.all_processes = []

    def can_execute(self, process: Process) -> bool:
        """프로세스가 실행 가능한지 확인"""
        if not self.use_ipc:
            return True
        return process.can_execute(self.completed_processes)
    
    @abstractmethod
    def get_next_process(self, ready_queue: List[Process]) -> Optional[Process]:
        """다음에 실행할 프로세스를 선택하는 메서드"""
        pass

    def add_to_history(self, process: Process, start_time: int, end_time: int, state: ProcessState):
        """실행 기록 추가"""
        execution = ProcessExecution(
            process_id=process.process_id,
            start_time=start_time,
            end_time=end_time,
            state=state
        )
        self.execution_history.append(execution)

    def update_process_metrics(self, process: Process):
        """프로세스의 성능 지표 업데이트"""
        process.completion_time = self.current_time
        process.turnaround_time = process.completion_time - process.arrival_time
        process.waiting_time = process.turnaround_time - process.burst_time

    def schedule(self, processes: List[Process]) -> List[ProcessExecution]:
        """프로세스 스케줄링 실행"""
        self.current_time = 0
        self.execution_history = []
        self.ready_queue = []
        self.completed_processes = []
        self.context_switches = 0
        self.all_processes = processes.copy()  # 모든 프로세스 저장
        
        # 모든 프로세스의 상태 초기화
        for process in processes:
            process.reset()
        
        # 모든 프로세스가 완료될 때까지 반복
        while len(self.completed_processes) < len(processes):
            # 현재 시간에 도착한 프로세스들을 ready queue에 추가
            for process in processes:
                if (process.arrival_time == self.current_time and 
                    process.state == ProcessState.NEW):
                    process.state = ProcessState.READY
                    self.ready_queue.append(process)
            
            # 실행 가능한 다음 프로세스 선택
            current_process = self.get_next_process(self.ready_queue)
            
            if current_process:
                # 이전에 실행중이던 프로세스가 있었다면 context switch 발생
                if self.execution_history and self.execution_history[-1].process_id != current_process.process_id:
                    self.context_switches += 1
                
                # 프로세스 실행
                execution_time = min(1, current_process.remaining_time)  # 1 시간 단위로 실행
                current_process.state = ProcessState.RUNNING
                current_process.remaining_time -= execution_time
                
                self.add_to_history(
                    current_process, 
                    self.current_time, 
                    self.current_time + execution_time,
                    ProcessState.RUNNING
                )
                
                # 프로세스가 완료되었는지 확인
                if current_process.remaining_time == 0:
                    current_process.state = ProcessState.TERMINATED
                    self.completed_processes.append(current_process.process_id)
                    self.ready_queue.remove(current_process)
                    self.update_process_metrics(current_process)
            
            self.current_time += 1
            
        return self.execution_history

    def calculate_detailed_metrics(self) -> Tuple[Dict[str, float], str]:
        """스케줄링 성능 지표 계산 및 상세 계산 과정 출력"""
        process_stats = {}
        detailed_output = []
        
        # 스케줄러 이름 출력
        detailed_output.append(f"\n{self.__class__.__name__} 상세 계산 과정:")
        detailed_output.append("=" * 50)
        
        # 모든 프로세스의 arrival_time 설정
        for process in self.all_processes:
            process_stats[process.process_id] = {
                'arrival_time': process.arrival_time,
                'burst_time': process.burst_time,
                'last_end': 0,
                'total_run_time': 0,
                'start_time': float('inf')
            }
        
        # 각 프로세스별로 실행 기록 정리
        for exec in self.execution_history:
            stats = process_stats[exec.process_id]
            stats['last_end'] = max(stats['last_end'], exec.end_time)
            stats['start_time'] = min(stats['start_time'], exec.start_time)
            if exec.state == ProcessState.RUNNING:
                stats['total_run_time'] += (exec.end_time - exec.start_time)
        
        # 전체 지표 계산 및 상세 정보 출력
        total_waiting_time = 0
        total_turnaround_time = 0
        total_processes = len(process_stats)
        
        detailed_output.append("각 프로세스별 계산 과정:")
        detailed_output.append("-" * 50)
        
        for pid, stats in process_stats.items():
            turnaround_time = stats['last_end'] - stats['arrival_time']
            waiting_time = turnaround_time - stats['total_run_time']
            
            process_detail = [
                f"Process {pid}:",
                f"- Arrival Time: {stats['arrival_time']}",
                f"- Burst Time: {stats['burst_time']}",
                f"- First Start Time: {stats['start_time']}",
                f"- Completion Time: {stats['last_end']}",
                f"- Total Run Time: {stats['total_run_time']}",
                f"- Turnaround Time = {stats['last_end']} - {stats['arrival_time']} = {turnaround_time}",
                f"- Waiting Time = {turnaround_time} - {stats['total_run_time']} = {waiting_time}",
                ""
            ]
            detailed_output.extend(process_detail)
            
            total_waiting_time += waiting_time
            total_turnaround_time += turnaround_time
        
        # 평균값 계산 및 출력
        avg_waiting_time = total_waiting_time / total_processes if total_processes > 0 else 0
        avg_turnaround_time = total_turnaround_time / total_processes if total_processes > 0 else 0
        
        summary = [
            "최종 계산 결과:",
            "-" * 30,
            f"Total Waiting Time = {total_waiting_time}",
            f"Average Waiting Time = {total_waiting_time} / {total_processes} = {avg_waiting_time:.2f}",
            f"Total Turnaround Time = {total_turnaround_time}",
            f"Average Turnaround Time = {total_turnaround_time} / {total_processes} = {avg_turnaround_time:.2f}",
            f"Context Switches = {self.context_switches}",
            "=" * 50,
            ""
        ]
        detailed_output.extend(summary)
        
        # CPU 사용률 계산
        total_time = self.current_time
        cpu_busy_time = sum(
            exec.end_time - exec.start_time 
            for exec in self.execution_history 
            if exec.state == ProcessState.RUNNING
        )
        
        metrics = {
            "avg_waiting_time": avg_waiting_time,
            "avg_turnaround_time": avg_turnaround_time,
            "cpu_utilization": (cpu_busy_time / total_time) * 100 if total_time > 0 else 0,
            "context_switches": self.context_switches
        }
        
        return metrics, "\n".join(detailed_output)

    def calculate_metrics(self) -> Dict[str, float]:
        """기존의 성능 지표 계산 메서드"""
        metrics, _ = self.calculate_detailed_metrics()
        return metrics