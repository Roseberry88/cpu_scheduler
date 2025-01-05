# CPU 스케줄러 구현 프로젝트

이 프로젝트는 다양한 CPU 스케줄링 알고리즘을 구현하고, 프로세스 간 통신(IPC)을 지원하며 실행 결과를 시각화하는 프로그램입니다.

## 시작하기

### 필요한 환경
- Python 3.7 이상
- 필수 라이브러리: matplotlib, numpy

### 설치 방법
1. 저장소 복제
2. 필요한 패키지 설치:
```bash
pip install matplotlib numpy
```

### 실행 방법
1. 기본 실행:
```bash
python main.py
```

2. 처음 실행 시:
- 프로그램이 자동으로 `process_config.json` 파일을 생성합니다
- 랜덤한 프로세스 정보가 생성됩니다
- 이후 실행부터는 생성된 설정 파일을 사용합니다

3. 설정 초기화:
- `process_config.json` 파일을 삭제하면 됩니다
- 다음 실행 시 새로운 설정이 생성됩니다

## 구현된 스케줄링 알고리즘

### 1. 선입선출(FCFS: First-Come, First-Served)
- 비선점 스케줄링 방식으로, 가장 기본적인 스케줄링 알고리즘
- 도착한 순서대로 프로세스 실행
- `fcfs.py`에 구현
- 주요 코드 설명:
  ```python
  def get_next_process(self, ready_queue: List[Process]) -> Optional[Process]:
      if not ready_queue:
          return None
      # IPC 모드에서는 의존성을 체크하여 실행 가능한 프로세스 선택
      if self.use_ipc:
          for process in ready_queue:
              if process.can_execute(self.completed_processes):
                  return process
          return None
      # Non-IPC 모드에서는 단순히 첫 번째 프로세스 반환
      return ready_queue[0]
  ```

### 2. 최단 작업 우선(SJF: Shortest Job First)
- 비선점 스케줄링 방식으로, CPU 버스트 시간이 가장 짧은 프로세스를 우선 실행
- 현재 실행 중인 프로세스는 중단되지 않음
- `sjf.py`에 구현
- 주요 코드 설명:
  ```python
  def get_next_process(self, ready_queue: List[Process]) -> Optional[Process]:
      # 현재 실행 중인 프로세스가 있다면 계속 실행
      if self.current_process and self.current_process in ready_queue:
          return self.current_process
      # IPC 모드에서는 의존성을 고려하여 최단 작업 선택
      if self.use_ipc:
          eligible_processes = [p for p in ready_queue 
                              if p.can_execute(self.completed_processes)]
          if not eligible_processes:
              return None
          return min(eligible_processes, key=lambda p: p.remaining_time)
      # Non-IPC 모드에서는 단순히 최단 작업 선택
      return min(ready_queue, key=lambda p: p.remaining_time)
  ```

### 3. 라운드 로빈(Round Robin)
- 선점형 스케줄링으로, 시간 할당량(Time Quantum)을 기반으로 프로세스를 순환 실행
- 기본 시간 할당량: 4 시간 단위
- `round_robin.py`에 구현
- 주요 코드 설명:
  ```python
  def get_next_process(self, ready_queue: List[Process]) -> Optional[Process]:
      # 시간 할당량을 모두 사용했거나 현재 프로세스가 없는 경우
      if (self.current_process is None or 
          self.current_quantum >= self.time_quantum):
          if self.current_process in ready_queue:
              ready_queue.remove(self.current_process)
              ready_queue.append(self.current_process)
          self.current_process = ready_queue[0]
          self.current_quantum = 0
      self.current_quantum += 1
      return self.current_process
  ```

### 4. 우선순위 스케줄링(Priority Scheduling)
- 선점형 우선순위 스케줄링으로, 우선순위가 높은 프로세스를 우선 실행
- 낮은 우선순위 번호가 높은 우선순위를 의미
- `priority.py`에 구현
- 주요 코드 설명:
  ```python
  def get_next_process(self, ready_queue: List[Process]) -> Optional[Process]:
      if self.use_ipc:
          eligible_processes = [p for p in ready_queue 
                              if p.can_execute(self.completed_processes)]
          if not eligible_processes:
              return None
          return min(eligible_processes, key=lambda p: p.priority)
      return min(ready_queue, key=lambda p: p.priority)
  ```

### 5. 다단계 큐(MLQ: Multi-Level Queue)
- 세 개의 큐 레벨(A, B, C)을 사용하는 고급 스케줄링 방식
- 각 레벨별로 다른 스케줄링 알고리즘 적용 가능
- 기본 설정:
  - A 레벨: 라운드 로빈(RR)
  - B 레벨: 선입선출(FCFS)
  - C 레벨: 최단 작업 우선(SJF)
- `mlq.py`에 구현
- 주요 코드 설명:
  ```python
  def get_next_process(self, ready_queue: List[Process]) -> Optional[Process]:
      self.update_queues(ready_queue)  # 각 레벨별 큐 업데이트
      
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
  ```

## 주요 기능

### 1. IPC(프로세스 간 통신) 지원
- 프로세스 간 의존성 구현
- 의존성 체인을 고려한 프로세스 실행
- 모든 스케줄러가 IPC 모드와 비IPC 모드 지원

### 2. 프로세스 설정
- `process_config.json` 파일로 설정 가능
- 설정 가능한 항목:
  - 프로세스 도착 시간
  - 실행 시간
  - 우선순위
  - 큐 레벨
  - 의존성 관계

### 3. 시각화 기능
- 간트 차트(실행 타임라인)
- 성능 비교 그래프
- 타임라인 뷰
- 지표 시각화:
  - 평균 대기 시간
  - 평균 반환 시간
  - CPU 사용률
  - 문맥 교환 횟수

### 4. 성능 측정
- 자동 계산되는 지표들:
  - 평균 대기 시간
  - 평균 반환 시간
  - CPU 사용률 백분율
  - 문맥 교환 횟수
  - 상세 실행 기록

## 프로세스 설정 파일 형식
프로세스의 설정은 JSON 파일을 통해 관리됩니다. 각 필드의 의미는 다음과 같습니다:

### 프로세스 정보 (processes)
```json
{
    "processes": [
        {
            "process_id": 1,      // 프로세스 고유 식별자
            "arrival_time": 0,    // 프로세스 도착 시간
            "burst_time": 10,     // CPU 실행 시간
            "priority": 1,        // 우선순위 (낮을수록 높은 우선순위)
            "queue_level": "A",   // MLQ에서의 큐 레벨 (A, B, C)
            "dependencies": []    // 의존성 있는 프로세스 ID 목록
        }
    ],
    "metadata": {
        "scheduler_settings": {
            "time_quantum": 4,    // 라운드 로빈의 시간 할당량
            "mlq_algorithms": {    // 각 레벨별 스케줄링 알고리즘
                "A": "RR",        // Round Robin
                "B": "FCFS",      // First-Come, First-Served
                "C": "SJF"        // Shortest Job First
            }
        }
    }
}
```

## 출력 파일
프로그램 실행 시 생성되는 시각화 파일들:
- `gantt_chart.png`: 각 스케줄러의 실행 타임라인
![gantt_chart](https://github.com/user-attachments/assets/28e8bc60-3044-48af-ba53-a138ff259d38)
- `performance_comparison.png`: 스케줄러 간 성능 비교
![performance_comparison](https://github.com/user-attachments/assets/8edac56c-0e0a-42b2-a399-dcbcb78270a4)
- `timeline_view.png`: 상세 프로세스 실행 시각화
![timeline_view](https://github.com/user-attachments/assets/72021bac-d1c0-40b3-8be5-608e1814ed4f)
