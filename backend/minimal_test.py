#!/usr/bin/env python3

print("Starting minimal test...")

try:
    from fastapi import FastAPI
    print("✅ FastAPI imported")
    
    app = FastAPI()
    print("✅ FastAPI app created")
    
    @app.get("/")
    def read_root():
        return {"Hello": "World"}
    
    print("✅ Route defined")
    
    import uvicorn
    print("✅ uvicorn imported")
    
    print("🚀 Starting server on port 8000...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
