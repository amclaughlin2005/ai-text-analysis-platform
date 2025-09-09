import { Metadata } from 'next';
import DatasetUploadPage from './DatasetUploadPage';

export const metadata: Metadata = {
  title: 'Upload Dataset - AI Text Analysis Platform',
  description: 'Upload CSV datasets for comprehensive text analysis',
};

export default function UploadPage() {
  return <DatasetUploadPage />;
}
