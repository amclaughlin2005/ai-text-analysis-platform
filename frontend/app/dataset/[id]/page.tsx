import { Suspense } from 'next';
import DatasetViewPage from './DatasetViewPage';

export const metadata = {
  title: 'Dataset View - AI Text Analysis Platform',
  description: 'View uploaded dataset questions and responses',
};

interface PageProps {
  params: {
    id: string;
  };
}

export default function DatasetPage({ params }: PageProps) {
  return (
    <div className="bg-gray-50 min-h-full">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <Suspense fallback={
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading dataset...</p>
            </div>
          </div>
        }>
          <DatasetViewPage datasetId={params.id} />
        </Suspense>
      </div>
    </div>
  );
}
