import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';

// Define public routes (everything else requires authentication)
const isPublicRoute = createRouteMatcher([
  '/login',
  '/sign-up',
  // Static assets and Next.js internals
  '/_next(.*)',
  '/favicon.ico',
  '/images(.*)',
  '/icons(.*)',
  '/api/health'
]);

export default clerkMiddleware(async (auth, req) => {
  const { userId } = await auth();
  const currentPath = req.nextUrl.pathname;

  // If user is not authenticated and trying to access protected route
  if (!userId && !isPublicRoute(req)) {
    // Redirect to login with return URL
    const signInUrl = new URL('/login', req.url);
    signInUrl.searchParams.set('redirect_url', req.url);
    return NextResponse.redirect(signInUrl);
  }

  // If user is authenticated and visiting login page, redirect to dashboard
  if (userId && currentPath === '/login') {
    return NextResponse.redirect(new URL('/dashboard', req.url));
  }

  // Allow the request to continue
  return NextResponse.next();
});

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
};
