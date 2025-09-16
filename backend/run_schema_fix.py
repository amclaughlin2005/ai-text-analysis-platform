#!/usr/bin/env python3
"""
Run the schema fix on Railway environment
"""

import os
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the schema fix
from fix_railway_schema import main

if __name__ == "__main__":
    success = main()
    print(f"Schema fix {'succeeded' if success else 'failed'}")
    sys.exit(0 if success else 1)
