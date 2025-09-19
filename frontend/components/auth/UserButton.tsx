'use client';

import { UserButton as ClerkUserButton, useAuth, useUser } from '@clerk/nextjs';
import { User } from 'lucide-react';
import { useEffect, useState } from 'react';

interface UserButtonProps {
  showName?: boolean;
  className?: string;
}

export default function UserButton({ 
  showName = false,
  className 
}: UserButtonProps) {
  const [mounted, setMounted] = useState(false);
  
  // Ensure component only renders on client side
  useEffect(() => {
    setMounted(true);
  }, []);

  // Don't render during SSR or if not mounted
  if (!mounted) {
    return null;
  }

  // Don't show if auth is not enabled
  const authEnabled = process.env.NEXT_PUBLIC_ENABLE_AUTH === 'true';
  if (!authEnabled) {
    return null;
  }

  return <UserButtonContent showName={showName} className={className} />;
}

// Separate component that uses Clerk hooks
function UserButtonContent({ 
  showName, 
  className 
}: { 
  showName?: boolean; 
  className?: string; 
}) {
  const { isSignedIn, isLoaded } = useAuth();
  const { user } = useUser();

  // Don't show if user is not signed in or not loaded
  if (!isLoaded || !isSignedIn) {
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
