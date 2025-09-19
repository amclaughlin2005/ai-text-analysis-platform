'use client';

import { SignInButton as ClerkSignInButton, useAuth } from '@clerk/nextjs';
import { LogIn } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SignInButtonProps {
  className?: string;
  variant?: 'default' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
}

export default function SignInButton({ 
  className, 
  variant = 'default',
  size = 'md' 
}: SignInButtonProps) {
  const { isSignedIn, isLoaded } = useAuth();

  // Don't show if auth is not enabled or user is already signed in
  const authEnabled = process.env.NEXT_PUBLIC_ENABLE_AUTH === 'true';
  if (!authEnabled || !isLoaded || isSignedIn) {
    return null;
  }

  const baseClasses = "inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2";
  
  const variants = {
    default: "bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500",
    outline: "border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus:ring-primary-500",
    ghost: "text-gray-700 hover:bg-gray-100 focus:ring-primary-500"
  };

  const sizes = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2 text-sm", 
    lg: "px-6 py-3 text-base"
  };

  return (
    <ClerkSignInButton mode="modal">
      <button 
        className={cn(
          baseClasses,
          variants[variant],
          sizes[size],
          className
        )}
      >
        <LogIn className="h-4 w-4" />
        Sign In
      </button>
    </ClerkSignInButton>
  );
}
