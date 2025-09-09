#!/usr/bin/env python3
"""
Database initialization script for AI Text Analysis Platform
Run this script to set up the database schema and initial data
"""

import sys
import logging
from database_service import DatabaseInitService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Initialize the database with tables and default settings
    """
    print("🚀 Initializing AI Text Analysis Platform Database...")
    print("=" * 60)
    
    try:
        # Initialize database
        success = DatabaseInitService.initialize_database()
        
        if success:
            print("✅ Database initialization completed successfully!")
            print("")
            print("📊 Database ready for:")
            print("  • Dataset uploads and management")
            print("  • Question and response storage")
            print("  • Word frequency analysis")
            print("  • Background job processing")
            print("  • Application settings management")
            print("")
            print("🚀 You can now start the API server:")
            print("  python3 api_server_db.py")
            
        else:
            print("❌ Database initialization failed!")
            print("Check the logs above for specific error details.")
            return 1
            
    except Exception as e:
        print(f"💥 Initialization error: {e}")
        logger.error(f"Database initialization error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
