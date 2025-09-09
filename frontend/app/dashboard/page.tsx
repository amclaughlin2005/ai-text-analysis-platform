import Link from 'next/link';

export default function DashboardPage() {
  return (
    <div className="bg-gray-50 min-h-full">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome to your AI Text Analysis Dashboard!
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            Your AI-powered text analysis platform
          </p>
        </div>

        {/* Dashboard content - placeholder for now */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Datasets
            </h3>
            <p className="text-3xl font-bold text-primary-600">0</p>
            <p className="text-sm text-gray-500">Total uploaded datasets</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Questions Analyzed
            </h3>
            <p className="text-3xl font-bold text-green-600">0</p>
            <p className="text-sm text-gray-500">Total questions processed</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Active Jobs
            </h3>
            <p className="text-3xl font-bold text-amber-600">0</p>
            <p className="text-sm text-gray-500">Currently processing</p>
          </div>
        </div>

        {/* Quick actions */}
        <div className="mt-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Quick Actions
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <button className="p-4 bg-gray-300 text-gray-500 rounded-lg cursor-not-allowed" disabled>
              Upload Dataset
              <span className="block text-xs mt-1 opacity-75">Coming Soon</span>
            </button>
            <button className="p-4 bg-gray-300 text-gray-500 rounded-lg cursor-not-allowed" disabled>
              View Analytics
              <span className="block text-xs mt-1 opacity-75">Coming Soon</span>
            </button>
            <Link href="/wordcloud-demo" className="p-4 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-center">
              Try Word Cloud Demo
            </Link>
            <button className="p-4 bg-gray-300 text-gray-500 rounded-lg cursor-not-allowed" disabled>
              Export Report
              <span className="block text-xs mt-1 opacity-75">Coming Soon</span>
            </button>
          </div>
        </div>

        {/* Recent activity placeholder */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Recent Activity
          </h2>
          <div className="text-center py-8 text-gray-500">
            <p>No recent activity yet.</p>
            <p className="text-sm mt-2">
              The full platform is coming soon! For now, try our interactive word cloud demo.
            </p>
            <div className="mt-4">
              <Link 
                href="/wordcloud-demo"
                className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                Explore Word Cloud Demo
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
