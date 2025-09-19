import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Navigation from '@/components/common/Navigation';
import { ClerkProvider } from '@clerk/nextjs';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'AI Text Analysis Platform',
  description: 'AI-powered text analysis with word clouds',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Check if authentication is enabled
  const authEnabled = process.env.NEXT_PUBLIC_ENABLE_AUTH === 'true';
  
  if (authEnabled) {
    return (
      <ClerkProvider>
        <html lang="en">
          <body className={inter.className}>
            <Navigation />
            <main className="min-h-screen">
              {children}
            </main>
          </body>
        </html>
      </ClerkProvider>
    );
  }

  // Fallback without Clerk provider if auth is disabled
  return (
    <html lang="en">
      <body className={inter.className}>
        <Navigation />
        <main className="min-h-screen">
          {children}
        </main>
      </body>
    </html>
  );
}