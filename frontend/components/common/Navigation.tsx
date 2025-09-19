'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Brain, Home, BarChart3, Upload, MessageSquare, Database } from 'lucide-react';
import { cn } from '@/lib/utils';
import SignInButton from '@/components/auth/SignInButton';
import UserButton from '@/components/auth/UserButton';

const navigationItems = [
  {
    name: 'Home',
    href: '/',
    icon: Home,
  },
  {
    name: 'Upload Dataset',
    href: '/upload',
    icon: Upload,
  },
  {
    name: 'Datasets',
    href: '/datasets',
    icon: Database,
  },
  {
    name: 'Dashboard',
    href: '/dashboard', 
    icon: BarChart3,
  },
  {
    name: 'Word Cloud',
    href: '/wordcloud',
    icon: MessageSquare,
  }
];

export default function Navigation() {
  const pathname = usePathname();

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
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                    isActive 
                      ? "bg-primary-100 text-primary-600" 
                      : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.name}</span>
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
