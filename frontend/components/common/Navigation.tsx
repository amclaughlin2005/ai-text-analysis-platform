'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Brain, Home, BarChart3, Upload, MessageSquare, Database, Lock } from 'lucide-react';
import { cn } from '@/lib/utils';
import SignInButton from '@/components/auth/SignInButton';
import UserButton from '@/components/auth/UserButton';
import { useAuth } from '@clerk/nextjs';

const navigationItems = [
  {
    name: 'Home',
    href: '/',
    icon: Home,
    protected: true,
  },
  {
    name: 'Word Cloud',
    href: '/wordcloud',
    icon: MessageSquare,
    protected: true,
  },
  {
    name: 'Upload Dataset',
    href: '/upload',
    icon: Upload,
    protected: true,
  },
  {
    name: 'Datasets',
    href: '/datasets',
    icon: Database,
    protected: true,
  },
  {
    name: 'Dashboard',
    href: '/dashboard', 
    icon: BarChart3,
    protected: true,
  }
];

export default function Navigation() {
  const pathname = usePathname();
  const { isSignedIn, isLoaded } = useAuth();
  const authEnforced = process.env.NEXT_PUBLIC_ENFORCE_AUTH === 'true';

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-3">
            <Brain className="h-8 w-8 text-primary-600" />
            <span className="text-xl font-bold text-gray-900">
              AI Text Analysis
            </span>
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-8">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              const isProtected = item.protected && authEnforced;
              const canAccess = !isProtected || isSignedIn;
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                    isActive 
                      ? "bg-primary-100 text-primary-600" 
                      : canAccess
                        ? "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                        : "text-gray-400 cursor-not-allowed"
                  )}
                  onClick={(e) => {
                    if (!canAccess) {
                      e.preventDefault();
                    }
                  }}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.name}</span>
                  {isProtected && !isSignedIn && (
                    <Lock className="h-3 w-3 text-gray-400" />
                  )}
                </Link>
              );
            })}
          </div>

          {/* Authentication */}
          <div className="hidden md:flex items-center space-x-4">
            <SignInButton variant="outline" />
            <UserButton showName />
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center space-x-2">
            <SignInButton size="sm" />
            <UserButton />
            <button className="text-gray-500 hover:text-gray-600">
              <span className="sr-only">Open menu</span>
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
