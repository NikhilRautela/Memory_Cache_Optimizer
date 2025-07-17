#!/usr/bin/env python3
# launcher.py - Central launcher for Memory Optimizer

import os
import sys
import ctypes
import subprocess
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_admin():
    """Check if the application is running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception as e:
        logger.error(f"Error checking admin privileges: {str(e)}")
        return False

def run_command(cmd):
    """Run a system command"""
    try:
        subprocess.Popen(cmd, shell=True)
        return True
    except Exception as e:
        logger.error(f"Error running command: {str(e)}")
        return False

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls')

def print_header():
    """Print application header"""
    print("\n" + "=" * 80)
    print(" " * 25 + "MEMORY & CACHE OPTIMIZER")
    print("=" * 80)
    
    # Show admin status
    is_admin = check_admin()
    if is_admin:
        print("✓ Running with administrator privileges - all optimization features available")
    else:
        print("⚠ Running without administrator privileges - some features will be limited")
    
    print("\nChoose your interface:")
    print("=" * 80)

def main():
    clear_screen()
    print_header()
    
    print("1. Desktop Application (Native UI)")
    print("   - Better performance and responsiveness")
    print("   - Native look and feel")
    print("   - Recommended for most users")
    print("\n2. Web Interface")
    print("   - Access via browser")
    print("   - Works on any system with a web browser")
    print("   - Useful if PyQt5 has issues on your system")
    print("\n0. Exit")
    
    choice = input("\nEnter your choice (0-2): ")
    
    if choice == '1':
        print("\nStarting Desktop Application...")
        run_command("python desktop_app.py")
    elif choice == '2':
        print("\nStarting Web Interface...")
        print("Once started, access the application at: http://localhost:5000")
        run_command("python run.py")
    elif choice == '0':
        print("\nExiting. Thank you for using Memory & Cache Optimizer!")
        sys.exit(0)
    else:
        print("\nInvalid choice. Please try again.")
        time.sleep(1)
        main()  # Restart the menu

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting. Thank you for using Memory & Cache Optimizer!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\nAn unexpected error occurred: {str(e)}")
        sys.exit(1) 