# AI Text Analysis Platform - Deployment Guide

## 🚀 Production Deployment Setup

This guide walks you through deploying the AI Text Analysis Platform to production using:
- **Frontend**: Vercel (Next.js hosting)
- **Backend**: Railway (Python FastAPI + PostgreSQL)
- **Code Repository**: GitHub

---

## 📋 Pre-Deployment Checklist

### ✅ **Development Complete**
- [x] Frontend React application built and tested
- [x] Backend FastAPI with database persistence
- [x] Word cloud visualization with column filtering
- [x] CSV upload and processing
- [x] Noise word filtering system

### 🔧 **Production Preparation**
- [ ] Environment variables configured
- [ ] Database migration to PostgreSQL
- [ ] Build scripts optimized
- [ ] Error handling enhanced
- [ ] Security headers configured

---

## 🏗️ **Architecture Overview**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vercel        │    │    Railway      │    │   GitHub        │
│   (Frontend)    │    │   (Backend)     │    │   (Source)      │
│                 │    │                 │    │                 │
│ Next.js 14      │◄──►│ FastAPI         │    │ Main Branch     │
│ React + Tailwind│    │ SQLAlchemy      │    │ Auto-deploy     │
│ Word Cloud UI   │    │ PostgreSQL      │    │ Webhooks        │
│                 │    │ File Storage    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 📦 **Step 1: Prepare for Production**

### Backend Production Requirements

1. **Database Migration**: SQLite → PostgreSQL
2. **File Storage**: Local uploads → Railway storage or S3
3. **Environment Variables**: Production secrets
4. **CORS Configuration**: Allow Vercel domain
5. **Logging**: Production-level logging

### Frontend Production Requirements

1. **API URLs**: Point to Railway backend
2. **Environment Variables**: Production API endpoints
3. **Build Optimization**: Next.js production build
4. **CSP Headers**: Allow Railway backend domain

---

## 🔑 **Step 2: Environment Variables Setup**

### **Frontend (.env.production)**
```bash
# Production API Configuration
NEXT_PUBLIC_API_URL=https://your-app-name.railway.app
NEXT_PUBLIC_WS_URL=wss://your-app-name.railway.app

# Feature Flags
NEXT_PUBLIC_ENABLE_DEBUG=false
NEXT_PUBLIC_ENABLE_ANALYTICS=true

# Production Settings
NODE_ENV=production
```

### **Backend (Railway Environment)**
```bash
# Database (Railway will provide this automatically)
DATABASE_URL=postgresql://user:password@host:port/database

# Application Settings
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=https://your-app-name.vercel.app,https://your-custom-domain.com

# File Storage (Railway or AWS S3)
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=10485760  # 10MB

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# Noise Words (stored in database settings)
DEFAULT_NOISE_WORDS=details,page,https,filevineapp,docviewer,view,source,embedding
```

---

## 📁 **Step 3: GitHub Repository Setup**

### **Repository Structure**
```
ai-text-analysis-platform/
├── frontend/                  # Next.js application
│   ├── package.json
│   ├── next.config.js
│   └── ...
├── backend/                   # FastAPI application  
│   ├── requirements.txt
│   ├── database.py
│   ├── api_server_db.py
│   └── ...
├── .github/
│   └── workflows/
│       ├── vercel-deploy.yml  # Vercel deployment
│       └── railway-deploy.yml # Railway deployment
├── README.md
├── DEPLOYMENT.md
└── .gitignore
```

### **Commands to Set Up GitHub**
```bash
# 1. Initialize repository (if not already done)
git init
git add .
git commit -m "Initial commit: AI Text Analysis Platform"

# 2. Create GitHub repository and push
git branch -M main
git remote add origin https://github.com/your-username/ai-text-analysis-platform.git
git push -u origin main
```

---

## 🌐 **Step 4: Vercel Frontend Deployment**

### **Vercel Configuration (`vercel.json`)**
```json
{
  "version": 2,
  "name": "ai-text-analysis-platform",
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/next",
      "config": {
        "projectSettings": {
          "framework": "nextjs"
        }
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://your-railway-app.railway.app/api/$1"
    }
  ],
  "env": {
    "NEXT_PUBLIC_API_URL": "https://your-railway-app.railway.app",
    "NEXT_PUBLIC_WS_URL": "wss://your-railway-app.railway.app"
  }
}
```

### **Deployment Steps**

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy from Frontend Directory**
   ```bash
   cd frontend
   vercel
   # Follow prompts to configure project
   ```

4. **Set Environment Variables in Vercel Dashboard**
   - Go to your project settings
   - Add production environment variables
   - Redeploy if needed

---

## 🚂 **Step 5: Railway Backend Deployment**

### **Railway Configuration (`railway.toml`)**
```toml
[build]
builder = "nixpacks"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "python api_server_db.py"
healthcheckPath = "/health"
healthcheckTimeout = 300

[env]
PORT = "8000"
ENVIRONMENT = "production"
```

### **Production Requirements (`requirements.txt`)**
```text
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
python-dotenv==1.0.0
pydantic==2.4.2
pydantic-settings==2.0.3

# Database
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.7

# Text Processing  
nltk==3.8.1
spacy==3.7.2
textblob==0.17.1

# Utilities
httpx==0.25.1
aiofiles==23.2.1
python-jose[cryptography]==3.3.0
```

### **Deployment Steps**

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Create New Project**
   ```bash
   cd backend
   railway create ai-text-analysis-platform
   ```

4. **Add PostgreSQL Database**
   ```bash
   railway add postgresql
   ```

5. **Deploy Backend**
   ```bash
   railway deploy
   ```

---

## 🔧 **Step 6: Production Database Setup**

### **Database Migration Script (`migrate_to_production.py`)**
```python
#!/usr/bin/env python3
"""
Migrate from SQLite development to PostgreSQL production
"""
import os
from sqlalchemy import create_engine
from database import Base
from database_service import DatabaseInitService

def migrate_to_production():
    # Production database URL from Railway
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    print(f"🚀 Migrating to production database...")
    
    # Initialize production database
    success = DatabaseInitService.initialize_database()
    
    if success:
        print("✅ Production database ready!")
        return True
    else:
        print("❌ Production database migration failed!")
        return False

if __name__ == "__main__":
    migrate_to_production()
```

---

## 🌍 **Step 7: Domain Configuration**

### **Custom Domain Setup (Optional)**

1. **Frontend Domain (Vercel)**
   ```bash
   # Add custom domain in Vercel dashboard
   your-app.com → Vercel project
   ```

2. **Backend Domain (Railway)**
   ```bash
   # Configure custom domain in Railway dashboard
   api.your-app.com → Railway service
   ```

### **CORS and Security Updates**
```python
# Update CORS in production backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",
        "https://your-app.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

## 📊 **Step 8: Monitoring & Maintenance**

### **Health Checks**
- **Frontend**: https://your-app.vercel.app
- **Backend**: https://your-app.railway.app/health
- **Database**: Built into Railway dashboard

### **Logging**
- **Vercel**: Function logs in dashboard
- **Railway**: Application logs in dashboard
- **Database**: Query logs in Railway

### **Performance Monitoring**
- **Vercel Analytics**: Built-in performance metrics
- **Railway Metrics**: CPU, memory, database usage
- **Custom Metrics**: API response times in `/health` endpoint

---

## 🆘 **Troubleshooting Guide**

### **Common Issues**

1. **CORS Errors**
   - Check CORS_ORIGINS in Railway
   - Verify domain spelling
   - Ensure HTTPS for production

2. **Database Connection Issues**
   - Verify DATABASE_URL in Railway
   - Check PostgreSQL service status
   - Run database initialization

3. **File Upload Issues**
   - Check file size limits
   - Verify upload directory permissions
   - Consider S3 for large files

4. **API Timeout Issues**
   - Increase Railway timeout settings
   - Optimize database queries
   - Add request caching

---

## 🔄 **Ongoing Development**

### **Deployment Workflow**
1. **Develop locally** with SQLite
2. **Push to GitHub** main branch
3. **Auto-deploy** to Vercel (frontend) and Railway (backend)
4. **Test production** environment
5. **Monitor** logs and performance

### **Feature Development**
- Use feature branches for new features
- Test with production database connection locally
- Deploy via pull requests and merges

---

## 📋 **Deployment Commands Summary**

```bash
# GitHub Setup
git init
git add .
git commit -m "Production deployment ready"
git remote add origin https://github.com/username/ai-text-analysis-platform.git
git push -u origin main

# Vercel Deployment
cd frontend
vercel login
vercel --prod

# Railway Deployment  
cd ../backend
railway login
railway create ai-text-analysis-platform
railway add postgresql
railway deploy

# Environment Variables
# Set in Vercel dashboard and Railway dashboard
```

This deployment setup will give you a production-ready AI text analysis platform! 🚀

**Ready to start? Let me know and I'll begin with the production preparation files.**
