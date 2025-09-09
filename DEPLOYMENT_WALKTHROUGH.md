# 🚀 AI Text Analysis Platform - Step-by-Step Deployment Walkthrough

**This guide will walk you through deploying your app from start to finish. Follow each step carefully.**

---

## 📋 **Step 1: Prepare Your Accounts** 

### **Create Required Accounts** (if you don't have them)
1. **GitHub**: https://github.com/signup
2. **Vercel**: https://vercel.com/signup
3. **Railway**: https://railway.app/signup

✅ **Log in to all three platforms before continuing**

---

## 🗂️ **Step 2: Create GitHub Repository**

### **A. Create New Repository**
1. Go to https://github.com/new
2. **Repository name**: `ai-text-analysis-platform`
3. **Description**: `AI-powered text analysis platform with word cloud visualization`
4. **Public** or **Private** (your choice)
5. **Initialize**: Don't initialize (we'll push existing code)
6. Click **Create repository**

### **B. Copy the Repository URL**
After creation, copy the repository URL:
```
https://github.com/YOUR-USERNAME/ai-text-analysis-platform.git
```

---

## 📤 **Step 3: Push Code to GitHub**

### **A. Open Terminal in Your Project Directory**
```bash
cd /Users/alexmclaughlin/Desktop/Cursor\ Projects/WordCloud
```

### **B. Initialize Git (if not already done)**
```bash
git init
git add .
git commit -m "Initial commit: AI Text Analysis Platform ready for deployment"
```

### **C. Connect to GitHub and Push**
```bash
# Replace YOUR-USERNAME with your actual GitHub username
git remote add origin https://github.com/YOUR-USERNAME/ai-text-analysis-platform.git
git branch -M main
git push -u origin main
```

✅ **Your code is now on GitHub!**

---

## 🌐 **Step 4: Deploy Frontend to Vercel**

### **A. Install Vercel CLI**
```bash
npm install -g vercel
```

### **B. Login to Vercel**
```bash
vercel login
```
Follow the prompts to authenticate with your Vercel account.

### **C. Deploy Frontend**
```bash
cd frontend
vercel
```

**During setup, answer:**
- **Set up and deploy?** → `Y`
- **Which scope?** → Select your personal account
- **Link to existing project?** → `N`  
- **What's your project's name?** → `ai-text-analysis-platform`
- **In which directory is your code located?** → `./` (current directory)
- **Want to override the settings?** → `N`

### **D. Deploy to Production**
```bash
vercel --prod
```

✅ **Copy the production URL** (e.g., `https://ai-text-analysis-platform.vercel.app`)

---

## 🚂 **Step 5: Deploy Backend to Railway**

### **A. Install Railway CLI**
```bash
npm install -g @railway/cli
```

### **B. Login to Railway**
```bash
railway login
```
This will open a browser window to authenticate.

### **C. Create Railway Project**
```bash
cd ../backend
railway create
```
**Project name**: `ai-text-analysis-platform`

### **D. Add PostgreSQL Database**
```bash
railway add postgresql
```

### **E. Deploy Backend**
```bash
railway deploy
```

### **F. Get Railway URL**
```bash
railway status
```
✅ **Copy the Railway URL** (e.g., `https://ai-text-analysis-platform.railway.app`)

---

## 🔧 **Step 6: Configure Environment Variables**

### **A. Update Vercel Environment Variables**
1. Go to https://vercel.com/dashboard
2. Select your `ai-text-analysis-platform` project
3. Go to **Settings** → **Environment Variables**
4. Add these variables:

```
NEXT_PUBLIC_API_URL = https://your-railway-app.railway.app
NEXT_PUBLIC_WS_URL = wss://your-railway-app.railway.app  
NODE_ENV = production
```

### **B. Update Railway Environment Variables**
1. Go to https://railway.app/dashboard
2. Select your `ai-text-analysis-platform` project
3. Go to **Variables** tab
4. Add these variables:

```
ENVIRONMENT = production
DEBUG = false
CORS_ORIGINS = https://your-vercel-app.vercel.app
MAX_FILE_SIZE = 10485760
UPLOAD_DIR = /app/uploads
DEFAULT_NOISE_WORDS = details,page,https,filevineapp,docviewer,view,source,embedding
```

---

## 🔄 **Step 7: Redeploy with Updated URLs**

### **A. Update Configuration Files**

**Update `vercel.json`** in your project root:
```json
{
  "env": {
    "NEXT_PUBLIC_API_URL": "https://YOUR-ACTUAL-RAILWAY-URL.railway.app"
  }
}
```

**Update `backend/railway.toml`**:
```toml
[env]
CORS_ORIGINS = { default = "https://YOUR-ACTUAL-VERCEL-URL.vercel.app" }
```

### **B. Push Updates**
```bash
git add .
git commit -m "Configure production URLs"
git push
```

### **C. Redeploy**
```bash
# Redeploy frontend
cd frontend && vercel --prod

# Redeploy backend  
cd ../backend && railway deploy
```

---

## ✅ **Step 8: Test Production Deployment**

### **A. Test Frontend**
1. Visit your Vercel URL
2. Check navigation works
3. Try uploading a CSV file
4. Verify word cloud displays

### **B. Test Backend**  
1. Visit `https://your-railway-app.railway.app/health`
2. Should return healthy status
3. Check `https://your-railway-app.railway.app/docs` for API documentation

### **C. Test Database**
1. Upload a dataset
2. Refresh page - dataset should persist
3. Check Railway database dashboard for data

---

## 🎯 **Step 9: Update Documentation**

### **A. Update README URLs**
Update the "Production" URLs section in README.md with your actual deployed URLs.

### **B. Update AI Instructions**
Update AI_Instructions.md with production deployment status.

### **C. Share Your Success!** 🎉
Your AI Text Analysis Platform is now live in production!

---

## 📊 **Monitoring Your Deployment**

### **Vercel Dashboard**
- **Analytics**: View page visits and performance
- **Functions**: Monitor API calls and errors
- **Deployments**: Track deployment history

### **Railway Dashboard**  
- **Metrics**: CPU, memory, and database usage
- **Logs**: View application logs
- **Database**: PostgreSQL query monitoring

---

## 🆘 **If Something Goes Wrong**

### **Frontend Issues**
- Check Vercel function logs
- Verify API URLs in environment variables
- Test API endpoints directly

### **Backend Issues**
- Check Railway application logs
- Verify database connection
- Test health endpoint: `/health`

### **Database Issues**
- Check Railway PostgreSQL service status
- Verify DATABASE_URL environment variable
- Run database initialization if needed

---

## 🎊 **Congratulations!**

Your AI Text Analysis Platform is now deployed to production! 

**Features Available:**
- ✅ Persistent dataset uploads
- ✅ Interactive word cloud analysis
- ✅ Column filtering and noise removal
- ✅ Real-time data processing
- ✅ Professional UI/UX

**Next Steps:**
- Add your own datasets
- Customize noise word filters
- Share with colleagues
- Build additional analytics features

---

*Need help? Check [DEPLOYMENT.md](DEPLOYMENT.md) for troubleshooting tips.*
