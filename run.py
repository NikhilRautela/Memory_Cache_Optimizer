#!/usr/bin/env python3
# run.py

import sys
import os
import logging
from app.comparison import app
from app.models import SystemOptimizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # Check for administrator privileges
    is_admin = SystemOptimizer.is_admin()
    
    if not is_admin:
        print("=" * 80)
        print("WARNING: Running without administrator privileges.")
        print("Memory and cache optimization features will be limited.")
        print("To use all features, please run this application with administrator privileges:")
        print("  - Right-click and select 'Run as administrator'")
        print("=" * 80)
        logger.warning("Application started without administrator privileges")
    else:
        print("Running with administrator privileges - all optimization features available.")
        logger.info("Application started with administrator privileges")
    
    try:
        # Start the Flask application
        app.run(debug=True)
    except Exception as e:
        logger.error(f"Error starting the application: {str(e)}")
        sys.exit(1)