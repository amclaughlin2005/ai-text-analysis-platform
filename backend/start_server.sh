#!/bin/bash

echo "🚀 Starting AI-Powered Text Analysis Platform Backend"
echo "=================================================="
echo "Current directory: $(pwd)"
echo "Python version: $(python3 --version)"
echo "=================================================="

echo "📦 Checking FastAPI installation..."
python3 -c "import fastapi; print('✅ FastAPI available')" || { echo "❌ FastAPI not available"; exit 1; }

echo "🚀 Starting server on port 8001..."
python3 working_server.py
