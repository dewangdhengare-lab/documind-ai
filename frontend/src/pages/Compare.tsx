import React, { useState, useEffect } from 'react';
import { useDocuments } from '../hooks/useDocuments';
import { compare, getComparisons, deleteComparison } from '../api/client';
import type { Comparison } from '../types';
import { DocumentSelector } from '../components/DocumentSelector';
import { LoadingSpinner } from '../components/LoadingSpinner';
import {
  GitCompare,
  AlertTriangle,
  CheckCircle,
  HelpCircle,
  Download,
  Trash2,
} from 'lucide-react';

export const Compare: React.FC = () => {
  const { documents } = useDocuments();
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [comparisons, setComparisons] = useState<Comparison[]>([]);
  const [currentComp, setCurrentComp] = useState<Comparison | null>(null);

  const fetchComparisons = async () => {
    try {
      const data = await getComparisons();
      setComparisons(data);
      if (data.length > 0 && !currentComp) {
        setCurrentComp(data[0]);
      }
    } catch (err) {
      console.error('Failed to load comparisons:', err);
    }
  };

  useEffect(() => {
    fetchComparisons();
  }, []);

  const handleCompare = async () => {
    if (selectedDocIds.length < 2) {
      alert('Please select at least 2 documents to compare.');
      return;
    }

    setLoading(true);
    try {
      const result = await compare(selectedDocIds);
      setCurrentComp(result);
      setComparisons([result, ...comparisons]);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Comparison failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Delete this comparison report?')) {
      try {
        await deleteComparison(id);
        const updated = comparisons.filter((c) => c.id !== id);
        setComparisons(updated);
        if (currentComp?.id === id) {
          setCurrentComp(updated.length > 0 ? updated[0] : null);
        }
      } catch (err) {
        console.error('Failed to delete comparison:', err);
      }
    }
  };

  const handleDownload = () => {
    if (!currentComp) return;
    const blob = new Blob([JSON.stringify(currentComp.result, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `comparison_${currentComp.id.slice(0, 8)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const resultData = currentComp?.result as any;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Document Comparison</h1>
        <p className="text-sm text-gray-500 mt-1">
          Perform multi-document comparative analysis to highlight differences, shared themes, and potential contradictions.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls Column */}
        <div className="lg:col-span-1 space-y-5">
          <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-xs space-y-4">
            <DocumentSelector
              multiple={true}
              documents={documents}
              value={selectedDocIds}
              onChange={setSelectedDocIds}
              label="Select Documents to Compare (2-5)"
            />

            <button
              onClick={handleCompare}
              disabled={selectedDocIds.length < 2 || loading}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-200 disabled:text-gray-400 text-white rounded-lg text-sm font-medium transition-colors cursor-pointer shadow-xs"
            >
              {loading ? (
                <>
                  <LoadingSpinner size="sm" />
                  <span>Cross-Analyzing Content...</span>
                </>
              ) : (
                <>
                  <GitCompare className="w-4 h-4" />
                  <span>Compare Selected Documents</span>
                </>
              )}
            </button>
          </div>

          {/* Past Comparisons */}
          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-xs space-y-3">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Saved Comparisons ({comparisons.length})
            </h3>
            <div className="divide-y divide-gray-100 max-h-64 overflow-y-auto">
              {comparisons.length === 0 ? (
                <p className="text-xs text-gray-400 py-3 text-center">No comparisons yet.</p>
              ) : (
                comparisons.map((c) => {
                  const isSelected = currentComp?.id === c.id;
                  return (
                    <div
                      key={c.id}
                      onClick={() => setCurrentComp(c)}
                      className={`group py-2.5 px-2 flex items-center justify-between text-xs rounded-md cursor-pointer transition-colors ${
                        isSelected ? 'bg-indigo-50 text-indigo-900 font-semibold' : 'hover:bg-gray-50 text-gray-700'
                      }`}
                    >
                      <div className="truncate mr-2">
                        <span className="font-medium">
                          {c.document_ids?.length || 2} Documents Analysis
                        </span>
                        <p className="text-[10px] text-gray-400">
                          {new Date(c.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <button
                        onClick={(e) => handleDelete(c.id, e)}
                        className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-red-500 transition-opacity"
                        title="Delete"
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

        {/* Results View */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 shadow-xs flex flex-col min-h-[500px]">
          {currentComp && resultData ? (
            <>
              {/* Toolbar */}
              <div className="p-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
                <div>
                  <h3 className="text-sm font-semibold text-gray-900">
                    Cross-Document Comparison Analysis
                  </h3>
                  <p className="text-xs text-gray-400">
                    {new Date(currentComp.created_at).toLocaleString()}
                  </p>
                </div>
                <button
                  onClick={handleDownload}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-md hover:bg-indigo-100 transition-colors cursor-pointer"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Export JSON</span>
                </button>
              </div>

              {/* Comparison Sections */}
              <div className="p-6 overflow-y-auto space-y-6">
                {/* High-level Summary */}
                {resultData.summary && (
                  <div className="p-4 rounded-xl bg-gray-50 border border-gray-200 text-sm text-gray-800 leading-relaxed">
                    <p className="font-semibold text-gray-900 text-xs uppercase tracking-wider mb-1">
                      Overview
                    </p>
                    {resultData.summary}
                  </div>
                )}

                {/* Contradictions & Divergences */}
                {resultData.contradictions && resultData.contradictions.length > 0 && (
                  <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 space-y-2">
                    <div className="flex items-center gap-2 text-amber-800 font-semibold text-xs uppercase tracking-wider">
                      <AlertTriangle className="w-4 h-4 text-amber-600" />
                      <span>Potential Contradictions / Inconsistencies</span>
                    </div>
                    <ul className="list-disc list-inside space-y-1 text-xs text-amber-900 leading-relaxed">
                      {resultData.contradictions.map((c: string, idx: number) => (
                        <li key={idx}>{c}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Similarities & Differences */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Similarities */}
                  <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/40 space-y-2">
                    <div className="flex items-center gap-2 text-emerald-800 font-semibold text-xs uppercase tracking-wider">
                      <CheckCircle className="w-4 h-4 text-emerald-600" />
                      <span>Shared Similarities</span>
                    </div>
                    <ul className="space-y-1.5 text-xs text-emerald-950">
                      {resultData.similarities?.map((s: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-1.5">
                          <span className="text-emerald-500 font-bold">&bull;</span>
                          <span>{s}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Differences */}
                  <div className="p-4 rounded-xl border border-blue-200 bg-blue-50/40 space-y-2">
                    <div className="flex items-center gap-2 text-blue-800 font-semibold text-xs uppercase tracking-wider">
                      <HelpCircle className="w-4 h-4 text-blue-600" />
                      <span>Key Differences</span>
                    </div>
                    <ul className="space-y-1.5 text-xs text-blue-950">
                      {resultData.differences?.map((d: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-1.5">
                          <span className="text-blue-500 font-bold">&bull;</span>
                          <span>{d}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Comparison Table */}
                {resultData.comparison_table && resultData.comparison_table.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Comparative Aspect Breakdown
                    </h4>
                    <div className="overflow-x-auto border border-gray-200 rounded-lg shadow-2xs">
                      <table className="min-w-full divide-y divide-gray-200 text-xs">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-4 py-2.5 text-left font-semibold text-gray-700">
                              Aspect
                            </th>
                            {Object.keys(resultData.comparison_table[0].values || {}).map(
                              (docKey, idx) => (
                                <th key={idx} className="px-4 py-2.5 text-left font-semibold text-gray-700">
                                  {docKey}
                                </th>
                              )
                            )}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100 bg-white">
                          {resultData.comparison_table.map((row: any, rIdx: number) => (
                            <tr key={rIdx} className="hover:bg-gray-50/70">
                              <td className="px-4 py-2.5 font-medium text-gray-900 bg-gray-50/30 whitespace-nowrap">
                                {row.aspect}
                              </td>
                              {Object.values(row.values || {}).map((val: any, cIdx: number) => (
                                <td key={cIdx} className="px-4 py-2.5 text-gray-700 whitespace-normal">
                                  {String(val)}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {/* Synthesis & Conclusion */}
                {resultData.conclusion && (
                  <div className="p-4 rounded-xl bg-indigo-50/60 border border-indigo-100 text-xs text-indigo-950 space-y-1.5">
                    <p className="font-semibold text-indigo-900 text-xs uppercase tracking-wider">
                      Synthesized Conclusion
                    </p>
                    <p className="leading-relaxed whitespace-pre-wrap">{resultData.conclusion}</p>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-gray-400">
              <GitCompare className="w-12 h-12 text-gray-300 mb-3" />
              <h4 className="text-base font-semibold text-gray-700">No Comparison Generated</h4>
              <p className="text-xs text-gray-500 max-w-sm mt-1">
                Select at least two documents on the left and click "Compare Selected Documents" to perform a full synthesis.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
