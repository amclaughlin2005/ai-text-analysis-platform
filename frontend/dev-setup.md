# Development Setup Guide

## Quick Start

1. **Install dependencies** (if not already done):
   ```bash
   npm install
   ```

2. **Create environment file** (optional):
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your configuration
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

4. **Open your browser**:
   - Main app: http://localhost:3000
   - Word cloud demo: http://localhost:3000/wordcloud-demo

## Environment Variables

Create a `.env.local` file with these variables:

```env
# API Configuration (Backend not running yet - using mock data)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Application Configuration
NEXT_PUBLIC_APP_NAME="AI-Powered Text Analysis Platform"

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_EXPORT=true

# Add Clerk keys when ready for authentication:
# NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
# CLERK_SECRET_KEY=sk_test_your_secret_key_here
```

## Available Scripts

```bash
# Development server
npm run dev

# Production build
npm run build

# Start production server
npm start

# Run linting
npm run lint

# Type checking
npm run type-check

# Format code
npm run format
```

## Current Status

✅ **Working Features:**
- Landing page with feature showcase
- Interactive word cloud demo with all modes
- Dashboard (no authentication required)
- Responsive design and animations
- Export functionality (client-side)
- Search and filtering capabilities
- Full navigation between pages

⏳ **Backend Integration:**
- Currently using mock data
- Ready for API integration once backend is running
- WebSocket connections configured but not active
- Authentication temporarily disabled (Clerk removed for now)

## Troubleshooting

### Common Issues:

1. **Port 3000 already in use:**
   ```bash
   # Kill process using port 3000
   npx kill-port 3000
   # Or use different port
   npm run dev -- -p 3001
   ```

2. **TypeScript errors:**
   ```bash
   npm run type-check
   ```

3. **Module resolution issues:**
   ```bash
   rm -rf node_modules .next
   npm install
   ```

### Development Tips:

- The word cloud demo works independently with mock data
- All components are fully typed with TypeScript
- Hot reload works for all code changes
- Use browser dev tools to inspect word cloud interactions

## Testing the Word Cloud

1. Navigate to: http://localhost:3000/wordcloud-demo
2. Try different analysis modes (All, Verbs, Themes, etc.)
3. Test interactive features:
   - Click words to select them
   - Use zoom controls
   - Try search functionality
   - Open controls and export panels
4. Test responsive design on different screen sizes

## Next Steps

Once the backend is running:
1. Update API endpoints in environment variables
2. Remove mock data generators
3. Enable authentication with Clerk
4. Test real-time WebSocket connections
5. Integrate with actual dataset processing
