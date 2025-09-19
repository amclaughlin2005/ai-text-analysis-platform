import { authMiddleware } from '@clerk/nextjs';

export default authMiddleware({
  // Public routes that don't require authentication
  publicRoutes: [
    '/login',              // Sign-in page only
    // Everything else requires authentication:
    // - / (landing page)
    // - /wordcloud  
    // - /upload
    // - /datasets  
    // - /dashboard
    // - /dataset/[id]
    // - All API endpoints (except ignored ones)
  ],

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
