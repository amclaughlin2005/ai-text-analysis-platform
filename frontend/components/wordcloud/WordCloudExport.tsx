'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Download, 
  FileImage, 
  FileText, 
  Table, 
  Share, 
  Copy,
  Check,
  Loader2,
  Settings
} from 'lucide-react';
import { WordCloudData, WordCloudFilters, ExportFormat } from '@/lib/types';
import { cn, downloadCSV } from '@/lib/utils';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

interface WordCloudExportProps {
  datasetId: string;
  mode: string;
  filters: WordCloudFilters;
  words: WordCloudData[];
  onExportComplete?: () => void;
}

const EXPORT_FORMATS = [
  {
    id: 'png',
    label: 'PNG Image',
    icon: FileImage,
    description: 'High-resolution image file',
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200'
  },
  {
    id: 'svg',
    label: 'SVG Vector',
    icon: FileImage,
    description: 'Scalable vector graphics',
    color: 'text-purple-600',
    bgColor: 'bg-purple-50',
    borderColor: 'border-purple-200'
  },
  {
    id: 'pdf',
    label: 'PDF Document',
    icon: FileText,
    description: 'Portable document format',
    color: 'text-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200'
  },
  {
    id: 'csv',
    label: 'CSV Data',
    icon: Table,
    description: 'Comma-separated values',
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200'
  },
  {
    id: 'json',
    label: 'JSON Data',
    icon: FileText,
    description: 'Structured data format',
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-50',
    borderColor: 'border-indigo-200'
  }
];

interface ExportSettings {
  includeMetadata: boolean;
  includeFilters: boolean;
  imageQuality: number;
  imageWidth: number;
  imageHeight: number;
  backgroundColor: string;
  fontSize: number;
}

const DEFAULT_EXPORT_SETTINGS: ExportSettings = {
  includeMetadata: true,
  includeFilters: true,
  imageQuality: 2,
  imageWidth: 1200,
  imageHeight: 800,
  backgroundColor: '#ffffff',
  fontSize: 16
};

export default function WordCloudExport({
  datasetId,
  mode,
  filters,
  words,
  onExportComplete
}: WordCloudExportProps) {
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>('PNG');
  const [isExporting, setIsExporting] = useState(false);
  const [exportStatus, setExportStatus] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState<ExportSettings>(DEFAULT_EXPORT_SETTINGS);
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const handleExport = async (format: ExportFormat) => {
    setIsExporting(true);
    setExportStatus(`Preparing ${format} export...`);

    try {
      switch (format.toLowerCase()) {
        case 'png':
          await exportPNG();
          break;
        case 'svg':
          await exportSVG();
          break;
        case 'pdf':
          await exportPDF();
          break;
        case 'csv':
          await exportCSV();
          break;
        case 'json':
          await exportJSON();
          break;
        default:
          throw new Error(`Export format ${format} not supported`);
      }
      
      setExportStatus('Export completed successfully!');
      setTimeout(() => {
        setExportStatus(null);
        if (onExportComplete) onExportComplete();
      }, 2000);
      
    } catch (error) {
      setExportStatus(`Export failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setTimeout(() => setExportStatus(null), 3000);
    } finally {
      setIsExporting(false);
    }
  };

  const exportPNG = async () => {
    setExportStatus('Capturing word cloud image...');
    
    // Find the word cloud SVG element
    const svgElement = document.querySelector('[data-testid="wordcloud-svg"]') as SVGElement;
    if (!svgElement) {
      throw new Error('Word cloud visualization not found');
    }

    // Create a canvas and render the SVG
    const canvas = await html2canvas(svgElement.parentElement!, {
      width: settings.imageWidth,
      height: settings.imageHeight,
      scale: settings.imageQuality,
      backgroundColor: settings.backgroundColor,
      useCORS: true,
      allowTaint: true,
    });

    // Download the image
    const link = document.createElement('a');
    link.download = `wordcloud-${mode}-${Date.now()}.png`;
    link.href = canvas.toDataURL('image/png');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const exportSVG = async () => {
    setExportStatus('Generating SVG file...');
    
    // Get the SVG element
    const svgElement = document.querySelector('[data-testid="wordcloud-svg"]') as SVGElement;
    if (!svgElement) {
      throw new Error('Word cloud visualization not found');
    }

    // Clone and prepare SVG for export
    const svgClone = svgElement.cloneNode(true) as SVGElement;
    svgClone.setAttribute('width', settings.imageWidth.toString());
    svgClone.setAttribute('height', settings.imageHeight.toString());
    svgClone.style.backgroundColor = settings.backgroundColor;

    // Create blob and download
    const svgString = new XMLSerializer().serializeToString(svgClone);
    const blob = new Blob([svgString], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.download = `wordcloud-${mode}-${Date.now()}.svg`;
    link.href = url;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
  };

  const exportPDF = async () => {
    setExportStatus('Creating PDF document...');
    
    // Create PDF
    const pdf = new jsPDF({
      orientation: settings.imageWidth > settings.imageHeight ? 'landscape' : 'portrait',
      unit: 'px',
      format: [settings.imageWidth, settings.imageHeight]
    });

    // Add title and metadata if enabled
    if (settings.includeMetadata) {
      pdf.setFontSize(20);
      pdf.text(`Word Cloud Analysis - ${mode.toUpperCase()}`, 40, 40);
      
      pdf.setFontSize(12);
      pdf.text(`Generated: ${new Date().toLocaleDateString()}`, 40, 70);
      pdf.text(`Total Words: ${words.length}`, 40, 90);
      pdf.text(`Dataset ID: ${datasetId}`, 40, 110);
      
      if (settings.includeFilters && Object.keys(filters).length > 0) {
        pdf.text('Applied Filters:', 40, 140);
        let yPos = 160;
        Object.entries(filters).forEach(([key, value]) => {
          if (value) {
            pdf.text(`- ${key}: ${JSON.stringify(value)}`, 50, yPos);
            yPos += 20;
          }
        });
      }
    }

    // Capture word cloud as image and add to PDF
    const svgElement = document.querySelector('[data-testid="wordcloud-svg"]') as SVGElement;
    if (svgElement) {
      const canvas = await html2canvas(svgElement.parentElement!, {
        width: settings.imageWidth * 0.8,
        height: settings.imageHeight * 0.6,
        scale: 1,
        backgroundColor: settings.backgroundColor,
      });
      
      const imgData = canvas.toDataURL('image/png');
      const yPos = settings.includeMetadata ? 200 : 40;
      pdf.addImage(imgData, 'PNG', 40, yPos, settings.imageWidth * 0.8, settings.imageHeight * 0.6);
    }

    // Save PDF
    pdf.save(`wordcloud-${mode}-${Date.now()}.pdf`);
  };

  const exportCSV = async () => {
    setExportStatus('Preparing CSV data...');
    
    const csvData = words.map(word => ({
      word: word.word,
      frequency: word.frequency,
      sentiment: word.sentiment || '',
      category: word.category || '',
      size: word.size,
      color: word.color
    }));

    // Add metadata if enabled
    if (settings.includeMetadata) {
      csvData.unshift({
        word: '# Metadata',
        frequency: 0,
        sentiment: '',
        category: `Mode: ${mode}, Generated: ${new Date().toISOString()}, Dataset: ${datasetId}`,
        size: 0,
        color: ''
      } as any);
    }

    downloadCSV(csvData, `wordcloud-${mode}-${Date.now()}.csv`);
  };

  const exportJSON = async () => {
    setExportStatus('Creating JSON file...');
    
    const jsonData = {
      metadata: settings.includeMetadata ? {
        mode,
        datasetId,
        generatedAt: new Date().toISOString(),
        totalWords: words.length,
        filters: settings.includeFilters ? filters : undefined
      } : undefined,
      words,
      settings: {
        imageWidth: settings.imageWidth,
        imageHeight: settings.imageHeight,
        backgroundColor: settings.backgroundColor
      }
    };

    const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.download = `wordcloud-${mode}-${Date.now()}.json`;
    link.href = url;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
  };

  const generateShareUrl = async () => {
    // This would integrate with your backend to create shareable links
    const shareData = {
      datasetId,
      mode,
      filters,
      timestamp: Date.now()
    };
    
    // For now, create a mock share URL
    const encodedData = btoa(JSON.stringify(shareData));
    const shareUrl = `${window.location.origin}/shared/wordcloud/${encodedData}`;
    setShareUrl(shareUrl);
    return shareUrl;
  };

  const copyShareUrl = async () => {
    if (!shareUrl) {
      const url = await generateShareUrl();
      await navigator.clipboard.writeText(url);
    } else {
      await navigator.clipboard.writeText(shareUrl);
    }
    
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="p-4 space-y-6">
      {/* Export Status */}
      {(isExporting || exportStatus) && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className={cn(
            "flex items-center gap-3 p-3 rounded-lg border",
            isExporting 
              ? "bg-blue-50 border-blue-200 text-blue-800"
              : exportStatus?.includes('failed')
              ? "bg-red-50 border-red-200 text-red-800"
              : "bg-green-50 border-green-200 text-green-800"
          )}
        >
          {isExporting ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : exportStatus?.includes('failed') ? (
            <span className="text-red-600">❌</span>
          ) : (
            <Check className="h-4 w-4" />
          )}
          <span className="text-sm font-medium">{exportStatus}</span>
        </motion.div>
      )}

      {/* Export Format Selection */}
      <div className="space-y-4">
        <h4 className="text-lg font-semibold text-gray-900">Export Format</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {EXPORT_FORMATS.map((format) => {
            const Icon = format.icon;
            const isSelected = selectedFormat === format.id.toUpperCase();
            
            return (
              <button
                key={format.id}
                onClick={() => setSelectedFormat(format.id.toUpperCase() as ExportFormat)}
                disabled={isExporting}
                className={cn(
                  "p-4 text-left rounded-lg border-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed",
                  isSelected 
                    ? `${format.borderColor} ${format.bgColor}` 
                    : "border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm"
                )}
              >
                <div className="flex items-center gap-3 mb-2">
                  <Icon className={cn(
                    "h-5 w-5",
                    isSelected ? format.color : "text-gray-500"
                  )} />
                  <span className="font-medium">{format.label}</span>
                  {isSelected && (
                    <div className="ml-auto">
                      <div className={`h-2 w-2 ${format.color.replace('text-', 'bg-')} rounded-full`}></div>
                    </div>
                  )}
                </div>
                <p className={cn(
                  "text-sm",
                  isSelected ? format.color.replace('600', '700') : "text-gray-600"
                )}>
                  {format.description}
                </p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Export Settings */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="text-lg font-semibold text-gray-900">Export Settings</h4>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Settings className="h-4 w-4" />
            {showSettings ? 'Hide' : 'Show'} Settings
          </button>
        </div>

        {showSettings && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-4 p-4 bg-gray-50 rounded-lg"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Image Width (px)
                </label>
                <input
                  type="number"
                  value={settings.imageWidth}
                  onChange={(e) => setSettings({...settings, imageWidth: parseInt(e.target.value)})}
                  min="400"
                  max="4000"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Image Height (px)
                </label>
                <input
                  type="number"
                  value={settings.imageHeight}
                  onChange={(e) => setSettings({...settings, imageHeight: parseInt(e.target.value)})}
                  min="300"
                  max="3000"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Image Quality
                </label>
                <select
                  value={settings.imageQuality}
                  onChange={(e) => setSettings({...settings, imageQuality: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value={1}>Standard (1x)</option>
                  <option value={2}>High (2x)</option>
                  <option value={3}>Ultra (3x)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Background Color
                </label>
                <input
                  type="color"
                  value={settings.backgroundColor}
                  onChange={(e) => setSettings({...settings, backgroundColor: e.target.value})}
                  className="w-full h-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="space-y-3">
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={settings.includeMetadata}
                  onChange={(e) => setSettings({...settings, includeMetadata: e.target.checked})}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm text-gray-700">Include metadata</span>
              </label>

              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={settings.includeFilters}
                  onChange={(e) => setSettings({...settings, includeFilters: e.target.checked})}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm text-gray-700">Include applied filters</span>
              </label>
            </div>
          </motion.div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3 pt-4 border-t border-gray-200">
        <button
          onClick={() => handleExport(selectedFormat)}
          disabled={isExporting}
          className="flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isExporting ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Download className="h-4 w-4" />
          )}
          Export as {selectedFormat}
        </button>

        <button
          onClick={copyShareUrl}
          disabled={isExporting}
          className="flex items-center gap-2 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {copied ? (
            <Check className="h-4 w-4 text-green-600" />
          ) : (
            <Share className="h-4 w-4" />
          )}
          {copied ? 'Copied!' : 'Share Link'}
        </button>
      </div>

      {/* Share URL Display */}
      {shareUrl && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="p-3 bg-gray-50 border border-gray-200 rounded-lg"
        >
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Share URL
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={shareUrl}
              readOnly
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-white text-sm"
            />
            <button
              onClick={() => navigator.clipboard.writeText(shareUrl)}
              className="p-2 text-gray-500 hover:text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Copy className="h-4 w-4" />
            </button>
          </div>
        </motion.div>
      )}
    </div>
  );
}
