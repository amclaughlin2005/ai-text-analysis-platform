export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          🎉 AI Text Analysis Platform
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Vercel deployment successful!
        </p>
        <div className="space-y-4">
          <p className="text-green-600 font-semibold">✅ Frontend: Working</p>
          <p className="text-blue-600 font-semibold">🚂 Backend: Railway deployed</p>
          <p className="text-purple-600">🚀 Ready for full app!</p>
        </div>
      </div>
    </div>
  );
}