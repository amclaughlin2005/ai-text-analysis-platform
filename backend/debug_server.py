#!/usr/bin/env python3

print("=== DEBUG SERVER START ===")
print(f"Python version: {__import__('sys').version}")
print(f"Current directory: {__import__('os').getcwd()}")

try:
    print("1. Testing basic imports...")
    import sys
    import os
    from datetime import datetime
    print("✅ Basic imports OK")
    
    print("2. Testing FastAPI import...")
    from fastapi import FastAPI, HTTPException
    print("✅ FastAPI import OK")
    
    print("3. Testing CORS middleware...")
    from fastapi.middleware.cors import CORSMiddleware
    print("✅ CORS import OK")
    
    print("4. Testing Pydantic...")
    from pydantic import BaseModel
    print("✅ Pydantic import OK")
    
    print("5. Creating FastAPI app...")
    app = FastAPI(title="Debug Server")
    print("✅ App created")
    
    print("6. Adding CORS...")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    print("✅ CORS added")
    
    @app.get("/")
    def root():
        return {"message": "Debug server working", "timestamp": datetime.now().isoformat()}
    
    @app.get("/health")
    def health():
        return {"status": "healthy", "debug": True}
    
    print("7. Routes defined")
    
    print("8. Testing uvicorn import...")
    import uvicorn
    print("✅ uvicorn import OK")
    
    print("9. Starting server...")
    print("   If you see this message, the server should start...")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
    
except Exception as e:
    print(f"❌ Error at step: {e}")
    import traceback
    traceback.print_exc()
