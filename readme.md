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
- 비선점 스케줄링
- 도착한 순서대로 프로세스 실행
- `fcfs.py`에 구현

### 2. 최단 작업 우선(SJF: Shortest Job First)
- 비선점 스케줄링
- 실행 시간이 가장 짧은 프로세스 우선 실행
- `sjf.py`에 구현

### 3. 라운드 로빈(Round Robin)
- 선점 스케줄링
- 시간 할당량(Time Quantum) 기반 실행
- 기본 시간 할당량: 4 시간 단위
- `round_robin.py`에 구현

### 4. 우선순위 스케줄링(Priority Scheduling)
- 선점형 우선순위 스케줄링
- 낮은 우선순위 번호가 높은 우선순위를 의미
- `priority.py`에 구현

### 5. 다단계 큐(MLQ: Multi-Level Queue)
- 세 개의 큐 레벨(A, B, C)
- 각 레벨별 다른 알고리즘 사용 가능
- 기본 설정:
  - A 레벨: 라운드 로빈(RR)
  - B 레벨: 선입선출(FCFS)
  - C 레벨: 최단 작업 우선(SJF)
- `mlq.py`에 구현

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
```json
{
    "processes": [
        {
            "process_id": 1,
            "arrival_time": 0,
            "burst_time": 10,
            "priority": 1,
            "queue_level": "A",
            "dependencies": []
        }
    ],
    "metadata": {
        "scheduler_settings": {
            "time_quantum": 4,
            "mlq_algorithms": {
                "A": "RR",
                "B": "FCFS",
                "C": "SJF"
            }
        }
    }
}
```

## 출력 파일
프로그램 실행 시 생성되는 시각화 파일들:
- `gantt_chart.png`: 각 스케줄러의 실행 타임라인
- `performance_comparison.png`: 스케줄러 간 성능 비교
- `timeline_view.png`: 상세 프로세스 실행 시각화