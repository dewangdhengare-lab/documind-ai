import React, { useState, useEffect } from 'react';
import { useDocuments } from '../hooks/useDocuments';
import { summarize, getSummaries, deleteSummary } from '../api/client';
import type { Summary } from '../types';
import { DocumentSelector } from '../components/DocumentSelector';
import { MarkdownRenderer } from '../components/MarkdownRenderer';
import { LoadingSpinner } from '../components/LoadingSpinner';
import {
  FileText,
  Sparkles,
  Copy,
  Download,
  Trash2,
  Check,
  Clock,
  Layers,
  ListOrdered,
  FileCheck2,
} from 'lucide-react';

export const Summarize: React.FC = () => {
  const { documents } = useDocuments();
  const [selectedDocId, setSelectedDocId] = useState('');
  const [summaryType, setSummaryType] = useState('executive');
  const [loading, setLoading] = useState(false);
  const [summaries, setSummaries] = useState<Summary[]>([]);
  const [currentSummary, setCurrentSummary] = useState<Summary | null>(null);
  const [copied, setCopied] = useState(false);

  const fetchSummariesList = async () => {
    try {
      const data = await getSummaries();
      setSummaries(data);
      if (data.length > 0 && !currentSummary) {
        setCurrentSummary(data[0]);
      }
    } catch (err) {
      console.error('Failed to load summaries:', err);
    }
  };

  useEffect(() => {
    fetchSummariesList();
  }, []);

  const handleGenerate = async () => {
    if (!selectedDocId) {
      alert('Please select a document first.');
      return;
    }
    setLoading(true);
    try {
      const result = await summarize(selectedDocId, summaryType);
      setCurrentSummary(result);
      setSummaries([result, ...summaries]);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Summarization failed');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (!currentSummary) return;
    navigator.clipboard.writeText(currentSummary.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!currentSummary) return;
    const blob = new Blob([currentSummary.content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `summary_${currentSummary.summary_type}_${currentSummary.id.slice(0, 8)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Delete this saved summary?')) {
      try {
        await deleteSummary(id);
        const updated = summaries.filter((s) => s.id !== id);
        setSummaries(updated);
        if (currentSummary?.id === id) {
          setCurrentSummary(updated.length > 0 ? updated[0] : null);
        }
      } catch (err) {
        console.error('Failed to delete summary:', err);
      }
    }
  };

  const summaryTypes = [
    { id: 'short', name: 'Short Summary', desc: '1-2 brief overview paragraphs', icon: FileCheck2 },
    { id: 'executive', name: 'Executive Summary', desc: 'Context, insights, metrics, & recommendations', icon: Sparkles },
    { id: 'detailed', name: 'Detailed Summary', desc: 'Comprehensive section-by-section breakdown', icon: Layers },
    { id: 'section_wise', name: 'Section-wise', desc: 'Detailed analysis organized by source headings', icon: ListOrdered },
    { id: 'key_points', name: 'Key Points', desc: 'Structured bulleted takeaways and highlights', icon: FileText },
    { id: 'facts_and_figures', name: 'Facts & Figures', desc: 'Metrics, numbers, dates, and quantitative data', icon: Clock },
  ];

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Document Summarization</h1>
        <p className="text-sm text-gray-500 mt-1">
          Generate grounded, factual summaries tailored to your preferred depth and format.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls Column */}
        <div className="lg:col-span-1 space-y-5">
          <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-xs space-y-4">
            <DocumentSelector
              multiple={false}
              documents={documents}
              value={selectedDocId}
              onChange={setSelectedDocId}
              label="Select Target Document"
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Summary Format</label>
              <div className="grid grid-cols-1 gap-2">
                {summaryTypes.map((type) => {
                  const Icon = type.icon;
                  const isSelected = summaryType === type.id;
                  return (
                    <button
                      key={type.id}
                      type="button"
                      onClick={() => setSummaryType(type.id)}
                      className={`flex items-start gap-3 p-2.5 rounded-lg border text-left cursor-pointer transition-all ${
                        isSelected
                          ? 'border-indigo-600 bg-indigo-50/70 text-indigo-900 shadow-xs'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50 text-gray-700'
                      }`}
                    >
                      <Icon className={`w-4 h-4 shrink-0 mt-0.5 ${isSelected ? 'text-indigo-600' : 'text-gray-400'}`} />
                      <div>
                        <p className="text-xs font-semibold">{type.name}</p>
                        <p className="text-[11px] text-gray-500">{type.desc}</p>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            <button
              onClick={handleGenerate}
              disabled={!selectedDocId || loading}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-200 disabled:text-gray-400 text-white rounded-lg text-sm font-medium transition-colors cursor-pointer shadow-xs"
            >
              {loading ? (
                <>
                  <LoadingSpinner size="sm" />
                  <span>Synthesizing Document...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Generate Summary</span>
                </>
              )}
            </button>
          </div>

          {/* Previous Summaries */}
          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-xs space-y-3">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Saved Summaries ({summaries.length})
            </h3>
            <div className="divide-y divide-gray-100 max-h-64 overflow-y-auto">
              {summaries.length === 0 ? (
                <p className="text-xs text-gray-400 py-3 text-center">No summaries generated yet.</p>
              ) : (
                summaries.map((s) => {
                  const isSelected = currentSummary?.id === s.id;
                  return (
                    <div
                      key={s.id}
                      onClick={() => setCurrentSummary(s)}
                      className={`group py-2.5 px-2 flex items-center justify-between text-xs rounded-md cursor-pointer transition-colors ${
                        isSelected ? 'bg-indigo-50 text-indigo-900 font-semibold' : 'hover:bg-gray-50 text-gray-700'
                      }`}
                    >
                      <div className="truncate mr-2">
                        <span className="capitalize">{s.summary_type.replace('_', ' ')}</span>
                        <p className="text-[10px] text-gray-400">
                          {new Date(s.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <button
                        onClick={(e) => handleDelete(s.id, e)}
                        className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-red-500 transition-opacity"
                        title="Delete summary"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>

        {/* Display Column */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 shadow-xs flex flex-col min-h-[500px]">
          {currentSummary ? (
            <>
              <div className="p-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
                <div>
                  <h3 className="text-sm font-semibold text-gray-900 capitalize">
                    {currentSummary.summary_type.replace('_', ' ')} Summary
                  </h3>
                  <p className="text-xs text-gray-400">
                    Generated on {new Date(currentSummary.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleCopy}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-700 bg-white border border-gray-200 rounded-md hover:bg-gray-50 transition-colors cursor-pointer"
                  >
                    {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copied ? 'Copied' : 'Copy'}</span>
                  </button>
                  <button
                    onClick={handleDownload}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-md hover:bg-indigo-100 transition-colors cursor-pointer"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Export (.md)</span>
                  </button>
                </div>
              </div>
              <div className="flex-1 p-6 overflow-y-auto">
                <MarkdownRenderer content={currentSummary.content} />
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-gray-400">
              <FileText className="w-12 h-12 text-gray-300 mb-3" />
              <h4 className="text-base font-semibold text-gray-700">No Summary Displayed</h4>
              <p className="text-xs text-gray-500 max-w-sm mt-1">
                Select a document and format on the left, then click "Generate Summary" to produce an AI synthesis.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
