'use client';

import { UserButton as ClerkUserButton, useAuth, useUser } from '@clerk/nextjs';
import { User } from 'lucide-react';

interface UserButtonProps {
  showName?: boolean;
  className?: string;
}

export default function UserButton({ 
  showName = false,
  className 
}: UserButtonProps) {
  const { isSignedIn, isLoaded } = useAuth();
  const { user } = useUser();

  // Don't show if auth is not enabled or user is not signed in
  const authEnabled = process.env.NEXT_PUBLIC_ENABLE_AUTH === 'true';
  if (!authEnabled || !isLoaded || !isSignedIn) {
    return null;
  }

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      {showName && user && (
        <div className="flex items-center gap-2 text-sm text-gray-700">
          <User className="h-4 w-4" />
          <span>
            {user.firstName || user.emailAddresses[0]?.emailAddress || 'User'}
          </span>
        </div>
      )}
      <ClerkUserButton 
        afterSignOutUrl="/"
        appearance={{
          elements: {
            avatarBox: "h-8 w-8"
          }
        }}
      />
    </div>
  );
}
