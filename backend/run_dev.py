"""
Development server runner for the AI-Powered Text Analysis Platform
Sets up environment and starts the FastAPI server
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import nltk
        import spacy
        import fastapi
        import sqlalchemy
        print("✅ Core dependencies available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def setup_nltk_data():
    """Download required NLTK data"""
    try:
        import nltk
        
        nltk_downloads = [
            'vader_lexicon', 'punkt', 'stopwords', 'wordnet',
            'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words'
        ]
        
        print("📚 Downloading NLTK data...")
        for download in nltk_downloads:
            try:
                nltk.data.find(f'corpora/{download}')
                print(f"   ✅ {download} - already available")
            except LookupError:
                print(f"   📥 {download} - downloading...")
                nltk.download(download, quiet=True)
                print(f"   ✅ {download} - downloaded")
        
        print("✅ NLTK data setup complete")
        return True
        
    except Exception as e:
        print(f"❌ NLTK setup failed: {e}")
        return False

def check_spacy_model():
    """Check if spaCy model is available"""
    try:
        import spacy
        spacy.load("en_core_web_sm")
        print("✅ spaCy model available")
        return True
    except OSError:
        print("⚠️  spaCy model not found")
        print("   Run: python -m spacy download en_core_web_sm")
        print("   Continuing without spaCy (will use NLTK fallbacks)")
        return False

def setup_environment():
    """Set up environment variables for development"""
    env_vars = {
        'APP_ENV': 'development',
        'DEBUG': 'true',
        'DATABASE_URL': 'sqlite:///./text_analysis_dev.db',
        'LOG_LEVEL': 'INFO',
        'CORS_ORIGINS': '["http://localhost:3000","http://127.0.0.1:3000"]'
    }
    
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
            print(f"   Set {key} = {value}")

def main():
    """Main development server startup"""
    print("🚀 Starting AI-Powered Text Analysis Platform - Development Server")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Set up environment
    print("\n📝 Setting up environment...")
    setup_environment()
    
    # Check dependencies
    print("\n🔍 Checking dependencies...")
    if not check_dependencies():
        print("\n❌ Install dependencies with: pip install -r requirements.txt")
        return False
    
    # Setup NLTK
    print("\n📚 Setting up NLTK...")
    if not setup_nltk_data():
        return False
    
    # Check spaCy (optional)
    print("\n🔍 Checking spaCy...")
    check_spacy_model()
    
    # Start server
    print("\n🚀 Starting FastAPI server...")
    print("   URL: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    print("   API Test: http://localhost:8000/api/analysis/test")
    print("\n   Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server failed to start: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
