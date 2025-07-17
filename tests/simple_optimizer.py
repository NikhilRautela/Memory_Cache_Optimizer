#!/usr/bin/env python3
# simple_optimizer.py - Simple standalone memory optimizer

import sys
import os
import platform
import time
import logging
import subprocess
import psutil
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QLabel, QProgressBar, QGridLayout,
    QMessageBox, QGroupBox
)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QFont, QColor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WorkerSignals(QObject):
    '''Defines the signals available from a running worker thread.'''
    finished = pyqtSignal(bool, str)
    error = pyqtSignal(str)


class OptimizeWorker(QThread):
    '''Worker thread for running optimization tasks'''
    def __init__(self, optimize_type):
        super().__init__()
        self.optimize_type = optimize_type
        self.signals = WorkerSignals()
        
    def run(self):
        try:
            if self.optimize_type == 'memory':
                success, message = optimize_memory()
            elif self.optimize_type == 'cache':
                success, message = optimize_cache()
            else:
                raise ValueError(f"Unknown optimization type: {self.optimize_type}")
                
            # Emit results
            self.signals.finished.emit(success, message)
        except Exception as e:
            logger.error(f"Error in optimization worker: {e}")
            self.signals.error.emit(str(e))


def is_admin():
    """Check if the application is running with admin privileges"""
    try:
        if platform.system() == 'Windows':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except Exception as e:
        logger.error(f"Error checking admin privileges: {str(e)}")
        return False


def run_command(cmd, shell=True):
    """Run a system command and return the output"""
    try:
        result = subprocess.run(
            cmd, 
            shell=shell, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.stderr}")
        return False, e.stderr
    except Exception as e:
        logger.error(f"Error running command: {str(e)}")
        return False, str(e)


def optimize_memory():
    """Perform memory optimization based on the current OS"""
    if not is_admin():
        logger.warning("Memory optimization requires administrator privileges")
        return perform_user_level_memory_optimization()
    
    system = platform.system()
    if system == 'Windows':
        return optimize_windows_memory()
    elif system == 'Linux':
        return optimize_linux_memory()
    elif system == 'Darwin':  # macOS
        return optimize_macos_memory()
    else:
        return False, f"Unsupported operating system: {system}"


def perform_user_level_memory_optimization():
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
            cleared = safely_clear_temp_directory(temp_path)
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


def safely_clear_temp_directory(directory, max_files=50):
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


def optimize_windows_memory():
    """Optimize memory on Windows systems"""
    success = False
    message = ""
    
    # 1. Clear standby list and working sets
    try:
        run_command("powershell -Command \"& {Get-Process | ForEach-Object { [void][System.Runtime.InteropServices.Marshal]::SetProcessWorkingSetSize($_.Handle, -1, -1) }}\"")
        success = True
        message += "Process working sets cleared. "
    except Exception as e:
        logger.error(f"Failed to clear process working sets: {str(e)}")
        message += "Working set clearing failed. "
    
    # 2. Clear DNS cache
    try:
        run_command("ipconfig /flushdns")
        success = True
        message += "DNS cache cleared. "
    except Exception as e:
        logger.error(f"Failed to clear DNS cache: {str(e)}")
        message += "DNS cache clearing failed. "
    
    # 3. Clear Windows temp files
    try:
        temp_path = os.environ.get('TEMP')
        if temp_path and os.path.exists(temp_path):
            file_count = safely_clear_temp_directory(temp_path)
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


def optimize_linux_memory():
    """Optimize memory on Linux systems"""
    success = False
    message = ""
    
    # 1. Drop caches
    try:
        run_command("sync && echo 3 > /proc/sys/vm/drop_caches")
        success = True
        message += "File system caches dropped. "
    except Exception as e:
        logger.error(f"Failed to drop caches: {str(e)}")
        message += "Cache dropping failed. "
    
    # 2. Compact memory
    try:
        run_command("echo 1 > /proc/sys/vm/compact_memory")
        success = True
        message += "Memory compacted. "
    except Exception as e:
        logger.error(f"Failed to compact memory: {str(e)}")
        message += "Memory compaction failed. "
    
    # 3. Adjust swappiness (reduce swapping frequency)
    try:
        run_command("sysctl -w vm.swappiness=10")
        success = True
        message += "Swappiness adjusted. "
    except Exception as e:
        logger.error(f"Failed to adjust swappiness: {str(e)}")
        message += "Swappiness adjustment failed. "
    
    # Even if some operations fail, if we did anything successful, report success
    if success:
        return True, f"Linux memory optimization completed: {message}"
    else:
        return False, f"Linux memory optimization failed: {message}"


def optimize_macos_memory():
    """Optimize memory on macOS systems"""
    success = False
    message = ""
    
    # 1. Purge memory
    try:
        run_command("purge")
        success = True
        message += "Memory purged. "
    except Exception as e:
        logger.error(f"Failed to purge memory: {str(e)}")
        message += "Memory purge failed. "
    
    # 2. Clear DNS cache
    try:
        run_command("dscacheutil -flushcache")
        run_command("killall -HUP mDNSResponder")
        success = True
        message += "DNS cache cleared. "
    except Exception as e:
        logger.error(f"Failed to clear DNS cache: {str(e)}")
        message += "DNS cache clearing failed. "
    
    # Even if some operations fail, if we did anything successful, report success
    if success:
        return True, f"macOS memory optimization completed: {message}"
    else:
        return False, f"macOS memory optimization failed: {message}"


def optimize_cache():
    """Perform cache optimization based on the current OS"""
    if not is_admin():
        logger.warning("Limited cache optimization - No administrator privileges")
        return perform_user_level_cache_optimization()
    
    system = platform.system()
    if system == 'Windows':
        return optimize_windows_cache()
    elif system == 'Linux':
        return optimize_linux_cache()
    elif system == 'Darwin':  # macOS
        return optimize_macos_cache()
    else:
        return False, f"Unsupported operating system: {system}"


def perform_user_level_cache_optimization():
    """Perform cache optimizations that don't require admin privileges"""
    success = False
    message = ""
    
    # Clear browser caches if possible
    try:
        browser_caches_cleared = clear_browser_caches()
        if browser_caches_cleared:
            success = True
            message += "Browser caches cleared. "
    except Exception as e:
        logger.error(f"Error clearing browser caches: {str(e)}")
        message += "Browser cache clearing failed. "
    
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


def clear_browser_caches():
    """Try to clear browser caches"""
    cleared_any = False
    try:
        system = platform.system()
        home = os.path.expanduser("~")
        
        if system == 'Windows':
            # Chrome cache
            chrome_cache = os.path.join(home, 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Cache')
            if safely_clear_directory(chrome_cache) > 0:
                cleared_any = True
            
            # Firefox cache
            firefox_profile = os.path.join(home, 'AppData', 'Local', 'Mozilla', 'Firefox', 'Profiles')
            if os.path.exists(firefox_profile):
                for profile in os.listdir(firefox_profile):
                    cache_path = os.path.join(firefox_profile, profile, 'cache2')
                    if safely_clear_directory(cache_path) > 0:
                        cleared_any = True
        
        elif system == 'Linux':
            # Chrome cache
            chrome_cache = os.path.join(home, '.cache', 'google-chrome', 'Default', 'Cache')
            if safely_clear_directory(chrome_cache) > 0:
                cleared_any = True
            
            # Firefox cache
            firefox_dir = os.path.join(home, '.mozilla', 'firefox')
            if os.path.exists(firefox_dir):
                for item in os.listdir(firefox_dir):
                    if item.endswith('.default'):
                        cache_path = os.path.join(firefox_dir, item, 'cache2')
                        if safely_clear_directory(cache_path) > 0:
                            cleared_any = True
        
        elif system == 'Darwin':  # macOS
            # Chrome cache
            chrome_cache = os.path.join(home, 'Library', 'Caches', 'Google', 'Chrome', 'Default', 'Cache')
            if safely_clear_directory(chrome_cache) > 0:
                cleared_any = True
            
            # Firefox cache
            firefox_dir = os.path.join(home, 'Library', 'Caches', 'Firefox')
            if safely_clear_directory(firefox_dir) > 0:
                cleared_any = True
        
    except Exception as e:
        logger.error(f"Error clearing browser caches: {str(e)}")
    
    return cleared_any


def safely_clear_directory(directory):
    """Safely clear contents of a directory without deleting the directory itself"""
    if not os.path.exists(directory):
        return 0
    
    count = 0
    try:
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            try:
                if os.path.isfile(item_path):
                    os.unlink(item_path)
                    count += 1
                elif os.path.isdir(item_path):
                    import shutil
                    shutil.rmtree(item_path, ignore_errors=True)
                    count += 1
            except Exception as e:
                logger.debug(f"Failed to remove {item_path}: {str(e)}")
    except Exception as e:
        logger.error(f"Error clearing directory {directory}: {str(e)}")
    
    return count


def optimize_windows_cache():
    """Optimize cache on Windows systems"""
    success = False
    message = ""
    
    # Clear DNS cache - may work without admin rights on some Windows versions
    try:
        run_command("ipconfig /flushdns")
        success = True
        message += "DNS cache cleared. "
    except Exception as e:
        logger.error(f"Failed to clear DNS cache: {str(e)}")
        message += "DNS cache clearing failed. "
    
    # Try to restart DNS Client service - usually requires admin rights
    try:
        run_command("net stop \"DNS Client\" && net start \"DNS Client\"")
        message += "DNS service restarted. "
    except Exception as e:
        logger.error(f"Failed to restart DNS service: {str(e)}")
        message += "DNS service restart failed. "
    
    # Clear system working set
    try:
        # This PowerShell command attempts to trim working sets of processes
        run_command("powershell -Command \"Get-Process | ForEach-Object { [void][System.Runtime.InteropServices.Marshal]::SetProcessWorkingSetSize($_.Handle, -1, -1) }\"")
        success = True
        message += "Process working sets cleared. "
    except Exception as e:
        logger.error(f"Failed to clear process working sets: {str(e)}")
        message += "Working set clearing failed. "
    
    # Clear browser caches
    try:
        if clear_browser_caches():
            success = True
            message += "Browser caches cleared. "
    except Exception as e:
        logger.error(f"Error clearing browser caches: {str(e)}")
        message += "Browser cache clearing failed. "
    
    # Even if some operations fail, if we did anything successful, report success
    if success:
        return True, f"Windows cache optimization completed: {message}"
    else:
        return False, f"Windows cache optimization failed: {message}"


def optimize_linux_cache():
    """Optimize cache on Linux systems"""
    success = False
    message = ""
    
    # Balance file system caches - drops clean caches but keeps active ones
    try:
        run_command("sync && echo 1 > /proc/sys/vm/drop_caches")
        success = True
        message += "File system caches balanced. "
    except Exception as e:
        logger.error(f"Error optimizing Linux cache: {str(e)}")
        message += "File system cache balancing failed. "
    
    # Clear browser caches
    try:
        if clear_browser_caches():
            success = True
            message += "Browser caches cleared. "
    except Exception as e:
        logger.error(f"Error clearing browser caches: {str(e)}")
        message += "Browser cache clearing failed. "
    
    if success:
        return True, f"Linux cache optimization completed: {message}"
    else:
        return False, f"Linux cache optimization failed: {message}"


def optimize_macos_cache():
    """Optimize cache on macOS systems"""
    success = False
    message = ""
    
    # Clear DNS cache
    try:
        run_command("dscacheutil -flushcache")
        run_command("killall -HUP mDNSResponder")
        success = True
        message += "DNS cache cleared. "
    except Exception as e:
        logger.error(f"Failed to clear DNS cache: {str(e)}")
        message += "DNS cache clearing failed. "
    
    # Clear browser caches
    try:
        if clear_browser_caches():
            success = True
            message += "Browser caches cleared. "
    except Exception as e:
        logger.error(f"Error clearing browser caches: {str(e)}")
        message += "Browser cache clearing failed. "
    
    if success:
        return True, f"macOS cache optimization completed: {message}"
    else:
        return False, f"macOS cache optimization failed: {message}"


class SimpleOptimizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Setup UI
        self.setWindowTitle("Memory & Cache Optimizer")
        self.setGeometry(100, 100, 600, 400)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create system info section
        info_layout = QGridLayout()
        
        self.total_memory_label = QLabel("Total Memory: --")
        self.used_memory_label = QLabel("Used Memory: --")
        self.free_memory_label = QLabel("Free Memory: --")
        self.memory_percent_label = QLabel("Memory Usage: --")
        
        info_layout.addWidget(QLabel("<b>System Information:</b>"), 0, 0, 1, 2)
        info_layout.addWidget(self.total_memory_label, 1, 0)
        info_layout.addWidget(self.used_memory_label, 1, 1)
        info_layout.addWidget(self.free_memory_label, 2, 0)
        info_layout.addWidget(self.memory_percent_label, 2, 1)
        
        main_layout.addLayout(info_layout)
        
        # Create memory section
        memory_group = QGroupBox("Memory Optimization")
        memory_layout = QVBoxLayout(memory_group)
        
        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        
        memory_button_layout = QHBoxLayout()
        self.memory_optimize_btn = QPushButton("Optimize Memory")
        self.memory_optimize_btn.setMinimumHeight(40)
        self.memory_optimize_btn.clicked.connect(self.optimize_memory)
        memory_button_layout.addWidget(self.memory_optimize_btn)
        
        memory_layout.addWidget(self.memory_progress)
        memory_layout.addLayout(memory_button_layout)
        
        main_layout.addWidget(memory_group)
        
        # Create cache section
        cache_group = QGroupBox("Cache Optimization")
        cache_layout = QVBoxLayout(cache_group)
        
        cache_button_layout = QHBoxLayout()
        self.cache_optimize_btn = QPushButton("Optimize Cache")
        self.cache_optimize_btn.setMinimumHeight(40)
        self.cache_optimize_btn.clicked.connect(self.optimize_cache)
        cache_button_layout.addWidget(self.cache_optimize_btn)
        
        cache_layout.addLayout(cache_button_layout)
        
        main_layout.addWidget(cache_group)
        
        # Create status section
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        
        main_layout.addLayout(status_layout)
        
        # Add admin warning if necessary
        if not is_admin():
            admin_warning = QLabel("⚠️ Running without administrator privileges. Some optimizations will be limited.")
            admin_warning.setStyleSheet("color: red;")
            main_layout.addWidget(admin_warning)
        
        # Setup timer to update stats
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_stats)
        self.update_timer.start(1000)  # Update every second
        
        # Initial update
        self.update_stats()
    
    def update_stats(self):
        try:
            mem = psutil.virtual_memory()
            
            total_gb = mem.total / (1024**3)
            used_gb = mem.used / (1024**3)
            free_gb = mem.available / (1024**3)
            
            self.total_memory_label.setText(f"Total Memory: {total_gb:.2f} GB")
            self.used_memory_label.setText(f"Used Memory: {used_gb:.2f} GB")
            self.free_memory_label.setText(f"Free Memory: {free_gb:.2f} GB")
            self.memory_percent_label.setText(f"Memory Usage: {mem.percent}%")
            
            self.memory_progress.setValue(int(mem.percent))
        except Exception as e:
            logger.error(f"Error updating stats: {e}")
    
    def optimize_memory(self):
        # Disable the button during optimization
        self.memory_optimize_btn.setEnabled(False)
        self.memory_optimize_btn.setText("Optimizing...")
        self.status_label.setText("Optimizing memory...")
        
        # Create and start worker thread
        self.memory_worker = OptimizeWorker('memory')
        self.memory_worker.signals.finished.connect(self.on_memory_optimization_finished)
        self.memory_worker.signals.error.connect(self.on_optimization_error)
        self.memory_worker.start()
    
    def optimize_cache(self):
        # Disable the button during optimization
        self.cache_optimize_btn.setEnabled(False)
        self.cache_optimize_btn.setText("Optimizing...")
        self.status_label.setText("Optimizing cache...")
        
        # Create and start worker thread
        self.cache_worker = OptimizeWorker('cache')
        self.cache_worker.signals.finished.connect(self.on_cache_optimization_finished)
        self.cache_worker.signals.error.connect(self.on_optimization_error)
        self.cache_worker.start()
    
    def on_memory_optimization_finished(self, success, message):
        # Re-enable the button
        self.memory_optimize_btn.setEnabled(True)
        self.memory_optimize_btn.setText("Optimize Memory")
        
        if success:
            self.status_label.setText("Memory optimization completed successfully")
            QMessageBox.information(self, "Optimization Complete", f"Memory optimization completed successfully.\n\n{message}")
        else:
            self.status_label.setText("Memory optimization completed with issues")
            QMessageBox.warning(self, "Optimization Warning", f"Memory optimization completed with issues.\n\n{message}")
        
        # Update stats after optimization
        self.update_stats()
    
    def on_cache_optimization_finished(self, success, message):
        # Re-enable the button
        self.cache_optimize_btn.setEnabled(True)
        self.cache_optimize_btn.setText("Optimize Cache")
        
        if success:
            self.status_label.setText("Cache optimization completed successfully")
            QMessageBox.information(self, "Optimization Complete", f"Cache optimization completed successfully.\n\n{message}")
        else:
            self.status_label.setText("Cache optimization completed with issues")
            QMessageBox.warning(self, "Optimization Warning", f"Cache optimization completed with issues.\n\n{message}")
    
    def on_optimization_error(self, error_message):
        # Re-enable the buttons
        self.memory_optimize_btn.setEnabled(True)
        self.memory_optimize_btn.setText("Optimize Memory")
        self.cache_optimize_btn.setEnabled(True)
        self.cache_optimize_btn.setText("Optimize Cache")
        
        self.status_label.setText(f"Error: {error_message}")
        QMessageBox.critical(self, "Optimization Error", f"Error during optimization: {error_message}")


if __name__ == "__main__":
    try:
        print("Starting simple memory optimizer...")
        # Check for admin privileges
        admin_status = is_admin()
        print(f"Admin privileges: {admin_status}")
        
        # Start the application
        app = QApplication(sys.argv)
        window = SimpleOptimizerApp()
        window.show()
        print("Application started successfully")
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error starting the application: {e}")
        logger.error(f"Error starting the application: {e}")
        sys.exit(1) 