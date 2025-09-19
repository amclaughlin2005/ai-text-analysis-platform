import { authMiddleware } from '@clerk/nextjs';

export default authMiddleware({
  // Public routes that don't require authentication
  publicRoutes: [
    '/',                    // Landing page
    '/wordcloud',          // Public word cloud viewing
    '/login',              // Sign-in page
    '/api/wordcloud/generate-fast',    // Public word cloud API
    '/api/wordcloud/generate-multi-fast', // Public multi-dataset API
    '/api/wordcloud/filter-options/(.*)', // Public filter options
  ],
  
  // Routes that require authentication
  // Everything not in publicRoutes will require sign-in:
  // - /upload
  // - /datasets  
  // - /dashboard
  // - /dataset/[id]
  // - Other API endpoints

  // Ignore these paths completely (no auth check)
  ignoredRoutes: [
    '/api/health',         // Health checks
    '/_next/(.*)',         // Next.js internals
    '/favicon.ico',        // Static assets
    '/images/(.*)',        // Public images
    '/icons/(.*)',         // Public icons
  ],

  // Custom redirects
  afterAuth(auth, req, evt) {
    // If user is not authenticated and trying to access protected route
    if (!auth.userId && !auth.isPublicRoute) {
      // Redirect to login with return URL
      const signInUrl = new URL('/login', req.url);
      signInUrl.searchParams.set('redirect_url', req.url);
      return Response.redirect(signInUrl);
    }

    // If user is authenticated and visiting login page, redirect to dashboard
    if (auth.userId && req.nextUrl.pathname === '/login') {
      return Response.redirect(new URL('/dashboard', req.url));
    }
  },
});

export const config = {
  matcher: ['/((?!.*\\..*|_next).*)', '/', '/(api|trpc)(.*)'],
};
