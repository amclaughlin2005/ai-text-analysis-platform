'use client';

import React from 'react';
import FlexibleDataUpload from '../../components/datasets/FlexibleDataUpload';

export default function FlexibleUploadPage() {
  const handleUploadComplete = (datasetId: string, schema: any) => {
    console.log('Upload completed:', { datasetId, schema });
    // Here you could redirect to the dataset view or word cloud generation
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto py-8">
        <FlexibleDataUpload onUploadComplete={handleUploadComplete} />
      </div>
    </div>
  );
}
