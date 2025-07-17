#!/usr/bin/env python3
# desktop_app.py - Desktop version of Memory Optimizer

import sys
import os
import platform
import time
import logging
import threading
import numpy as np
import traceback
import ctypes
from datetime import datetime
import psutil

print("Loading PyQt5 modules...")
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
        QHBoxLayout, QPushButton, QLabel, QProgressBar, QGroupBox,
        QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
        QSplitter, QFrame
    )
    from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QObject, QThread
    from PyQt5.QtGui import QFont, QIcon, QColor
    
except Exception as e:
    print(f"ERROR: Failed to import PyQt5 modules: {e}")
    print(f"Traceback: {traceback.format_exc()}")
    sys.exit(1)

print("Loading application modules...")
try:
    from app.models import MemoryStats, CacheStats, PerformanceMetrics, MemoryOptimizer, CacheOptimizer
    from app.components.memory_graph import MemoryGraph
    from app.components.performance_graphs import PerformanceGraphs
    print("Application modules loaded successfully")
except Exception as e:
    print(f"Error loading application modules: {e}")
    print(f"Traceback: {traceback.format_exc()}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MatplotlibCanvas:
    """Dummy matplotlib canvas class that does nothing"""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = None
        self.axes = None
        
    def update_plot(self, x_data, y_data, color='blue', clear=True, label=None):
        pass
    
    def update_bar_plot(self, data, labels, color='blue'):
        pass


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.
    '''
    finished = pyqtSignal(bool, str, dict, dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(dict)  # Signal for progress updates


class OptimizeWorker(QThread):
    '''
    Worker thread for running optimization tasks
    '''
    def __init__(self, optimize_type):
        super().__init__()
        self.optimize_type = optimize_type
        self.signals = WorkerSignals()
        # Connect the progress signal from signals object
        self.progress = self.signals.progress
    
    def run(self):
        try:
            if self.optimize_type == 'memory':
                # Get before stats
                before_stats = MemoryStats.get_current().to_dict()
                self.signals.progress.emit({'type': 'memory', 'stats': before_stats})
                
                # Run memory optimization
                success, message, details = MemoryOptimizer.optimize_with_details()
                
                # Get after stats
                after_stats = MemoryStats.get_current().to_dict()
                self.signals.progress.emit({'type': 'memory', 'stats': after_stats})
                
                # Store details in class attribute
                MemoryOptimizer.last_optimization_details = details
                
            elif self.optimize_type == 'cache':
                # Get before stats
                before_stats = CacheStats.get_current().to_dict()
                self.signals.progress.emit({'type': 'cache', 'stats': before_stats})
                
                # Run cache optimization
                success, message, details = CacheOptimizer.optimize_with_details()
                
                # Get after stats
                after_stats = CacheStats.get_current().to_dict()
                self.signals.progress.emit({'type': 'cache', 'stats': after_stats})
                
                # Store details in class attribute
                CacheOptimizer.last_optimization_details = details
            else:
                raise ValueError(f"Unknown optimization type: {self.optimize_type}")
            
            # Emit results with details
            self.signals.finished.emit(success, message, before_stats, after_stats)
            
        except Exception as e:
            logger.error(f"Error in optimization worker: {str(e)}")
            self.signals.error.emit(str(e))


class MemoryMonitorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("icon.ico"))
        
        # Initialize data storage
        self.memory_history = []
        self.cache_history = []
        self.timestamps = []
        self.performance_metrics = {
            'response_times': [],
            'throughput': [],
            'page_faults': [],
            'swap_usage': []
        }
        self.optimization_history = {
            'memory': {'before': None, 'after': None, 'details': []},
            'cache': {'before': None, 'after': None, 'details': []}
        }
        
        # Initialize CPU history
        self.cpu_history = []
        
        # Initialize optimization flags
        self.optimization_in_progress = False
        
        # Setup UI
        self.setWindowTitle("Memory & Cache Optimizer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Setup central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # Create tabs
        self.dashboard_tab = QWidget()
        self.memory_tab = QWidget()
        self.cache_tab = QWidget()
        self.optimization_tab = QWidget()
        
        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.memory_tab, "Memory")
        self.tabs.addTab(self.cache_tab, "Cache")
        self.tabs.addTab(self.optimization_tab, "Optimization")
        
        # Setup tabs
        self.setup_dashboard_tab()
        self.setup_memory_tab()
        self.setup_cache_tab()
        self.setup_optimization_tab()
        
        # Setup update timer (1 second interval)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_stats)
        self.update_timer.start(1000)  # 1000ms = 1s
        
        # Check for admin privileges
        is_admin = False
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception as e:
            logger.error(f"Error checking admin privileges: {e}")
        
        if not is_admin:
            QMessageBox.warning(
                self, 
                "Limited Functionality", 
                "This application is running without administrator privileges.\n\n"
                "Some optimization features will be limited. For full functionality, "
                "please restart the application with administrator rights."
            )
        
        # Create memory graph widget
        self.memory_graph = MemoryGraph(self)
        self.main_layout.addWidget(self.memory_graph)
        
        # Create performance graphs widget
        self.performance_graphs = PerformanceGraphs(self)
        
        # Add performance graphs to the dashboard tab
        dashboard_layout = self.dashboard_tab.layout()
        dashboard_layout.addWidget(self.performance_graphs)
        
        # Initial update
        self.update_stats()
    
    def setup_dashboard_tab(self):
        layout = QVBoxLayout(self.dashboard_tab)
        
        # Top section with buttons
        button_layout = QHBoxLayout()
        
        self.memory_optimize_btn = QPushButton("Optimize Memory")
        self.memory_optimize_btn.setMinimumHeight(40)
        self.memory_optimize_btn.clicked.connect(self.optimize_memory)
        
        self.cache_optimize_btn = QPushButton("Optimize Cache")
        self.cache_optimize_btn.setMinimumHeight(40)
        self.cache_optimize_btn.clicked.connect(self.optimize_cache)
        
        button_layout.addWidget(self.memory_optimize_btn)
        button_layout.addWidget(self.cache_optimize_btn)
        
        layout.addLayout(button_layout)
        
        # Main stats display
        stats_layout = QHBoxLayout()
        
        # Memory stats
        memory_group = QGroupBox("Memory Usage")
        memory_layout = QVBoxLayout(memory_group)
        
        self.memory_usage_label = QLabel("Memory Usage: --")
        self.memory_usage_bar = QProgressBar()
        self.memory_usage_bar.setRange(0, 100)
        
        memory_details_layout = QHBoxLayout()
        self.memory_total_label = QLabel("Total: --")
        self.memory_used_label = QLabel("Used: --")
        self.memory_free_label = QLabel("Free: --")
        
        memory_details_layout.addWidget(self.memory_total_label)
        memory_details_layout.addWidget(self.memory_used_label)
        memory_details_layout.addWidget(self.memory_free_label)
        
        memory_layout.addWidget(self.memory_usage_label)
        memory_layout.addWidget(self.memory_usage_bar)
        memory_layout.addLayout(memory_details_layout)
        
        # Cache stats
        cache_group = QGroupBox("Cache Performance")
        cache_layout = QVBoxLayout(cache_group)
        
        self.cache_hit_ratio_label = QLabel("Hit Ratio: --")
        self.cache_hit_ratio_bar = QProgressBar()
        self.cache_hit_ratio_bar.setRange(0, 100)
        
        cache_details_layout = QHBoxLayout()
        self.cache_hits_label = QLabel("Hits: --")
        self.cache_misses_label = QLabel("Misses: --")
        self.cache_access_time_label = QLabel("Access Time: --")
        
        cache_details_layout.addWidget(self.cache_hits_label)
        cache_details_layout.addWidget(self.cache_misses_label)
        cache_details_layout.addWidget(self.cache_access_time_label)
        
        cache_layout.addWidget(self.cache_hit_ratio_label)
        cache_layout.addWidget(self.cache_hit_ratio_bar)
        cache_layout.addLayout(cache_details_layout)
        
        stats_layout.addWidget(memory_group)
        stats_layout.addWidget(cache_group)
        
        layout.addLayout(stats_layout)
        
        # Status section
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
    
    def setup_memory_tab(self):
        layout = QVBoxLayout(self.memory_tab)
        
        # Memory stats table
        self.memory_table = QTableWidget()
        self.memory_table.setColumnCount(2)
        self.memory_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.memory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.memory_table.setRowCount(10)
        
        # Memory optimization button
        self.memory_optimize_detail_btn = QPushButton("Optimize Memory")
        self.memory_optimize_detail_btn.setMinimumHeight(40)
        self.memory_optimize_detail_btn.clicked.connect(self.optimize_memory)
        
        layout.addWidget(self.memory_table)
        layout.addWidget(self.memory_optimize_detail_btn)
    
    def setup_cache_tab(self):
        layout = QVBoxLayout(self.cache_tab)
        
        # Cache stats table
        self.cache_table = QTableWidget()
        self.cache_table.setColumnCount(2)
        self.cache_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.cache_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cache_table.setRowCount(7)
        
        # Cache optimization button
        self.cache_optimize_detail_btn = QPushButton("Optimize Cache")
        self.cache_optimize_detail_btn.setMinimumHeight(40)
        self.cache_optimize_detail_btn.clicked.connect(self.optimize_cache)
        
        layout.addWidget(self.cache_table)
        layout.addWidget(self.cache_optimize_detail_btn)
    
    def setup_optimization_tab(self):
        layout = QVBoxLayout(self.optimization_tab)
        
        # Memory optimization section
        memory_opt_group = QGroupBox("Memory Optimization")
        memory_opt_layout = QVBoxLayout(memory_opt_group)
        
        self.memory_opt_result_label = QLabel("No optimization performed yet")
        
        memory_opt_layout.addWidget(self.memory_opt_result_label)
        
        # Cache optimization section
        cache_opt_group = QGroupBox("Cache Optimization")
        cache_opt_layout = QVBoxLayout(cache_opt_group)
        
        self.cache_opt_result_label = QLabel("No optimization performed yet")
        
        cache_opt_layout.addWidget(self.cache_opt_result_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.memory_optimize_opt_btn = QPushButton("Optimize Memory")
        self.memory_optimize_opt_btn.setMinimumHeight(40)
        self.memory_optimize_opt_btn.clicked.connect(self.optimize_memory)
        
        self.cache_optimize_opt_btn = QPushButton("Optimize Cache")
        self.cache_optimize_opt_btn.setMinimumHeight(40)
        self.cache_optimize_opt_btn.clicked.connect(self.optimize_cache)
        
        button_layout.addWidget(self.memory_optimize_opt_btn)
        button_layout.addWidget(self.cache_optimize_opt_btn)
        
        layout.addWidget(memory_opt_group)
        layout.addWidget(cache_opt_group)
        layout.addLayout(button_layout)
    
    def update_stats(self):
        try:
            # Get current stats
            memory_stats = MemoryStats.get_current()
            cache_stats = CacheStats.get_current()
            perf_metrics = PerformanceMetrics.get_current()
            
            # Get CPU usage
            cpu_percent = psutil.cpu_percent()
            self.cpu_history.append(cpu_percent)
            
            # Convert to dictionaries
            memory_dict = memory_stats.to_dict()
            cache_dict = cache_stats.to_dict()
            perf_dict = perf_metrics.to_dict()
            
            # Store in history
            current_time = datetime.now()
            self.memory_history.append(memory_dict)
            self.cache_history.append(cache_dict)
            self.timestamps.append(current_time)
            
            self.performance_metrics['response_times'].append(perf_dict['response_time'])
            self.performance_metrics['throughput'].append(perf_dict['throughput'])
            self.performance_metrics['page_faults'].append(perf_dict['page_faults'])
            self.performance_metrics['swap_usage'].append(perf_dict['swap_rate'])
            
            # Ensure all arrays have the same length
            min_length = min(
                len(self.memory_history),
                len(self.cache_history),
                len(self.timestamps),
                len(self.cpu_history),
                len(self.performance_metrics['response_times']),
                len(self.performance_metrics['throughput']),
                len(self.performance_metrics['page_faults']),
                len(self.performance_metrics['swap_usage'])
            )
            
            # Trim all arrays to the same length
            self.memory_history = self.memory_history[-min_length:]
            self.cache_history = self.cache_history[-min_length:]
            self.timestamps = self.timestamps[-min_length:]
            self.cpu_history = self.cpu_history[-min_length:]
            self.performance_metrics['response_times'] = self.performance_metrics['response_times'][-min_length:]
            self.performance_metrics['throughput'] = self.performance_metrics['throughput'][-min_length:]
            self.performance_metrics['page_faults'] = self.performance_metrics['page_faults'][-min_length:]
            self.performance_metrics['swap_usage'] = self.performance_metrics['swap_usage'][-min_length:]
            
            # Limit history length to prevent using too much memory
            max_history = 60  # 1 minute at 1 second intervals
            if min_length > max_history:
                self.memory_history = self.memory_history[-max_history:]
                self.cache_history = self.cache_history[-max_history:]
                self.timestamps = self.timestamps[-max_history:]
                self.cpu_history = self.cpu_history[-max_history:]
                self.performance_metrics['response_times'] = self.performance_metrics['response_times'][-max_history:]
                self.performance_metrics['throughput'] = self.performance_metrics['throughput'][-max_history:]
                self.performance_metrics['page_faults'] = self.performance_metrics['page_faults'][-max_history:]
                self.performance_metrics['swap_usage'] = self.performance_metrics['swap_usage'][-max_history:]
            
            # Update all UI components
            self.update_dashboard_ui(memory_dict, cache_dict)
            self.update_memory_tab(memory_dict)
            self.update_cache_tab(cache_dict)
            
            # Update performance graphs
            self.performance_graphs.update_all_graphs(
                self.memory_history,
                self.cpu_history,
                self.cache_history,
                self.performance_metrics,
                self.timestamps
            )
            
        except Exception as e:
            logger.error(f"Error updating stats: {str(e)}")
            self.status_label.setText(f"Error updating stats: {str(e)}")
            
            # Try to recover from error by resetting histories
            try:
                self.memory_history = []
                self.cache_history = []
                self.timestamps = []
                self.cpu_history = []
                self.performance_metrics = {
                    'response_times': [],
                    'throughput': [],
                    'page_faults': [],
                    'swap_usage': []
                }
            except Exception as reset_error:
                logger.error(f"Error resetting histories: {str(reset_error)}")
    
    def update_dashboard_ui(self, memory_dict, cache_dict):
        # Update memory stats
        memory_percent = memory_dict['percent']
        self.memory_usage_label.setText(f"Memory Usage: {memory_percent:.1f}%")
        self.memory_usage_bar.setValue(int(memory_percent))
        
        # Update memory details
        total_gb = memory_dict['total'] / (1024**3)
        used_gb = memory_dict['used'] / (1024**3)
        free_gb = memory_dict['free'] / (1024**3)
        
        self.memory_total_label.setText(f"Total: {total_gb:.1f} GB")
        self.memory_used_label.setText(f"Used: {used_gb:.1f} GB")
        self.memory_free_label.setText(f"Free: {free_gb:.1f} GB")
        
        # Update cache stats
        hit_ratio = cache_dict['hit_ratio'] * 100
        self.cache_hit_ratio_label.setText(f"Hit Ratio: {hit_ratio:.1f}%")
        self.cache_hit_ratio_bar.setValue(int(hit_ratio))
        
        # Update cache details
        self.cache_hits_label.setText(f"Hits: {cache_dict['hits']}")
        self.cache_misses_label.setText(f"Misses: {cache_dict['misses']}")
        self.cache_access_time_label.setText(f"Access Time: {cache_dict['access_time']:.3f} ms")
    
    def update_memory_tab(self, memory_dict):
        # Update memory table
        total_gb = memory_dict['total'] / (1024**3)
        available_gb = memory_dict['available'] / (1024**3)
        used_gb = memory_dict['used'] / (1024**3)
        free_gb = memory_dict['free'] / (1024**3)
        swap_total_gb = memory_dict['swap_total'] / (1024**3)
        swap_used_gb = memory_dict['swap_used'] / (1024**3)
        swap_free_gb = memory_dict['swap_free'] / (1024**3)
        
        memory_items = [
            ("Total Memory", f"{total_gb:.2f} GB"),
            ("Available Memory", f"{available_gb:.2f} GB"),
            ("Used Memory", f"{used_gb:.2f} GB"),
            ("Free Memory", f"{free_gb:.2f} GB"),
            ("Memory Usage", f"{memory_dict['percent']:.1f}%"),
            ("Swap Total", f"{swap_total_gb:.2f} GB"),
            ("Swap Used", f"{swap_used_gb:.2f} GB"),
            ("Swap Free", f"{swap_free_gb:.2f} GB"),
            ("Swap Usage", f"{memory_dict['swap_percent']:.1f}%"),
            ("Last Updated", memory_dict['timestamp'])
        ]
        
        for i, (key, value) in enumerate(memory_items):
            self.memory_table.setItem(i, 0, QTableWidgetItem(key))
            self.memory_table.setItem(i, 1, QTableWidgetItem(value))
    
    def update_cache_tab(self, cache_dict):
        # Update cache table
        cache_items = [
            ("Cache Hits", str(cache_dict['hits'])),
            ("Cache Misses", str(cache_dict['misses'])),
            ("Hit Ratio", f"{cache_dict['hit_ratio']*100:.1f}%"),
            ("Access Time", f"{cache_dict['access_time']:.3f} ms"),
            ("Eviction Rate", f"{cache_dict['eviction_rate']:.3f}"),
            ("Write Back Rate", f"{cache_dict['write_back_rate']:.3f}"),
            ("Last Updated", cache_dict['timestamp'])
        ]
        
        for i, (key, value) in enumerate(cache_items):
            self.cache_table.setItem(i, 0, QTableWidgetItem(key))
            self.cache_table.setItem(i, 1, QTableWidgetItem(value))
    
    def optimize_memory(self):
        try:
            if self.optimization_in_progress:
                return
                
            self.optimization_in_progress = True
            
            # Disable all optimize buttons while running
            self.memory_optimize_btn.setEnabled(False)
            self.memory_optimize_detail_btn.setEnabled(False)
            self.memory_optimize_opt_btn.setEnabled(False)
            self.memory_optimize_btn.setText("Optimizing...")
            self.memory_optimize_detail_btn.setText("Optimizing...")
            self.memory_optimize_opt_btn.setText("Optimizing...")
            self.status_label.setText("Optimizing memory...")
            
            # Create worker thread
            self.memory_worker = OptimizeWorker('memory')
            
            # Connect signals
            self.memory_worker.signals.finished.connect(self.on_memory_optimization_finished)
            self.memory_worker.signals.error.connect(self.on_optimization_error)
            self.memory_worker.signals.progress.connect(self.on_optimization_progress)
            
            # Start worker
            self.memory_worker.start()
            
        except Exception as e:
            logger.error(f"Error starting memory optimization: {str(e)}")
            self.on_optimization_error(str(e))
    
    def optimize_cache(self):
        try:
            if self.optimization_in_progress:
                return
                
            self.optimization_in_progress = True
            
            # Disable all optimize buttons while running
            self.cache_optimize_btn.setEnabled(False)
            self.cache_optimize_detail_btn.setEnabled(False)
            self.cache_optimize_opt_btn.setEnabled(False)
            self.cache_optimize_btn.setText("Optimizing...")
            self.cache_optimize_detail_btn.setText("Optimizing...")
            self.cache_optimize_opt_btn.setText("Optimizing...")
            self.status_label.setText("Optimizing cache...")
            
            # Create worker thread
            self.cache_worker = OptimizeWorker('cache')
            
            # Connect signals
            self.cache_worker.signals.finished.connect(self.on_cache_optimization_finished)
            self.cache_worker.signals.error.connect(self.on_optimization_error)
            self.cache_worker.signals.progress.connect(self.on_optimization_progress)
            
            # Start worker
            self.cache_worker.start()
            
        except Exception as e:
            logger.error(f"Error starting cache optimization: {str(e)}")
            self.on_optimization_error(str(e))
    
    def on_optimization_progress(self, progress_data):
        """Handle progress updates during optimization"""
        try:
            # Update graphs based on progress
            if progress_data['type'] == 'memory':
                self.memory_history.append(progress_data['stats'])
                self.timestamps.append(datetime.now())
            elif progress_data['type'] == 'cache':
                self.cache_history.append(progress_data['stats'])
                self.timestamps.append(datetime.now())
            
            # Update UI
            self.update_stats()
            
        except Exception as e:
            logger.error(f"Error handling optimization progress: {str(e)}")
    
    def on_memory_optimization_finished(self, success, message, before_stats, after_stats):
        try:
            # Re-enable all optimize buttons
            self.memory_optimize_btn.setEnabled(True)
            self.memory_optimize_detail_btn.setEnabled(True)
            self.memory_optimize_opt_btn.setEnabled(True)
            self.memory_optimize_btn.setText("Optimize Memory")
            self.memory_optimize_detail_btn.setText("Optimize Memory")
            self.memory_optimize_opt_btn.setText("Optimize Memory")
            self.status_label.setText("Memory optimization complete")
            
            # Update the graph
            self.memory_graph.update_graph(before_stats, after_stats)
            
            # Create concise message
            if success:
                improvement = before_stats['percent'] - after_stats['percent']
                if improvement > 0.5:
                    concise_msg = f"Memory optimized: {improvement:.1f}% improvement"
                elif improvement > 0:
                    concise_msg = f"Memory slightly optimized: {improvement:.1f}% improvement\nSmall improvements are normal when system is already running efficiently"
                else:
                    concise_msg = "System memory is running efficiently\nNo significant optimization needed"
                
                # Add temp files info
                if any("temp files" in str(detail).lower() for detail in MemoryOptimizer.last_optimization_details):
                    concise_msg += "\nTemp files cleaned"
                    
                # Add explanation for negative or small improvements
                if improvement <= 0.5:
                    concise_msg += "\n\nNote: Small or negative changes can occur due to:"
                    concise_msg += "\n• Active system processes"
                    concise_msg += "\n• Background applications"
                    concise_msg += "\n• System already running optimally"
                
                QMessageBox.information(self, "Optimization Complete", concise_msg)
            else:
                QMessageBox.warning(self, "Optimization Warning", "Memory optimization completed with some issues")
            
            # Store optimization history
            self.optimization_history['memory']['before'] = before_stats
            self.optimization_history['memory']['after'] = after_stats
            self.optimization_history['memory']['details'] = MemoryOptimizer.last_optimization_details
            
            # Update optimization tab
            self.update_memory_optimization_display(before_stats, after_stats, MemoryOptimizer.last_optimization_details)
            
        except Exception as e:
            logger.error(f"Error in memory optimization finished handler: {str(e)}")
            self.on_optimization_error(str(e))
        finally:
            self.optimization_in_progress = False
    
    def on_cache_optimization_finished(self, success, message, before_stats, after_stats):
        try:
            # Re-enable all optimize buttons
            self.cache_optimize_btn.setEnabled(True)
            self.cache_optimize_detail_btn.setEnabled(True)
            self.cache_optimize_opt_btn.setEnabled(True)
            self.cache_optimize_btn.setText("Optimize Cache")
            self.cache_optimize_detail_btn.setText("Optimize Cache")
            self.cache_optimize_opt_btn.setText("Optimize Cache")
            self.status_label.setText("Cache optimization complete")
            
            # Create concise message
            if success:
                concise_msg = "Cache optimized successfully"
                if any("temp files" in str(detail).lower() for detail in CacheOptimizer.last_optimization_details):
                    concise_msg += "\nTemp files cleaned"
                QMessageBox.information(self, "Optimization Complete", concise_msg)
            else:
                QMessageBox.warning(self, "Optimization Warning", "Cache optimization completed with some issues")
            
            # Store optimization history
            self.optimization_history['cache']['before'] = before_stats
            self.optimization_history['cache']['after'] = after_stats
            self.optimization_history['cache']['details'] = CacheOptimizer.last_optimization_details
            
            # Update optimization tab
            self.update_cache_optimization_display(before_stats, after_stats, CacheOptimizer.last_optimization_details)
            
        except Exception as e:
            logger.error(f"Error in cache optimization finished handler: {str(e)}")
            self.on_optimization_error(str(e))
        finally:
            self.optimization_in_progress = False
    
    def on_optimization_error(self, error_message):
        try:
            # Re-enable all optimize buttons
            self.memory_optimize_btn.setEnabled(True)
            self.memory_optimize_detail_btn.setEnabled(True)
            self.memory_optimize_opt_btn.setEnabled(True)
            self.cache_optimize_btn.setEnabled(True)
            self.cache_optimize_detail_btn.setEnabled(True)
            self.cache_optimize_opt_btn.setEnabled(True)
            
            self.memory_optimize_btn.setText("Optimize Memory")
            self.memory_optimize_detail_btn.setText("Optimize Memory")
            self.memory_optimize_opt_btn.setText("Optimize Memory")
            self.cache_optimize_btn.setText("Optimize Cache")
            self.cache_optimize_detail_btn.setText("Optimize Cache")
            self.cache_optimize_opt_btn.setText("Optimize Cache")
            
            self.status_label.setText("Optimization error")
            QMessageBox.critical(self, "Error", f"Optimization failed: {error_message}")
            
        except Exception as e:
            logger.error(f"Error in optimization error handler: {str(e)}")
        finally:
            self.optimization_in_progress = False
    
    def update_memory_optimization_display(self, before_stats, after_stats, details=None):
        # Calculate improvement
        before_percent = before_stats['percent']
        after_percent = after_stats['percent']
        
        if before_percent > 0:
            improvement = ((before_percent - after_percent) / before_percent) * 100
            if improvement > 0.5:
                improvement_text = f"+{improvement:.1f}%"
            elif improvement > 0:
                improvement_text = f"slight improvement ({improvement:.1f}%)"
            else:
                improvement_text = "system already optimal"
        else:
            improvement = 0
            improvement_text = "N/A"
        
        # Create detailed report text
        result_text = f"Memory usage: {before_percent:.1f}% → {after_percent:.1f}% ({improvement_text})"
        
        # Add system status explanation
        if after_percent < 60:
            result_text += "\nSystem Status: Good - Memory usage is within normal range"
        elif after_percent < 80:
            result_text += "\nSystem Status: Fair - Consider closing unused applications"
        else:
            result_text += "\nSystem Status: High - Recommend freeing up memory"
        
        # Add details if available
        if details:
            result_text += "\n\nActions performed:"
            for step in details:
                if isinstance(step, tuple) and len(step) >= 2:
                    step_name, step_result = step[0], step[1]
                    # Skip EmptyStandbyList errors
                    if "EmptyStandbyList.exe" in str(step_result):
                        continue
                    result_text += f"\n• {step_name}: {step_result}"
                else:
                    # Skip if it's a string containing EmptyStandbyList
                    if isinstance(step, str) and "EmptyStandbyList.exe" in step:
                        continue
                    result_text += f"\n• {step}"
        
        # Update result label with rich text
        self.memory_opt_result_label.setText(result_text)
        self.memory_opt_result_label.setWordWrap(True)
    
    def update_cache_optimization_display(self, before_stats, after_stats, details=None):
        # Calculate improvement
        before_ratio = before_stats['hit_ratio']
        after_ratio = after_stats['hit_ratio']
        
        if before_ratio > 0:
            improvement = ((after_ratio - before_ratio) / before_ratio) * 100
            improvement_text = f"+{improvement:.1f}%" if improvement > 0 else f"{improvement:.1f}%"
        else:
            improvement = 0
            improvement_text = "N/A"
        
        # Create detailed report text
        result_text = f"Cache hit ratio improved from {before_ratio*100:.1f}% to {after_ratio*100:.1f}% (Improvement: {improvement_text})"
        
        # Add details if available
        if details:
            result_text += "\n\nActions performed:"
            for step in details:
                if isinstance(step, tuple) and len(step) >= 2:
                    step_name, step_result = step[0], step[1]
                    # Skip EmptyStandbyList errors
                    if "EmptyStandbyList.exe" in str(step_result):
                        continue
                    result_text += f"\n• {step_name}: {step_result}"
                else:
                    # Skip if it's a string containing EmptyStandbyList
                    if isinstance(step, str) and "EmptyStandbyList.exe" in step:
                        continue
                    result_text += f"\n• {step}"
        
        # Update result label with rich text
        self.cache_opt_result_label.setText(result_text)
        self.cache_opt_result_label.setWordWrap(True)


if __name__ == "__main__":
    try:
        print("Starting the application...")
        # Check for admin privileges
        is_admin = False
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception as e:
            logger.error(f"Error checking admin privileges: {e}")
        
        if not is_admin:
            logger.warning("Application started without administrator privileges")
        else:
            logger.info("Application started with administrator privileges")
        
        # Start the application
        print("Creating QApplication...")
        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon("icon.ico"))
        print("Creating main window...")
        window = MemoryMonitorApp()
        print("Showing main window...")
        window.show()
        print("Entering event loop...")
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Error starting the application: {e}")
        print(f"Error starting the application: {e}")
        sys.exit(1) 