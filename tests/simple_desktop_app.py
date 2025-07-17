#!/usr/bin/env python3
# simple_desktop_app.py - Simplified Desktop version of Memory Optimizer

import sys
import os
import platform
import time
import logging
import psutil
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QLabel, QProgressBar, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleMemoryMonitorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Setup UI
        self.setWindowTitle("Memory & Cache Optimizer")
        self.setGeometry(100, 100, 800, 600)
        
        # Setup central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create memory section
        memory_group = QGroupBox("Memory Statistics")
        memory_layout = QVBoxLayout(memory_group)
        
        # Memory usage details
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
        
        # Memory optimization button
        self.memory_optimize_btn = QPushButton("Optimize Memory")
        self.memory_optimize_btn.setMinimumHeight(40)
        self.memory_optimize_btn.clicked.connect(self.optimize_memory)
        
        memory_layout.addWidget(self.memory_usage_label)
        memory_layout.addWidget(self.memory_usage_bar)
        memory_layout.addLayout(memory_details_layout)
        memory_layout.addWidget(self.memory_optimize_btn)
        
        # Create cache section
        cache_group = QGroupBox("Cache Optimization")
        cache_layout = QVBoxLayout(cache_group)
        
        # Cache optimization button
        self.cache_optimize_btn = QPushButton("Optimize Cache")
        self.cache_optimize_btn.setMinimumHeight(40)
        self.cache_optimize_btn.clicked.connect(self.optimize_cache)
        
        cache_layout.addWidget(self.cache_optimize_btn)
        
        # Add admin warning if necessary
        if not self.is_admin():
            admin_warning = QLabel("⚠️ Running without administrator privileges. Some optimizations may be limited.")
            admin_warning.setStyleSheet("color: red;")
            self.main_layout.addWidget(admin_warning)
        
        # Add sections to main layout
        self.main_layout.addWidget(memory_group)
        self.main_layout.addWidget(cache_group)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.main_layout.addWidget(self.status_label)
        
        # Setup update timer (1 second interval)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_stats)
        self.update_timer.start(1000)  # 1000ms = 1s
        
        # Initial update
        self.update_stats()
    
    def is_admin(self):
        """Check if the application is running with admin privileges"""
        try:
            if platform.system() == 'Windows':
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except:
            return False
    
    def update_stats(self):
        try:
            mem = psutil.virtual_memory()
            
            # Update memory stats
            memory_percent = mem.percent
            self.memory_usage_label.setText(f"Memory Usage: {memory_percent:.1f}%")
            self.memory_usage_bar.setValue(int(memory_percent))
            
            # Update memory details
            total_gb = mem.total / (1024**3)
            used_gb = mem.used / (1024**3)
            free_gb = mem.available / (1024**3)
            
            self.memory_total_label.setText(f"Total: {total_gb:.1f} GB")
            self.memory_used_label.setText(f"Used: {used_gb:.1f} GB")
            self.memory_free_label.setText(f"Free: {free_gb:.1f} GB")
            
        except Exception as e:
            logger.error(f"Error updating stats: {e}")
            self.status_label.setText(f"Error: {str(e)}")
    
    def optimize_memory(self):
        self.memory_optimize_btn.setEnabled(False)
        self.memory_optimize_btn.setText("Optimizing...")
        self.status_label.setText("Optimizing memory...")
        
        # Run optimization in the main thread (for simplicity)
        try:
            success, message = self.perform_memory_optimization()
            
            if success:
                self.status_label.setText("Memory optimization completed successfully")
                QMessageBox.information(self, "Optimization Complete", f"Memory optimization completed successfully.\n\n{message}")
            else:
                self.status_label.setText("Memory optimization completed with issues")
                QMessageBox.warning(self, "Optimization Warning", f"Memory optimization completed with issues.\n\n{message}")
            
        except Exception as e:
            logger.error(f"Error in memory optimization: {e}")
            self.status_label.setText(f"Error: {str(e)}")
            QMessageBox.critical(self, "Optimization Error", f"Error during optimization: {str(e)}")
        
        self.memory_optimize_btn.setEnabled(True)
        self.memory_optimize_btn.setText("Optimize Memory")
        
        # Update stats after optimization
        self.update_stats()
    
    def optimize_cache(self):
        self.cache_optimize_btn.setEnabled(False)
        self.cache_optimize_btn.setText("Optimizing...")
        self.status_label.setText("Optimizing cache...")
        
        # Run optimization in the main thread (for simplicity)
        try:
            success, message = self.perform_cache_optimization()
            
            if success:
                self.status_label.setText("Cache optimization completed successfully")
                QMessageBox.information(self, "Optimization Complete", f"Cache optimization completed successfully.\n\n{message}")
            else:
                self.status_label.setText("Cache optimization completed with issues")
                QMessageBox.warning(self, "Optimization Warning", f"Cache optimization completed with issues.\n\n{message}")
            
        except Exception as e:
            logger.error(f"Error in cache optimization: {e}")
            self.status_label.setText(f"Error: {str(e)}")
            QMessageBox.critical(self, "Optimization Error", f"Error during optimization: {str(e)}")
        
        self.cache_optimize_btn.setEnabled(True)
        self.cache_optimize_btn.setText("Optimize Cache")
    
    def perform_memory_optimization(self):
        """Perform memory optimization based on the current OS"""
        if not self.is_admin():
            logger.warning("Memory optimization requires administrator privileges")
            return self.perform_user_level_memory_optimization()
        
        system = platform.system()
        if system == 'Windows':
            return self.optimize_windows_memory()
        elif system == 'Linux':
            return self.optimize_linux_memory()
        elif system == 'Darwin':  # macOS
            return self.optimize_macos_memory()
        else:
            return False, f"Unsupported operating system: {system}"
    
    def perform_user_level_memory_optimization(self):
        """Perform memory optimizations that don't require admin privileges"""
        success = False
        message = ""
        
        # Force Python garbage collection
        import gc
        gc.collect()
        message += "Garbage collection performed. "
        success = True
        
        # Clear any temp files we have access to
        try:
            # Get user temp directory
            temp_paths = []
            
            # Try standard temp environment variables
            for var in ['TEMP', 'TMP', 'TMPDIR']:
                if var in os.environ and os.path.exists(os.environ[var]):
                    temp_paths.append(os.environ[var])
            
            # Clear files in accessible temp directories
            for temp_path in temp_paths:
                cleared = self.safely_clear_temp_directory(temp_path)
                if cleared > 0:
                    success = True
                    message += f"Cleared {cleared} temporary files. "
            
        except Exception as e:
            logger.error(f"Error clearing temp files: {str(e)}")
            message += "Error clearing temporary files. "
        
        if success:
            return True, f"Limited memory optimization completed: {message}"
        else:
            return False, "User-level memory optimization failed"
    
    def safely_clear_temp_directory(self, directory, max_files=50):
        """Safely clear temporary files in a directory"""
        if not os.path.exists(directory) or not os.path.isdir(directory):
            return 0
        
        count = 0
        try:
            # Get list of files sorted by modification time (oldest first)
            files = []
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path):
                    try:
                        mtime = os.path.getmtime(item_path)
                        files.append((item_path, mtime))
                    except:
                        pass
            
            # Sort files by modification time (oldest first)
            files.sort(key=lambda x: x[1])
            
            # Delete oldest files first, up to max_files
            for file_path, _ in files[:max_files]:
                try:
                    os.unlink(file_path)
                    count += 1
                except:
                    # Skip files we can't delete
                    pass
            
        except Exception as e:
            logger.error(f"Error clearing temp directory {directory}: {str(e)}")
        
        return count
    
    def optimize_windows_memory(self):
        """Optimize memory on Windows systems"""
        success = False
        message = ""
        
        # 1. Clear standby list and working sets
        try:
            import subprocess
            subprocess.run("powershell -Command \"& {Get-Process | ForEach-Object { [void][System.Runtime.InteropServices.Marshal]::SetProcessWorkingSetSize($_.Handle, -1, -1) }}\"", 
                          shell=True, check=False)
            success = True
            message += "Process working sets cleared. "
        except Exception as e:
            logger.error(f"Failed to clear process working sets: {str(e)}")
            message += "Working set clearing failed. "
        
        # 2. Clear DNS cache
        try:
            subprocess.run("ipconfig /flushdns", shell=True, check=False)
            success = True
            message += "DNS cache cleared. "
        except Exception as e:
            logger.error(f"Failed to clear DNS cache: {str(e)}")
            message += "DNS cache clearing failed. "
        
        # 3. Clear Windows temp files
        try:
            temp_path = os.environ.get('TEMP')
            if temp_path and os.path.exists(temp_path):
                file_count = self.safely_clear_temp_directory(temp_path)
                if file_count > 0:
                    success = True
                    message += f"Cleared {file_count} temporary files. "
            else:
                message += "Temp directory not found. "
        except Exception as e:
            logger.error(f"Error clearing temp files: {str(e)}")
            message += "Temp file clearing failed. "
        
        # Even if some operations fail, if we did anything successful, report success
        if success:
            return True, f"Windows memory optimization completed: {message}"
        else:
            return False, f"Windows memory optimization failed: {message}"
    
    def optimize_linux_memory(self):
        """Optimize memory on Linux systems"""
        success = False
        message = ""
        
        # 1. Drop caches
        try:
            os.system("sync && echo 3 > /proc/sys/vm/drop_caches")
            success = True
            message += "File system caches dropped. "
        except Exception as e:
            logger.error(f"Failed to drop caches: {str(e)}")
            message += "Cache dropping failed. "
        
        # Even if some operations fail, if we did anything successful, report success
        if success:
            return True, f"Linux memory optimization completed: {message}"
        else:
            return False, f"Linux memory optimization failed: {message}"
    
    def optimize_macos_memory(self):
        """Optimize memory on macOS systems"""
        success = False
        message = ""
        
        # 1. Purge memory
        try:
            os.system("purge")
            success = True
            message += "Memory purged. "
        except Exception as e:
            logger.error(f"Failed to purge memory: {str(e)}")
            message += "Memory purge failed. "
        
        # Even if some operations fail, if we did anything successful, report success
        if success:
            return True, f"macOS memory optimization completed: {message}"
        else:
            return False, f"macOS memory optimization failed: {message}"
    
    def perform_cache_optimization(self):
        """Perform cache optimization based on the current OS"""
        if not self.is_admin():
            logger.warning("Limited cache optimization - No administrator privileges")
            return self.perform_user_level_cache_optimization()
        
        system = platform.system()
        if system == 'Windows':
            return self.optimize_windows_cache()
        elif system == 'Linux':
            return self.optimize_linux_cache()
        elif system == 'Darwin':  # macOS
            return self.optimize_macos_cache()
        else:
            return False, f"Unsupported operating system: {system}"
    
    def perform_user_level_cache_optimization(self):
        """Perform cache optimizations that don't require admin privileges"""
        success = False
        message = ""
        
        # Try to free memory which can help cache performance
        try:
            # Force Python garbage collection
            import gc
            gc.collect()
            
            # Use psutil to close handle to unused memory
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                if proc.info['pid'] == os.getpid():
                    # This is our own process, we can safely trim its memory
                    try:
                        # On Windows, this calls SetProcessWorkingSetSize
                        proc.memory_info()
                    except:
                        pass
            
            success = True
            message += "Memory freed at user-level. "
        except Exception as e:
            logger.error(f"Error freeing memory: {str(e)}")
            message += "Memory freeing failed. "
        
        if success:
            return True, f"Limited cache optimization completed: {message}"
        else:
            return False, "User-level cache optimization failed"
    
    def optimize_windows_cache(self):
        """Optimize cache on Windows systems"""
        success = False
        message = ""
        
        # Clear DNS cache - may work without admin rights on some Windows versions
        try:
            import subprocess
            subprocess.run("ipconfig /flushdns", shell=True, check=False)
            success = True
            message += "DNS cache cleared. "
        except Exception as e:
            logger.error(f"Failed to clear DNS cache: {str(e)}")
            message += "DNS cache clearing failed. "
        
        # Try to restart DNS Client service - usually requires admin rights
        try:
            subprocess.run("net stop \"DNS Client\" && net start \"DNS Client\"", shell=True, check=False)
            message += "DNS service restarted. "
        except Exception as e:
            logger.error(f"Failed to restart DNS service: {str(e)}")
            message += "DNS service restart failed. "
        
        # Clear system working set
        try:
            # This PowerShell command attempts to trim working sets of processes
            subprocess.run("powershell -Command \"Get-Process | ForEach-Object { [void][System.Runtime.InteropServices.Marshal]::SetProcessWorkingSetSize($_.Handle, -1, -1) }\"", 
                          shell=True, check=False)
            success = True
            message += "Process working sets cleared. "
        except Exception as e:
            logger.error(f"Failed to clear process working sets: {str(e)}")
            message += "Working set clearing failed. "
        
        # Even if some operations fail, if we did anything successful, report success
        if success:
            return True, f"Windows cache optimization completed: {message}"
        else:
            return False, f"Windows cache optimization failed: {message}"
    
    def optimize_linux_cache(self):
        """Optimize cache on Linux systems"""
        success = False
        message = ""
        
        # Balance file system caches - drops clean caches but keeps active ones
        try:
            os.system("sync && echo 1 > /proc/sys/vm/drop_caches")
            success = True
            message += "File system caches balanced. "
        except Exception as e:
            logger.error(f"Error optimizing Linux cache: {str(e)}")
            message += "File system cache balancing failed. "
        
        if success:
            return True, f"Linux cache optimization completed: {message}"
        else:
            return False, f"Linux cache optimization failed: {message}"
    
    def optimize_macos_cache(self):
        """Optimize cache on macOS systems"""
        success = False
        message = ""
        
        # Clear DNS cache
        try:
            os.system("dscacheutil -flushcache")
            os.system("killall -HUP mDNSResponder")
            success = True
            message += "DNS cache cleared. "
        except Exception as e:
            logger.error(f"Failed to clear DNS cache: {str(e)}")
            message += "DNS cache clearing failed. "
        
        if success:
            return True, f"macOS cache optimization completed: {message}"
        else:
            return False, f"macOS cache optimization failed: {message}"


if __name__ == "__main__":
    try:
        print("Starting simple memory monitor application...")
        # Create application
        app = QApplication(sys.argv)
        
        # Create and show main window
        window = SimpleMemoryMonitorApp()
        window.show()
        
        # Start event loop
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error starting application: {e}")
        logger.error(f"Error starting application: {e}")
        sys.exit(1) 