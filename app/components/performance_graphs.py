from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

class PerformanceGraphs(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        
        # Create stats panel
        self.stats_panel = QFrame()
        self.stats_panel.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.stats_layout = QHBoxLayout()
        self.stats_panel.setLayout(self.stats_layout)
        
        # Create stat labels
        self.memory_stat = QLabel("Memory: --")
        self.cpu_stat = QLabel("CPU: --")
        self.cache_stat = QLabel("Cache Hit: --")
        self.page_stat = QLabel("Page Faults: --")
        
        for label in [self.memory_stat, self.cpu_stat, self.cache_stat, self.page_stat]:
            label.setStyleSheet("QLabel { font-size: 12pt; padding: 5px; }")
            self.stats_layout.addWidget(label)
        
        self.layout.addWidget(self.stats_panel)
        
        # Create two rows of graphs
        self.top_row = QHBoxLayout()
        self.bottom_row = QHBoxLayout()
        
        # Memory Usage Graph
        self.memory_figure = Figure(figsize=(6, 4))
        self.memory_canvas = FigureCanvas(self.memory_figure)
        self.top_row.addWidget(self.memory_canvas)
        
        # CPU Usage Graph
        self.cpu_figure = Figure(figsize=(6, 4))
        self.cpu_canvas = FigureCanvas(self.cpu_figure)
        self.top_row.addWidget(self.cpu_canvas)
        
        # Cache Performance Graph
        self.cache_figure = Figure(figsize=(6, 4))
        self.cache_canvas = FigureCanvas(self.cache_figure)
        self.bottom_row.addWidget(self.cache_canvas)
        
        # Page Faults Graph
        self.page_figure = Figure(figsize=(6, 4))
        self.page_canvas = FigureCanvas(self.page_figure)
        self.bottom_row.addWidget(self.page_canvas)
        
        # Add rows to main layout
        self.layout.addLayout(self.top_row)
        self.layout.addLayout(self.bottom_row)
        self.setLayout(self.layout)
        
        # Set style
        plt.style.use('bmh')
        
    def update_memory_graph(self, history_data, timestamps):
        """Update memory usage over time graph"""
        try:
            self.memory_figure.clear()
            ax = self.memory_figure.add_subplot(111)
            
            memory_usage = [d['percent'] for d in history_data]
            
            # Ensure timestamps and memory_usage have the same length
            min_len = min(len(timestamps), len(memory_usage))
            timestamps = timestamps[-min_len:]
            memory_usage = memory_usage[-min_len:]
            
            # Create line plot with gradient
            ax.plot(range(len(memory_usage)), memory_usage, color='#2ecc71', linewidth=2, label='Usage')
            ax.fill_between(range(len(memory_usage)), memory_usage, alpha=0.2, color='#2ecc71')
            
            # Add trend line
            if len(memory_usage) > 1:
                z = np.polyfit(range(len(memory_usage)), memory_usage, 1)
                p = np.poly1d(z)
                ax.plot(range(len(memory_usage)), p(range(len(memory_usage))), "r--", alpha=0.8, label='Trend')
            
            ax.set_title('Memory Usage Over Time')
            ax.set_ylabel('Memory Usage (%)')
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # Update stats
            if memory_usage:
                current = memory_usage[-1]
                avg = sum(memory_usage) / len(memory_usage)
                self.memory_stat.setText(f"Memory: {current:.1f}% (Avg: {avg:.1f}%)")
            
            # Format x-axis
            ax.set_xticks(range(0, len(memory_usage), max(1, len(memory_usage) // 5)))
            ax.set_xticklabels([t.strftime('%H:%M:%S') for t in timestamps[::max(1, len(memory_usage) // 5)]], rotation=45)
            
            self.memory_figure.tight_layout()
            self.memory_canvas.draw()
        except Exception as e:
            print(f"Error updating memory graph: {str(e)}")
        
    def update_cpu_graph(self, cpu_history):
        """Update CPU usage graph"""
        try:
            self.cpu_figure.clear()
            ax = self.cpu_figure.add_subplot(111)
            
            x_range = range(len(cpu_history))
            
            # Create line plot with gradient
            ax.plot(x_range, cpu_history, color='#3498db', linewidth=2, label='Usage')
            ax.fill_between(x_range, cpu_history, alpha=0.2, color='#3498db')
            
            # Add moving average
            if len(cpu_history) > 5:
                window_size = 5
                moving_avg = np.convolve(cpu_history, np.ones(window_size)/window_size, mode='valid')
                ax.plot(range(window_size-1, len(cpu_history)), moving_avg, 'r--', label='Moving Avg')
            
            ax.set_title('CPU Usage Over Time')
            ax.set_ylabel('CPU Usage (%)')
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # Update stats
            if cpu_history:
                current = cpu_history[-1]
                avg = sum(cpu_history) / len(cpu_history)
                self.cpu_stat.setText(f"CPU: {current:.1f}% (Avg: {avg:.1f}%)")
            
            self.cpu_figure.tight_layout()
            self.cpu_canvas.draw()
        except Exception as e:
            print(f"Error updating CPU graph: {str(e)}")
        
    def update_cache_graph(self, cache_history):
        """Update cache performance graph"""
        try:
            self.cache_figure.clear()
            ax = self.cache_figure.add_subplot(111)
            
            hit_ratios = [d['hit_ratio'] * 100 for d in cache_history]
            x_range = range(len(hit_ratios))
            
            # Create line plot with gradient
            ax.plot(x_range, hit_ratios, color='#e74c3c', linewidth=2, label='Hit Ratio')
            ax.fill_between(x_range, hit_ratios, alpha=0.2, color='#e74c3c')
            
            # Add efficiency threshold line
            if hit_ratios:
                threshold = 80
                ax.axhline(y=threshold, color='g', linestyle='--', alpha=0.5, label='Efficiency Threshold')
            
            ax.set_title('Cache Hit Ratio Over Time')
            ax.set_ylabel('Hit Ratio (%)')
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # Update stats
            if hit_ratios:
                current = hit_ratios[-1]
                avg = sum(hit_ratios) / len(hit_ratios)
                self.cache_stat.setText(f"Cache Hit: {current:.1f}% (Avg: {avg:.1f}%)")
            
            self.cache_figure.tight_layout()
            self.cache_canvas.draw()
        except Exception as e:
            print(f"Error updating cache graph: {str(e)}")
        
    def update_page_faults_graph(self, perf_metrics):
        """Update page faults graph"""
        try:
            self.page_figure.clear()
            ax = self.page_figure.add_subplot(111)
            
            page_faults = perf_metrics['page_faults']
            x_range = range(len(page_faults))
            
            # Create bar plot with color gradient based on value
            max_faults = max(page_faults) if page_faults else 1
            colors = plt.cm.RdYlGn_r(np.array(page_faults) / max_faults)
            ax.bar(x_range, page_faults, color=colors, alpha=0.7)
            
            # Add trend line
            if len(page_faults) > 1:
                z = np.polyfit(x_range, page_faults, 1)
                p = np.poly1d(z)
                ax.plot(x_range, p(x_range), "r--", alpha=0.8, label='Trend')
                ax.legend()
            
            ax.set_title('Page Faults Over Time')
            ax.set_ylabel('Page Faults')
            ax.grid(True, axis='y', alpha=0.3)
            
            # Update stats
            if page_faults:
                current = page_faults[-1]
                avg = sum(page_faults) / len(page_faults)
                self.page_stat.setText(f"Page Faults: {current} (Avg: {avg:.1f})")
            
            self.page_figure.tight_layout()
            self.page_canvas.draw()
        except Exception as e:
            print(f"Error updating page faults graph: {str(e)}")
        
    def update_all_graphs(self, memory_history, cpu_history, cache_history, perf_metrics, timestamps):
        """Update all performance graphs"""
        try:
            self.update_memory_graph(memory_history, timestamps)
            self.update_cpu_graph(cpu_history)
            self.update_cache_graph(cache_history)
            self.update_page_faults_graph(perf_metrics)
        except Exception as e:
            print(f"Error updating all graphs: {str(e)}") 