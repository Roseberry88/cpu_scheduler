import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple
from src.schedulers.base import ProcessExecution
from src.process import ProcessState

class GanttVisualizer:
    def __init__(self):
        self.colors = plt.cm.get_cmap('Set3')
        
    def _create_process_color_map(self, executions: List[ProcessExecution]) -> Dict[int, str]:
        """각 프로세스에 고유한 색상 할당"""
        process_ids = sorted(set(exe.process_id for exe in executions))
        return {
            pid: self.colors(i / len(process_ids))
            for i, pid in enumerate(process_ids)
        }
    
    def plot_single_scheduler(self, 
                            ax: plt.Axes,
                            executions: List[ProcessExecution],
                            scheduler_name: str,
                            process_colors: Dict[int, str]):
        """한 스케줄러의 Gantt Chart 그리기"""
        current_time = 0
        y_position = 0
        
        # 각 실행 구간을 막대로 표시
        for execution in executions:
            if execution.state == ProcessState.RUNNING:
                ax.barh(y_position,
                       execution.end_time - execution.start_time,
                       left=execution.start_time,
                       color=process_colors[execution.process_id],
                       edgecolor='black')
                
                # 프로세스 ID 표시
                ax.text(execution.start_time,
                       y_position,
                       f'P{execution.process_id}',
                       ha='left',
                       va='center')
                
            current_time = max(current_time, execution.end_time)
        
        # 축 설정
        ax.set_xlim(0, current_time)
        ax.set_ylim(-0.5, 0.5)
        ax.set_yticks([])
        ax.set_xlabel('Time')
        ax.set_title(f'{scheduler_name} Scheduler')
        ax.grid(True, axis='x', linestyle='--', alpha=0.7)
        
    def plot_all_schedulers(self,
                          results: Dict[str, Tuple[List[ProcessExecution], Dict[str, float]]],
                          save_path: str = None):
        """모든 스케줄러의 Gantt Chart 비교"""
        n_schedulers = len(results)
        fig, axs = plt.subplots(n_schedulers, 1, figsize=(15, 3 * n_schedulers))
        
        # 단일 스케줄러일 경우 axes를 리스트로 변환
        if n_schedulers == 1:
            axs = [axs]
        
        # 모든 실행 기록을 합쳐서 프로세스별 색상 맵 생성
        all_executions = []
        for executions, _ in results.values():
            all_executions.extend(executions)
        process_colors = self._create_process_color_map(all_executions)
        
        # 각 스케줄러의 Gantt Chart 그리기
        for (scheduler_name, (executions, metrics)), ax in zip(results.items(), axs):
            self.plot_single_scheduler(ax, executions, scheduler_name, process_colors)
            
            # 성능 지표 텍스트 추가
            metrics_text = (
                f'Avg Wait: {metrics["avg_waiting_time"]:.2f}\n'
                f'Avg Turnaround: {metrics["avg_turnaround_time"]:.2f}\n'
                f'CPU Util: {metrics["cpu_utilization"]:.1f}%\n'
                f'Context Switches: {metrics["context_switches"]}'
            )
            ax.text(1.02, 0.5, metrics_text,
                   transform=ax.transAxes,
                   verticalalignment='center',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            plt.close()
        else:
            plt.show()

    def plot_all_schedulers_with_ipc(self,
                                   ipc_results: Dict[str, Tuple[List[ProcessExecution], Dict[str, float]]],
                                   non_ipc_results: Dict[str, Tuple[List[ProcessExecution], Dict[str, float]]],
                                   save_path: str = None):
        """IPC와 Non-IPC 버전의 스케줄러 결과를 2x5 그리드로 시각화"""
        fig, axs = plt.subplots(2, 5, figsize=(25, 8))
        
        # 모든 실행 기록을 합쳐서 프로세스별 색상 맵 생성
        all_executions = []
        for results in [ipc_results, non_ipc_results]:
            for executions, _ in results.values():
                all_executions.extend(executions)
        process_colors = self._create_process_color_map(all_executions)
        
        # IPC 버전 (첫 번째 행)
        for i, (scheduler_name, (executions, metrics)) in enumerate(ipc_results.items()):
            self.plot_single_scheduler(axs[0, i], executions, f"{scheduler_name}\n(with IPC)", process_colors)
            
        # Non-IPC 버전 (두 번째 행)
        for i, (scheduler_name, (executions, metrics)) in enumerate(non_ipc_results.items()):
            self.plot_single_scheduler(axs[1, i], executions, f"{scheduler_name}\n(without IPC)", process_colors)
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            plt.close()
        else:
            plt.show()

    def create_performance_comparison(self,
                                    results: Dict[str, Tuple[List[ProcessExecution], Dict[str, float]]],
                                    save_path: str = None):
        """스케줄러들의 성능 지표 비교 그래프 생성"""
        metrics = ['avg_waiting_time', 'avg_turnaround_time', 'cpu_utilization', 'context_switches']
        metric_labels = ['Average Waiting Time', 'Average Turnaround Time', 
                        'CPU Utilization (%)', 'Context Switches']
        
        schedulers = list(results.keys())
        n_metrics = len(metrics)
        
        fig, axs = plt.subplots(2, 2, figsize=(15, 10))
        axs = axs.ravel()
        
        for i, (metric, label) in enumerate(zip(metrics, metric_labels)):
            values = [results[s][1][metric] for s in schedulers]
            axs[i].bar(schedulers, values)
            axs[i].set_title(label)
            axs[i].tick_params(axis='x', rotation=45)
            axs[i].grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            plt.close()
        else:
            plt.show()

    def create_performance_comparison_with_ipc(self,
                                            ipc_results: Dict[str, Tuple[List[ProcessExecution], Dict[str, float]]],
                                            non_ipc_results: Dict[str, Tuple[List[ProcessExecution], Dict[str, float]]],
                                            save_path: str = None):
        """Create comparison plots for both IPC and non-IPC versions"""
        metrics = ['avg_waiting_time', 'avg_turnaround_time', 'cpu_utilization', 'context_switches']
        metric_labels = ['Average Waiting Time', 'Average Turnaround Time', 
                        'CPU Utilization (%)', 'Context Switches']
        
        fig, axs = plt.subplots(2, 2, figsize=(15, 12))
        axs = axs.ravel()
        
        schedulers = list(ipc_results.keys())
        x = np.arange(len(schedulers))
        width = 0.35
        
        for i, (metric, label) in enumerate(zip(metrics, metric_labels)):
            ipc_values = [ipc_results[s][1][metric] for s in schedulers]
            non_ipc_values = [non_ipc_results[s][1][metric] for s in schedulers]
            
            axs[i].bar(x - width/2, ipc_values, width, label='With IPC')
            axs[i].bar(x + width/2, non_ipc_values, width, label='Without IPC')
            
            axs[i].set_title(label)
            axs[i].set_xticks(x)
            axs[i].set_xticklabels(schedulers, rotation=45)
            axs[i].legend()
            axs[i].grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            plt.close()
        else:
            plt.show()