'use client';

import { SignIn, useAuth } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Brain, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function LoginPage() {
  const [mounted, setMounted] = useState(false);
  
  // Ensure component only renders on client side
  useEffect(() => {
    setMounted(true);
  }, []);

  // Check if auth is enabled
  const authEnabled = process.env.NEXT_PUBLIC_ENABLE_AUTH === 'true';

  // Don't render during SSR
  if (!mounted) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-4 shadow-lg rounded-lg sm:px-10">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-4 text-sm text-gray-600">Loading...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!authEnabled) {
    return <AuthDisabledPage />;
  }

  return <LoginPageContent />;
}

// Component for when auth is disabled
function AuthDisabledPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow-lg rounded-lg sm:px-10">
          <div className="text-center">
            <Brain className="mx-auto h-12 w-12 text-primary-600" />
            <h2 className="mt-6 text-3xl font-bold text-gray-900">
              Authentication Disabled
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              Authentication is currently disabled in development mode.
            </p>
            <div className="mt-6">
              <Link 
                href="/"
                className="flex items-center justify-center gap-2 w-full bg-primary-600 text-white py-2 px-4 rounded-lg hover:bg-primary-700 transition-colors"
              >
                <ArrowLeft className="h-4 w-4" />
                Back to App
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Component that uses Clerk hooks
function LoginPageContent() {
  const { isSignedIn, isLoaded } = useAuth();
  const router = useRouter();

  // Redirect if already signed in
  useEffect(() => {
    if (isLoaded && isSignedIn) {
      router.push('/');
    }
  }, [isSignedIn, isLoaded, router]);

  // Show loading state
  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-4 shadow-lg rounded-lg sm:px-10">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-4 text-sm text-gray-600">Loading...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show sign-in form
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <Brain className="mx-auto h-12 w-12 text-primary-600" />
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            Sign in to your account
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Access your personalized AI text analysis dashboard
          </p>
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow-lg rounded-lg sm:px-10">
          <SignIn 
            routing="hash"
            signUpUrl="/login"
            redirectUrl="/"
            appearance={{
              elements: {
                rootBox: "w-full",
                card: "shadow-none border-0 w-full",
                headerTitle: "hidden",
                headerSubtitle: "hidden",
                socialButtonsBlockButton: "w-full",
                formButtonPrimary: "w-full bg-primary-600 hover:bg-primary-700",
                footerAction: "hidden"
              }
            }}
          />
          
          {/* Back to app link */}
          <div className="mt-6 text-center">
            <Link 
              href="/"
              className="inline-flex items-center gap-2 text-sm text-primary-600 hover:text-primary-700"
            >
              <ArrowLeft className="h-4 w-4" />
              Continue without signing in
            </Link>
          </div>
        </div>
      </div>

      {/* Phase 1 Notice */}
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="text-center">
            <p className="text-xs text-blue-800">
              <strong>Phase 1:</strong> Authentication is optional. All features work without signing in.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
