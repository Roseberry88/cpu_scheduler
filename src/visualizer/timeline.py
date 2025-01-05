import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple
from src.schedulers.base import ProcessExecution

class TimelineVisualizer:
    def __init__(self):
        self.colors = plt.cm.Set3(np.linspace(0, 1, 10))
    
    def create_timeline_view(self,
                           results: Dict[str, Tuple[List[ProcessExecution], Dict[str, float]]],
                           save_path: str = None):
        """Create a 2x3 grid of timeline views for each scheduler"""
        fig, axs = plt.subplots(2, 3, figsize=(20, 12))
        axs = axs.ravel()
        
        # Get global time range for consistent scaling
        max_time = 0
        for executions, _ in results.values():
            if executions:
                max_time = max(max_time, max(exe.end_time for exe in executions))
        
        # Create process color mapping
        all_processes = set()
        for executions, _ in results.values():
            all_processes.update(exe.process_id for exe in executions)
        process_colors = {pid: self.colors[i % len(self.colors)] 
                         for i, pid in enumerate(sorted(all_processes))}
        
        for (scheduler_name, (executions, metrics)), ax in zip(results.items(), axs):
            # Get unique processes and sort them in reverse order (P1 at top)
            processes = sorted(set(exe.process_id for exe in executions), reverse=True)
            
            # Plot execution blocks
            for i, pid in enumerate(processes):
                process_execs = [exe for exe in executions 
                               if exe.process_id == pid and exe.state.value == "RUNNING"]
                
                for exe in process_execs:
                    ax.barh(y=f'P{pid}', 
                           width=exe.end_time - exe.start_time,
                           left=exe.start_time,
                           color=process_colors[pid],
                           edgecolor='black',
                           alpha=0.7)
            
            # Customize the plot
            ax.set_title(f'{scheduler_name}')
            ax.set_xlabel('Time')
            ax.grid(True, axis='x', alpha=0.3)
            ax.set_xlim(0, max_time)
            
            # Add metrics text
            metrics_text = (f'Avg Wait: {metrics["avg_waiting_time"]:.1f}\n'
                          f'Switches: {metrics["context_switches"]}')
            ax.text(1.02, 0.98, metrics_text,
                   transform=ax.transAxes,
                   verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            plt.close()
        else:
            plt.show()

    def create_timeline_view_with_ipc(self,
                                    ipc_results: Dict[str, Tuple[List[ProcessExecution], Dict[str, float]]],
                                    non_ipc_results: Dict[str, Tuple[List[ProcessExecution], Dict[str, float]]],
                                    save_path: str = None):
        """Create a 2x5 grid of timeline views for IPC and non-IPC schedulers"""
        fig, axs = plt.subplots(2, 5, figsize=(25, 10))
        
        # Get global time range for consistent scaling
        max_time = 0
        for results in [ipc_results, non_ipc_results]:
            for executions, _ in results.values():
                if executions:
                    max_time = max(max_time, max(exe.end_time for exe in executions))
        
        # Create process color mapping
        all_processes = set()
        for results in [ipc_results, non_ipc_results]:
            for executions, _ in results.values():
                all_processes.update(exe.process_id for exe in executions)
        process_colors = {pid: self.colors[i % len(self.colors)] 
                         for i, pid in enumerate(sorted(all_processes))}
        
        # Plot IPC version (first row)
        for i, (scheduler_name, (executions, metrics)) in enumerate(ipc_results.items()):
            self._plot_timeline(axs[0, i], executions, metrics, 
                              f"{scheduler_name}\n(with IPC)", 
                              process_colors, max_time)
        
        # Plot non-IPC version (second row)
        for i, (scheduler_name, (executions, metrics)) in enumerate(non_ipc_results.items()):
            self._plot_timeline(axs[1, i], executions, metrics, 
                              f"{scheduler_name}\n(without IPC)", 
                              process_colors, max_time)
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            plt.close()
        else:
            plt.show()

    def _plot_timeline(self, ax, executions, metrics, title, process_colors, max_time):
        """Helper method to plot individual timeline"""
        # Sort processes in reverse order (P1 at top)
        processes = sorted(set(exe.process_id for exe in executions), reverse=True)
        
        for i, pid in enumerate(processes):
            process_execs = [exe for exe in executions 
                           if exe.process_id == pid and exe.state.value == "RUNNING"]
            
            for exe in process_execs:
                ax.barh(y=f'P{pid}', 
                       width=exe.end_time - exe.start_time,
                       left=exe.start_time,
                       color=process_colors[pid],
                       edgecolor='black',
                       alpha=0.7)
        
        ax.set_title(title)
        ax.set_xlabel('Time')
        ax.grid(True, axis='x', alpha=0.3)
        ax.set_xlim(0, max_time)
        
        metrics_text = (f'Avg Wait: {metrics["avg_waiting_time"]:.1f}\n'
                       f'Switches: {metrics["context_switches"]}')
        ax.text(1.02, 0.98, metrics_text,
               transform=ax.transAxes,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))