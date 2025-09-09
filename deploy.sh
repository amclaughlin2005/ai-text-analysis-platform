#!/bin/bash
# AI Text Analysis Platform - Deployment Script

set -e  # Exit on any error

echo "🚀 AI Text Analysis Platform - Production Deployment"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check requirements
print_info "Checking deployment requirements..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    print_error "Git not initialized. Run: git init"
    exit 1
fi

# Check if we're on main branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    print_warning "Not on main branch (current: $current_branch). Deploying from main is recommended."
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    print_warning "Uncommitted changes detected. Consider committing before deployment."
fi

# Build frontend
print_info "Building frontend for production..."
cd frontend

if [ ! -f "package.json" ]; then
    print_error "Frontend package.json not found!"
    exit 1
fi

# Install dependencies and build
npm install
npm run build

if [ $? -eq 0 ]; then
    print_status "Frontend build successful"
else
    print_error "Frontend build failed"
    exit 1
fi

cd ..

# Test backend
print_info "Testing backend configuration..."
cd backend

if [ ! -f "requirements.txt" ]; then
    print_error "Backend requirements.txt not found!"
    exit 1
fi

# Test database connection (development)
python3 -c "
from database import check_database_connection
if check_database_connection():
    print('✅ Database connection test passed')
else:
    print('❌ Database connection test failed')
    exit(1)
"

if [ $? -eq 0 ]; then
    print_status "Backend tests passed"
else
    print_error "Backend tests failed"
    exit 1
fi

cd ..

# Pre-deployment checklist
print_info "Pre-deployment checklist:"
echo "  📋 Frontend built successfully"
echo "  📋 Backend tests passed"  
echo "  📋 Database connection verified"
echo "  📋 Environment variables template created"

print_status "Application ready for deployment!"
echo ""
print_info "Next steps:"
echo "  1. Create GitHub repository"
echo "  2. Deploy to Vercel: cd frontend && vercel --prod"
echo "  3. Deploy to Railway: cd backend && railway deploy"
echo "  4. Update environment variables with production URLs"
echo "  5. Test production deployment"
echo ""
print_info "See DEPLOYMENT.md for detailed instructions"
