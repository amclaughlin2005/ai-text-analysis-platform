#!/usr/bin/env python3
"""
Simplified entry point for Railway deployment
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Import and run the production server
    from production_server import *
    
    # This will run the uvicorn.run() call from production_server.py
