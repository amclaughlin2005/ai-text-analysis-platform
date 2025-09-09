import WordCloudDemo from './WordCloudDemo';

export const metadata = {
  title: 'Word Cloud Demo - AI Text Analysis Platform',
  description: 'Interactive demonstration of our advanced word cloud visualization system',
};

export default function WordCloudDemoPage() {
  return (
    <div className="bg-gray-50 min-h-full">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Word Cloud Demo
          </h1>
          <p className="text-lg text-gray-600">
            Interactive word cloud visualization with multiple analysis modes.
          </p>
        </div>

        <WordCloudDemo />
      </div>
    </div>
  );
}
