import random
import json
import os
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple

class QueueType(Enum):
    FCFS = "FCFS"
    SJF = "SJF"
    RR = "RR"

class QueueLevel(Enum):
    A = "A"  # FCFS
    B = "B"  # SJF
    C = "C"  # RR

class ProcessState(Enum):
    NEW = "NEW"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    TERMINATED = "TERMINATED"

@dataclass
class Process:
    process_id: int
    arrival_time: int
    burst_time: int
    priority: int
    queue_level: QueueLevel
    dependencies: List[int]
    
    # Runtime attributes
    remaining_time: int = 0
    start_time: int = 0
    completion_time: int = 0
    waiting_time: int = 0
    turnaround_time: int = 0
    state: ProcessState = ProcessState.NEW
    current_quantum: int = 0
    
    def __post_init__(self):
        self.remaining_time = self.burst_time
    
    @property
    def queue_type(self) -> QueueType:
        if self.queue_level == QueueLevel.A:
            return QueueType.FCFS
        elif self.queue_level == QueueLevel.B:
            return QueueType.SJF
        else:  # QueueLevel.C
            return QueueType.RR
    
    def is_dependent_on(self, process_id: int) -> bool:
        return process_id in self.dependencies
    
    def can_execute(self, completed_processes: List[int]) -> bool:
        return all(dep in completed_processes for dep in self.dependencies)
    
    def reset(self):
        self.remaining_time = self.burst_time
        self.start_time = 0
        self.completion_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0
        self.state = ProcessState.NEW
        self.current_quantum = 0
        
    def copy(self):
        return Process(
            process_id=self.process_id,
            arrival_time=self.arrival_time,
            burst_time=self.burst_time,
            priority=self.priority,
            queue_level=self.queue_level,
            dependencies=self.dependencies.copy()
        )

    def to_dict(self) -> Dict:
        """Process 객체를 dictionary로 변환"""
        return {
            "process_id": self.process_id,
            "arrival_time": self.arrival_time,
            "burst_time": self.burst_time,
            "priority": self.priority,
            "queue_level": self.queue_level.value,
            "dependencies": self.dependencies
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Process':
        """Dictionary에서 Process 객체 생성"""
        return cls(
            process_id=data["process_id"],
            arrival_time=data["arrival_time"],
            burst_time=data["burst_time"],
            priority=data["priority"],
            queue_level=QueueLevel[data["queue_level"]],
            dependencies=data["dependencies"]
        )

def save_processes(processes: List[Process], time_quantum: int = 4, 
                  mlq_algorithms: Dict[str, str] = None, 
                  filename: str = "process_config.json"):
    """프로세스 설정을 JSON 파일로 저장"""
    if mlq_algorithms is None:
        mlq_algorithms = {
            "A": "RR",
            "B": "FCFS",
            "C": "SJF"
        }
        
    data = {
        "processes": [p.to_dict() for p in processes],
        "metadata": {
            "scheduler_settings": {
                "time_quantum": time_quantum,
                "mlq_algorithms": mlq_algorithms
            }
        }
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def load_processes(filename: str = "process_config.json") -> Tuple[Optional[List[Process]], Optional[Dict]]:
    """JSON 파일에서 프로세스 설정과 스케줄러 설정 불러오기"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            processes = [Process.from_dict(p) for p in data["processes"]]
            scheduler_settings = data.get("metadata", {}).get("scheduler_settings", {})
            return processes, scheduler_settings
    except FileNotFoundError:
        return None, None

def create_processes(num_processes: int = 10, max_dependencies: int = 3) -> Tuple[List[Process], Dict]:
    """프로세스 생성 또는 불러오기"""
    config_file = "process_config.json"
    loaded_data = load_processes(config_file)
    
    if loaded_data[0] is not None:
        print(f"Configuration loaded from {config_file}")
        return loaded_data
    
    # 설정 파일이 없으면 새로 생성
    print(f"No configuration file found. Creating new processes...")
    processes = []
    priorities = list(range(1, num_processes + 1))
    random.shuffle(priorities)

    # 프로세스 생성
    for i in range(num_processes):
        process = Process(
            process_id=i+1,
            arrival_time=random.randint(0, 20),
            burst_time=random.randint(10, 20),
            priority=priorities[i],
            queue_level=random.choice(list(QueueLevel)),
            dependencies=[]
        )
        processes.append(process)
    
    # 의존성 설정
    if max_dependencies > 0:
        num_dependent = min(max_dependencies + 1, num_processes)
        dependent_processes = random.sample(processes, num_dependent)
        
        for i in range(1, len(dependent_processes)):
            dependent_processes[i].dependencies.append(dependent_processes[i-1].process_id)
    
    # 생성된 설정 저장
    scheduler_settings = {
        "time_quantum": 4,
        "mlq_algorithms": {
            "A": "RR",
            "B": "FCFS",
            "C": "SJF"
        }
    }
    save_processes(processes, 
                  scheduler_settings["time_quantum"], 
                  scheduler_settings["mlq_algorithms"],
                  config_file)
    print(f"New configuration saved to {config_file}")
    
    return processes, scheduler_settings