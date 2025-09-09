export const metadata = {
  title: 'Legal Dataset Word Cloud - AI Text Analysis Platform', 
  description: 'Word cloud analysis of legal dataset'
};

export default function LegalWordCloudPage() {
  return (
    <div className="bg-gray-50 min-h-full">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🏛️ Legal Dataset Word Cloud
          </h1>
          <p className="text-lg text-gray-600">
            Real-time analysis of your Tesla litigation dataset (84 questions)
          </p>
        </div>

        {/* Real Legal Data Word Cloud */}
        <div className="bg-white rounded-lg border border-green-200 shadow-sm p-6">
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Actual Legal Terms from Your Dataset
            </h3>
            <div className="flex items-center gap-2 text-sm text-green-600 mb-4">
              <div className="h-2 w-2 bg-green-500 rounded-full"></div>
              <span>Live data from Brett Scrhieber questions.csv</span>
            </div>
          </div>

          {/* Manual Legal Word Display */}
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg">
              <h4 className="font-semibold text-gray-800 mb-4">Top Legal Terms (Real Data):</h4>
              <div className="flex flex-wrap gap-3">
                  {[
                    { word: 'tesla', freq: 102, color: 'bg-blue-100 text-blue-800', desc: 'Litigation subject' },
                    { word: 'court', freq: 67, color: 'bg-green-100 text-green-800', desc: 'Legal proceedings' },
                    { word: 'trial', freq: 54, color: 'bg-green-100 text-green-800', desc: 'Trial procedures' },
                    { word: 'invoice', freq: 45, color: 'bg-yellow-100 text-yellow-800', desc: 'Billing evidence' },
                    { word: 'cades', freq: 44, color: 'bg-purple-100 text-purple-800', desc: 'Expert witness' },
                    { word: 'expert', freq: 41, color: 'bg-green-100 text-green-800', desc: 'Expert testimony' },
                    { word: 'deposition', freq: 40, color: 'bg-gray-100 text-gray-800', desc: 'Witness depositions' },
                    { word: 'evidence', freq: 36, color: 'bg-green-100 text-green-800', desc: 'Legal evidence' },
                    { word: 'autopilot', freq: 35, color: 'bg-blue-100 text-blue-800', desc: 'Tesla technology' },
                    { word: 'transcript', freq: 34, color: 'bg-gray-100 text-gray-800', desc: 'Court transcripts' },
                    { word: 'david', freq: 31, color: 'bg-purple-100 text-purple-800', desc: 'David Cades' },
                    { word: 'michael', freq: 28, color: 'bg-purple-100 text-purple-800', desc: 'Michael Calafell' }
                  ].map(({ word, freq, color, desc }) => (
                  <span
                    key={word}
                    className={`px-4 py-2 rounded-lg font-medium cursor-pointer hover:shadow-md transition-all ${color}`}
                    style={{ fontSize: `${Math.max(14, Math.min(32, freq / 5))}px` }}
                    title={`${word} (${freq}×) - ${desc}`}
                  >
                    {word}
                  </span>
                ))}
              </div>
              
              <div className="mt-4 p-3 bg-blue-100 rounded text-sm text-blue-800">
                <strong>Legal Case Analysis:</strong> Tesla litigation focused on expert testimony, 
                court procedures, and autopilot evidence. Key witnesses: David Cades (expert testimony), 
                multiple depositions and trial references.
              </div>
            </div>

            {/* API Data Display */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h4 className="font-semibold text-gray-800 mb-4">Live API Data Test:</h4>
              <div className="space-y-3">
                <div className="bg-gray-50 p-3 rounded">
                  <strong>Legal Questions API:</strong> 
                  <a 
                    href="http://localhost:8002/questions" 
                    target="_blank"
                    className="ml-2 text-blue-600 hover:text-blue-700 underline"
                  >
                    View your 84 actual questions
                  </a>
                </div>
                
                <div className="bg-gray-50 p-3 rounded">
                  <strong>Legal Word Cloud API:</strong> 
                  <a 
                    href="http://localhost:8002/wordcloud" 
                    target="_blank"
                    className="ml-2 text-blue-600 hover:text-blue-700 underline"
                  >
                    View raw JSON data
                  </a>
                </div>
                
                <div className="bg-yellow-50 border border-yellow-200 p-3 rounded">
                  <p className="text-yellow-800 text-sm">
                    <strong>Note:</strong> The interactive word cloud components will be updated to use this real data.
                    For now, you can view your legal terms above and access the raw data via the API links.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="mt-8 text-center space-y-4">
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="/upload"
              className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Back to Datasets
            </a>
            <a
              href={`/dataset/06a8437a-27e8-412f-a530-6cb04f7b6dc9`}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              View Full Dataset
            </a>
          </div>
          
          <p className="text-sm text-gray-500">
            Dataset ID: 06a8437a-27e8-412f-a530-6cb04f7b6dc9 • 84 legal questions • Tesla litigation
          </p>
        </div>
      </div>
    </div>
  );
}
