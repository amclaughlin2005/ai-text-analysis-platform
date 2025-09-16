'use client';

import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Download, 
  Image, 
  FileImage, 
  FileText, 
  Share2, 
  Settings, 
  Check,
  AlertCircle,
  Palette,
  Maximize2
} from 'lucide-react';
import { WordCloudData } from '@/lib/types';
import { cn } from '@/lib/utils';

interface ExportOptions {
  format: 'png' | 'svg' | 'pdf' | 'json' | 'csv';
  width: number;
  height: number;
  quality: number;
  backgroundColor: string;
  includeMetadata: boolean;
  title?: string;
  description?: string;
  theme: string;
  layout: string;
}

interface WordCloudExportPanelProps {
  words: WordCloudData[];
  className?: string;
  currentTheme?: string;
  currentLayout?: string;
  onExport?: (options: ExportOptions) => void;
}

const EXPORT_FORMATS = [
  {
    id: 'png',
    label: 'PNG Image',
    description: 'High-quality raster image for web and print',
    icon: Image,
    fileSize: 'Medium',
    recommended: true
  },
  {
    id: 'svg',
    label: 'SVG Vector',
    description: 'Scalable vector graphics for unlimited scaling',
    icon: FileImage,
    fileSize: 'Small',
    recommended: false
  },
  {
    id: 'pdf',
    label: 'PDF Document',
    description: 'Professional document with analysis summary',
    icon: FileText,
    fileSize: 'Large',
    recommended: false
  },
  {
    id: 'json',
    label: 'JSON Data',
    description: 'Raw word cloud data for further analysis',
    icon: FileText,
    fileSize: 'Small',
    recommended: false
  },
  {
    id: 'csv',
    label: 'CSV Spreadsheet',
    description: 'Word frequency data in spreadsheet format',
    icon: FileText,
    fileSize: 'Small',
    recommended: false
  }
] as const;

const PRESET_DIMENSIONS = [
  { label: 'Social Media (1200×630)', width: 1200, height: 630 },
  { label: 'HD Display (1920×1080)', width: 1920, height: 1080 },
  { label: 'Print A4 (2480×3508)', width: 2480, height: 3508 },
  { label: 'Square (1000×1000)', width: 1000, height: 1000 },
  { label: 'Custom', width: 0, height: 0 }
];

const BACKGROUND_COLORS = [
  { label: 'White', value: '#FFFFFF', preview: 'bg-white' },
  { label: 'Light Gray', value: '#F8F9FA', preview: 'bg-gray-50' },
  { label: 'Dark', value: '#121212', preview: 'bg-gray-900' },
  { label: 'Blue', value: '#EBF8FF', preview: 'bg-blue-50' },
  { label: 'Green', value: '#F0FDF4', preview: 'bg-green-50' },
  { label: 'Transparent', value: 'transparent', preview: 'bg-gradient-to-br from-gray-100 to-white' }
];

export default function WordCloudExportPanel({
  words,
  className,
  currentTheme = 'default',
  currentLayout = 'spiral',
  onExport
}: WordCloudExportPanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedFormat, setSelectedFormat] = useState<ExportOptions['format']>('png');
  const [exportOptions, setExportOptions] = useState<ExportOptions>({
    format: 'png',
    width: 1200,
    height: 630,
    quality: 90,
    backgroundColor: '#FFFFFF',
    includeMetadata: true,
    title: 'Word Cloud Analysis',
    description: '',
    theme: currentTheme,
    layout: currentLayout
  });
  const [isCustomDimensions, setIsCustomDimensions] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Handle export format change
  const handleFormatChange = (format: ExportOptions['format']) => {
    setSelectedFormat(format);
    setExportOptions(prev => ({
      ...prev,
      format,
      // Adjust defaults based on format
      ...(format === 'svg' && { backgroundColor: 'transparent' }),
      ...(format === 'pdf' && { width: 2480, height: 3508 }), // A4 size
      ...(format === 'json' || format === 'csv') && { 
        backgroundColor: 'transparent',
        includeMetadata: true
      }
    }));
  };

  // Handle dimension preset change
  const handleDimensionPreset = (preset: typeof PRESET_DIMENSIONS[0]) => {
    if (preset.label === 'Custom') {
      setIsCustomDimensions(true);
    } else {
      setIsCustomDimensions(false);
      setExportOptions(prev => ({
        ...prev,
        width: preset.width,
        height: preset.height
      }));
    }
  };

  // Generate shareable link
  const generateShareLink = () => {
    const baseUrl = window.location.origin + window.location.pathname;
    const params = new URLSearchParams({
      theme: exportOptions.theme,
      layout: exportOptions.layout,
      bg: exportOptions.backgroundColor,
      words: words.slice(0, 20).map(w => w.word).join(',') // Top 20 words
    });
    
    return `${baseUrl}?${params.toString()}`;
  };

  // Copy share link to clipboard
  const copyShareLink = async () => {
    try {
      const link = generateShareLink();
      await navigator.clipboard.writeText(link);
      setExportSuccess(true);
      setTimeout(() => setExportSuccess(false), 2000);
    } catch (error) {
      setExportError('Failed to copy link to clipboard');
      setTimeout(() => setExportError(null), 3000);
    }
  };

  // Handle export
  const handleExport = async () => {
    setIsExporting(true);
    setExportError(null);

    try {
      // Update options with current theme/layout
      const finalOptions = {
        ...exportOptions,
        theme: currentTheme,
        layout: currentLayout
      };

      if (onExport) {
        await onExport(finalOptions);
      } else {
        // Default export behavior (you can implement actual export logic here)
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate export
      }

      setExportSuccess(true);
      setTimeout(() => {
        setExportSuccess(false);
        setIsOpen(false);
      }, 2000);

    } catch (error) {
      setExportError(error instanceof Error ? error.message : 'Export failed');
    } finally {
      setIsExporting(false);
    }
  };

  // Calculate estimated file size
  const getEstimatedFileSize = () => {
    const pixelCount = exportOptions.width * exportOptions.height;
    
    switch (exportOptions.format) {
      case 'png':
        return `~${Math.round(pixelCount * 4 / 1024 / 1024 * exportOptions.quality / 100)}MB`;
      case 'svg':
        return `~${Math.round(words.length * 0.1)}KB`;
      case 'pdf':
        return `~${Math.round(pixelCount * 3 / 1024 / 1024)}MB`;
      case 'json':
        return `~${Math.round(words.length * 0.2)}KB`;
      case 'csv':
        return `~${Math.round(words.length * 0.1)}KB`;
      default:
        return 'Unknown';
    }
  };

  const selectedFormatConfig = EXPORT_FORMATS.find(f => f.id === selectedFormat);

  return (
    <div className={cn("relative", className)}>
      {/* Export Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors shadow-sm"
        title="Export word cloud"
      >
        <Download className="h-4 w-4 text-gray-600" />
        <span className="text-sm font-medium text-gray-700">Export</span>
      </button>

      {/* Export Panel */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
              onClick={() => setIsOpen(false)}
            />

            {/* Panel */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              className="absolute top-full right-0 mt-2 w-96 bg-white rounded-xl shadow-xl border z-50 overflow-hidden"
            >
              {/* Header */}
              <div className="px-4 py-3 bg-gradient-to-r from-blue-50 to-indigo-50 border-b">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">Export Word Cloud</h3>
                  <button
                    onClick={() => setIsOpen(false)}
                    className="p-1 hover:bg-white/60 rounded-lg transition-colors"
                  >
                    ×
                  </button>
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  Choose format and customize export settings
                </p>
              </div>

              <div className="p-4 space-y-6 max-h-96 overflow-y-auto">
                {/* Format Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Export Format
                  </label>
                  <div className="grid grid-cols-1 gap-2">
                    {EXPORT_FORMATS.map((format) => (
                      <button
                        key={format.id}
                        onClick={() => handleFormatChange(format.id)}
                        className={cn(
                          "flex items-center justify-between p-3 border rounded-lg text-left transition-all",
                          selectedFormat === format.id
                            ? "border-blue-200 bg-blue-50 ring-2 ring-blue-100"
                            : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                        )}
                      >
                        <div className="flex items-center gap-3">
                          <format.icon className="h-4 w-4 text-gray-600" />
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-gray-900">{format.label}</span>
                              {format.recommended && (
                                <span className="px-1.5 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">
                                  Recommended
                                </span>
                              )}
                            </div>
                            <p className="text-xs text-gray-500">{format.description}</p>
                          </div>
                        </div>
                        <span className="text-xs text-gray-400">{format.fileSize}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Dimensions (for image formats) */}
                {(selectedFormat === 'png' || selectedFormat === 'svg' || selectedFormat === 'pdf') && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      Dimensions
                    </label>
                    <div className="space-y-2">
                      {PRESET_DIMENSIONS.map((preset) => (
                        <button
                          key={preset.label}
                          onClick={() => handleDimensionPreset(preset)}
                          className={cn(
                            "w-full p-2 text-left border rounded-lg text-sm transition-colors",
                            ((!isCustomDimensions && exportOptions.width === preset.width) || 
                             (isCustomDimensions && preset.label === 'Custom'))
                              ? "border-blue-200 bg-blue-50"
                              : "border-gray-200 hover:bg-gray-50"
                          )}
                        >
                          {preset.label}
                        </button>
                      ))}
                    </div>

                    {isCustomDimensions && (
                      <div className="mt-3 grid grid-cols-2 gap-2">
                        <div>
                          <label className="block text-xs text-gray-600 mb-1">Width</label>
                          <input
                            type="number"
                            value={exportOptions.width}
                            onChange={(e) => setExportOptions(prev => ({ 
                              ...prev, 
                              width: parseInt(e.target.value) || 0 
                            }))}
                            className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                            min="100"
                            max="4000"
                          />
                        </div>
                        <div>
                          <label className="block text-xs text-gray-600 mb-1">Height</label>
                          <input
                            type="number"
                            value={exportOptions.height}
                            onChange={(e) => setExportOptions(prev => ({ 
                              ...prev, 
                              height: parseInt(e.target.value) || 0 
                            }))}
                            className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                            min="100"
                            max="4000"
                          />
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Background Color (for image formats) */}
                {(selectedFormat === 'png' || selectedFormat === 'svg') && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      Background
                    </label>
                    <div className="grid grid-cols-3 gap-2">
                      {BACKGROUND_COLORS.map((color) => (
                        <button
                          key={color.value}
                          onClick={() => setExportOptions(prev => ({ 
                            ...prev, 
                            backgroundColor: color.value 
                          }))}
                          className={cn(
                            "flex items-center gap-2 p-2 border rounded-lg text-xs transition-all",
                            exportOptions.backgroundColor === color.value
                              ? "border-blue-200 bg-blue-50 ring-1 ring-blue-100"
                              : "border-gray-200 hover:border-gray-300"
                          )}
                        >
                          <div className={cn("w-4 h-4 rounded border border-gray-300", color.preview)} />
                          <span className="truncate">{color.label}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Quality (for PNG) */}
                {selectedFormat === 'png' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      Quality: {exportOptions.quality}%
                    </label>
                    <input
                      type="range"
                      min="60"
                      max="100"
                      value={exportOptions.quality}
                      onChange={(e) => setExportOptions(prev => ({ 
                        ...prev, 
                        quality: parseInt(e.target.value) 
                      }))}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>Lower size</span>
                      <span>Higher quality</span>
                    </div>
                  </div>
                )}

                {/* Metadata */}
                <div>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={exportOptions.includeMetadata}
                      onChange={(e) => setExportOptions(prev => ({ 
                        ...prev, 
                        includeMetadata: e.target.checked 
                      }))}
                      className="rounded"
                    />
                    <span className="text-sm text-gray-700">Include metadata</span>
                  </label>
                  <p className="text-xs text-gray-500 mt-1">
                    Embed analysis details in the exported file
                  </p>
                </div>

                {/* File Size Estimate */}
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Estimated file size:</span>
                    <span className="font-medium">{getEstimatedFileSize()}</span>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="px-4 py-3 bg-gray-50 border-t space-y-2">
                {/* Share Link */}
                <button
                  onClick={copyShareLink}
                  className="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <Share2 className="h-4 w-4" />
                  Copy Shareable Link
                </button>

                {/* Export Button */}
                <button
                  onClick={handleExport}
                  disabled={isExporting}
                  className={cn(
                    "w-full flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium rounded-lg transition-colors",
                    isExporting
                      ? "bg-gray-400 text-white cursor-not-allowed"
                      : "bg-blue-600 text-white hover:bg-blue-700"
                  )}
                >
                  {isExporting ? (
                    <>
                      <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
                      Exporting...
                    </>
                  ) : exportSuccess ? (
                    <>
                      <Check className="h-4 w-4" />
                      Exported Successfully!
                    </>
                  ) : (
                    <>
                      <Download className="h-4 w-4" />
                      Export {selectedFormatConfig?.label}
                    </>
                  )}
                </button>

                {/* Error Message */}
                {exportError && (
                  <div className="flex items-center gap-2 p-2 bg-red-50 border border-red-200 rounded-lg">
                    <AlertCircle className="h-4 w-4 text-red-600 flex-shrink-0" />
                    <span className="text-sm text-red-700">{exportError}</span>
                  </div>
                )}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
