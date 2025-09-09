# 🧠 AI-Powered Text Analysis Platform

A comprehensive web application for analyzing query-response datasets using NLTK, interactive word clouds, and advanced text processing capabilities.

![Platform Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![Frontend](https://img.shields.io/badge/Frontend-Next.js%2014-blue)
![Backend](https://img.shields.io/badge/Backend-FastAPI-green)
![Database](https://img.shields.io/badge/Database-PostgreSQL-blue)

## 🌟 **Features**

### ✅ **Core Features (Live)**
- 📊 **Interactive Word Cloud Visualization** with 6 analysis modes
- 📤 **CSV Dataset Upload** with multi-encoding support
- 🎯 **Column Filtering** - Select specific CSV columns for analysis  
- 🚫 **Noise Word Filtering** - Automatically remove unwanted terms
- 🗄️ **Database Persistence** - Datasets survive server restarts
- 📱 **Responsive UI** - Works on desktop and mobile

### 🔄 **Text Analysis Modes**
- **All Words**: Complete vocabulary analysis
- **Action Words**: Verbs and action-oriented language  
- **Themes**: Common themes and topics
- **Emotions**: Emotional language detection
- **Entities**: Named entities and organizations
- **Topics**: Topic modeling results

### 🎛️ **Advanced Filtering**
- **Smart Column Selection**: Analyze questions only, responses only, or combined
- **Preset Filters**: Quick filtering options for different analysis types
- **Custom Noise Words**: Configurable word exclusion lists
- **Real-time Updates**: Word cloud updates instantly with filter changes

---

## 🚀 **Quick Start**

### **Development Setup**
```bash
# 1. Clone the repository
git clone https://github.com/your-username/ai-text-analysis-platform.git
cd ai-text-analysis-platform

# 2. Install dependencies
npm run install:all

# 3. Set up database
npm run setup:db

# 4. Start development servers
npm run dev
```

### **Production Deployment**
```bash
# 1. Prepare for deployment
./deploy.sh

# 2. Deploy frontend to Vercel
cd frontend && vercel --prod

# 3. Deploy backend to Railway  
cd backend && railway deploy

# See DEPLOYMENT.md for detailed instructions
```

---

## 🏗️ **Architecture**

### **Tech Stack**
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, Framer Motion
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, NLTK
- **Deployment**: Vercel (Frontend), Railway (Backend)
- **Database**: SQLite (Dev), PostgreSQL (Production)

### **Project Structure**
```
├── frontend/                 # Next.js React application
│   ├── app/                 # App router pages
│   ├── components/          # React components
│   │   ├── wordcloud/      # Word cloud visualization
│   │   ├── datasets/       # Dataset management
│   │   └── common/         # Shared components
│   └── lib/                # Utilities and types
├── backend/                 # FastAPI Python application  
│   ├── database.py         # Database configuration
│   ├── models.py           # SQLAlchemy models
│   ├── database_service.py # Database operations
│   ├── api_server_db.py    # Main API server
│   └── production_server.py # Production optimized server
└── docs/                   # Documentation
```

---

## 🌐 **Live Application URLs**

### **Development**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8003
- **Legal Data API**: http://localhost:8002
- **API Docs**: http://localhost:8003/docs

### **Production** *(Update after deployment)*
- **Frontend**: https://your-app-name.vercel.app
- **Backend API**: https://your-app-name.railway.app
- **API Docs**: https://your-app-name.railway.app/docs

---

## 📊 **Usage Guide**

### **1. Upload Dataset**
1. Go to **Upload Dataset** page
2. Drop or select a CSV file with question/response columns
3. Preview data and confirm upload
4. Dataset is stored permanently in database

### **2. Analyze with Word Cloud**  
1. Go to **Word Cloud Demo** page
2. Select analysis mode (All, Verbs, Themes, etc.)
3. Use **Column Filter** button to select specific CSV columns
4. Explore interactive word cloud visualization

### **3. View Dataset Details**
1. Go to **My Datasets** from upload page
2. Click **View Dataset** to see questions and answers
3. Use **Word Cloud** button for visualization
4. Apply column filters for targeted analysis

---

## 🔧 **Configuration**

### **Environment Variables**

Copy `env.template` to `.env` and configure:

```bash
# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8003
NEXT_PUBLIC_WS_URL=ws://localhost:8003

# Backend  
DATABASE_URL=sqlite:///./wordcloud_analysis.db
PORT=8003
CORS_ORIGINS=http://localhost:3000
```

### **Customization**

**Noise Words**: Update in database settings or `DEFAULT_NOISE_WORDS` env var
```bash
DEFAULT_NOISE_WORDS=details,page,https,filevineapp,docviewer,view,source,embedding
```

**Word Cloud Limits**: Adjust maximum words displayed
```bash
MAX_WORDS_PER_CLOUD=50
```

---

## 📚 **Documentation**

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide
- **[AI_Instructions.md](AI_Instructions.md)** - Development and architecture details  
- **[AI_System_Prompt.md](AI_System_Prompt.md)** - High-level system overview
- **[Frontend README](frontend/README.md)** - Frontend-specific documentation
- **[Backend README](backend/README.md)** - Backend-specific documentation

---

## 🛠️ **Development**

### **Available Scripts**
```bash
npm run dev              # Start development servers
npm run build            # Build for production  
npm run clean            # Clean build artifacts
npm run setup:db         # Initialize database
npm run deploy:vercel    # Deploy to Vercel
npm run deploy:railway   # Deploy to Railway
```

### **Adding Features**
1. Create feature branch: `git checkout -b feature/new-feature`
2. Develop and test locally
3. Update documentation if needed
4. Create pull request to main branch
5. Auto-deploy to production on merge

---

## 🐛 **Troubleshooting**

### **Common Issues**
- **CORS errors**: Update `CORS_ORIGINS` in backend environment
- **Database connection**: Check `DATABASE_URL` and PostgreSQL status
- **File upload fails**: Verify file size limits and upload directory
- **Word cloud not loading**: Check API endpoint connectivity

### **Getting Help**
- Check the [Deployment Guide](DEPLOYMENT.md) for setup issues
- Review [AI Instructions](AI_Instructions.md) for technical details
- Check application health: `/health` endpoint

---

## 📄 **License**

MIT License - See LICENSE file for details

---

## 🎯 **Roadmap**

### **Completed** ✅
- Interactive word cloud with 6 analysis modes
- CSV upload and database persistence  
- Column filtering and noise word removal
- Production deployment configuration

### **Next Features** 🚧
- Advanced NLTK sentiment analysis
- Real-time background processing
- Comprehensive analytics dashboard
- User authentication and multi-tenancy
- Export functionality (PNG, PDF, CSV)

---

**Built with ❤️ for AI-powered text analysis**
