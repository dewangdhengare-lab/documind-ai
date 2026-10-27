import React, { useState, useEffect } from 'react';
import { useDocuments } from '../hooks/useDocuments';
import { extract, getExtractions, deleteExtraction, exportExtraction } from '../api/client';
import type { Extraction } from '../types';
import { DocumentSelector } from '../components/DocumentSelector';
import { LoadingSpinner } from '../components/LoadingSpinner';
import {
  Table2,
  Sparkles,
  Trash2,
  FileSpreadsheet,
  FileCode,
  Info,
} from 'lucide-react';

const PREDEFINED_TEMPLATES = [
  {
    name: 'Custom Query',
    instruction: '',
  },
  {
    name: 'Project Information',
    instruction: 'Extract all project names, objectives, milestones, deadlines, budgets, responsible leaders, and project statuses.',
  },
  {
    name: 'Financial Data & Metrics',
    instruction: 'Extract all financial figures, revenue numbers, expenses, profit margins, growth percentages, and budget allocations with their respective dates and categories.',
  },
  {
    name: 'Key Dates & Deadlines',
    instruction: 'Extract all dates, milestones, deadlines, project phases, and time-bound commitments mentioned in the document.',
  },
  {
    name: 'Risks & Mitigations',
    instruction: 'Extract all identified risks, their severity level, potential impact, and the specified mitigation strategies or contingency actions.',
  },
  {
    name: 'Stakeholders & Contacts',
    instruction: 'Extract all individuals, their job titles or organizations, roles/responsibilities, and any contact details mentioned.',
  },
];

export const Extract: React.FC = () => {
  const { documents } = useDocuments();
  const [selectedDocId, setSelectedDocId] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState('Project Information');
  const [instruction, setInstruction] = useState(PREDEFINED_TEMPLATES[1].instruction);
  const [loading, setLoading] = useState(false);
  const [extractions, setExtractions] = useState<Extraction[]>([]);
  const [currentExt, setCurrentExt] = useState<Extraction | null>(null);

  const fetchExtractions = async () => {
    try {
      const data = await getExtractions();
      setExtractions(data);
      if (data.length > 0 && !currentExt) {
        setCurrentExt(data[0]);
      }
    } catch (err) {
      console.error('Failed to load extractions:', err);
    }
  };

  useEffect(() => {
    fetchExtractions();
  }, []);

  const handleTemplateChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const templateName = e.target.value;
    setSelectedTemplate(templateName);
    const tmpl = PREDEFINED_TEMPLATES.find((t) => t.name === templateName);
    if (tmpl) {
      setInstruction(tmpl.instruction);
    }
  };

  const handleExtract = async () => {
    if (!selectedDocId) {
      alert('Please select a document.');
      return;
    }
    if (!instruction.trim()) {
      alert('Please enter an extraction instruction.');
      return;
    }

    setLoading(true);
    try {
      const result = await extract(selectedDocId, instruction);
      setCurrentExt(result);
      setExtractions([result, ...extractions]);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Extraction failed');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: 'csv' | 'json') => {
    if (!currentExt) return;
    try {
      const blob = await exportExtraction(currentExt.id, format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `extraction_${currentExt.id.slice(0, 8)}.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export failed:', err);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Delete this extraction?')) {
      try {
        await deleteExtraction(id);
        const updated = extractions.filter((x) => x.id !== id);
        setExtractions(updated);
        if (currentExt?.id === id) {
          setCurrentExt(updated.length > 0 ? updated[0] : null);
        }
      } catch (err) {
        console.error('Failed to delete extraction:', err);
      }
    }
  };

  // Parse result object safely
  const parsedData = React.useMemo(() => {
    if (!currentExt?.result) return null;
    const res = currentExt.result as any;
    if (typeof res === 'string') {
      try {
        return JSON.parse(res);
      } catch {
        return { summary: res };
      }
    }
    return res;
  }, [currentExt]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Information Extraction</h1>
        <p className="text-sm text-gray-500 mt-1">
          Extract entities, tabular rows, metrics, and key data points from documents into structured formats.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form Column */}
        <div className="lg:col-span-1 space-y-5">
          <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-xs space-y-4">
            <DocumentSelector
              multiple={false}
              documents={documents}
              value={selectedDocId}
              onChange={setSelectedDocId}
              label="Select Document"
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Predefined Template
              </label>
              <select
                value={selectedTemplate}
                onChange={handleTemplateChange}
                className="w-full px-3.5 py-2.5 bg-white border border-gray-300 rounded-lg text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-xs cursor-pointer"
              >
                {PREDEFINED_TEMPLATES.map((tmpl) => (
                  <option key={tmpl.name} value={tmpl.name}>
                    {tmpl.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Extraction Instruction
              </label>
              <textarea
                value={instruction}
                onChange={(e) => setInstruction(e.target.value)}
                placeholder="Specify what fields and entities to extract..."
                rows={4}
                className="w-full px-3.5 py-2.5 bg-white border border-gray-300 rounded-lg text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-xs resize-none"
              />
            </div>

            <button
              onClick={handleExtract}
              disabled={!selectedDocId || !instruction.trim() || loading}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-200 disabled:text-gray-400 text-white rounded-lg text-sm font-medium transition-colors cursor-pointer shadow-xs"
            >
              {loading ? (
                <>
                  <LoadingSpinner size="sm" />
                  <span>Parsing & Extracting...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Extract Structured Data</span>
                </>
              )}
            </button>
          </div>

          {/* Past Extractions */}
          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-xs space-y-3">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Past Extractions ({extractions.length})
            </h3>
            <div className="divide-y divide-gray-100 max-h-64 overflow-y-auto">
              {extractions.length === 0 ? (
                <p className="text-xs text-gray-400 py-3 text-center">No extractions yet.</p>
              ) : (
                extractions.map((x) => {
                  const isSelected = currentExt?.id === x.id;
                  return (
                    <div
                      key={x.id}
                      onClick={() => setCurrentExt(x)}
                      className={`group py-2.5 px-2 flex items-center justify-between text-xs rounded-md cursor-pointer transition-colors ${
                        isSelected ? 'bg-indigo-50 text-indigo-900 font-semibold' : 'hover:bg-gray-50 text-gray-700'
                      }`}
                    >
                      <div className="truncate mr-2">
                        <span className="truncate block font-medium">{x.instruction.slice(0, 40)}...</span>
                        <p className="text-[10px] text-gray-400">
                          {new Date(x.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <button
                        onClick={(e) => handleDelete(x.id, e)}
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
          {currentExt && parsedData ? (
            <>
              {/* Toolbar */}
              <div className="p-4 border-b border-gray-100 flex flex-wrap items-center justify-between gap-3 bg-gray-50/50">
                <div>
                  <h3 className="text-sm font-semibold text-gray-900">
                    {parsedData.title || 'Structured Extraction'}
                  </h3>
                  <p className="text-xs text-gray-400">
                    {new Date(currentExt.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleExport('csv')}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-md hover:bg-emerald-100 transition-colors cursor-pointer"
                  >
                    <FileSpreadsheet className="w-3.5 h-3.5" />
                    <span>Export CSV</span>
                  </button>
                  <button
                    onClick={() => handleExport('json')}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-md hover:bg-indigo-100 transition-colors cursor-pointer"
                  >
                    <FileCode className="w-3.5 h-3.5" />
                    <span>Export JSON</span>
                  </button>
                </div>
              </div>

              {/* Data Content */}
              <div className="p-6 overflow-y-auto space-y-5">
                {parsedData.summary && (
                  <div className="p-3.5 rounded-lg bg-indigo-50/70 border border-indigo-100 text-xs text-indigo-900 flex items-start gap-2.5">
                    <Info className="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" />
                    <p>{parsedData.summary}</p>
                  </div>
                )}

                {/* Structured Table */}
                {parsedData.rows && Array.isArray(parsedData.rows) && parsedData.rows.length > 0 ? (
                  <div className="overflow-x-auto border border-gray-200 rounded-lg shadow-2xs">
                    <table className="min-w-full divide-y divide-gray-200 text-xs">
                      <thead className="bg-gray-50">
                        <tr>
                          {(parsedData.headers || Object.keys(parsedData.rows[0])).map(
                            (header: string, idx: number) => (
                              <th
                                key={idx}
                                className="px-4 py-2.5 text-left font-semibold text-gray-700 uppercase tracking-wider"
                              >
                                {header}
                              </th>
                            )
                          )}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100 bg-white">
                        {parsedData.rows.map((row: any, rIdx: number) => (
                          <tr key={rIdx} className="hover:bg-gray-50/70">
                            {(parsedData.headers || Object.keys(parsedData.rows[0])).map(
                              (header: string, cIdx: number) => {
                                const val = row[header];
                                const isMissing = val === null || val === undefined || val === 'Not Specified';
                                return (
                                  <td
                                    key={cIdx}
                                    className={`px-4 py-2.5 whitespace-normal ${
                                      isMissing ? 'text-gray-400 italic' : 'text-gray-800'
                                    }`}
                                  >
                                    {isMissing ? 'Not Specified' : String(val)}
                                  </td>
                                );
                              }
                            )}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <pre className="p-4 bg-gray-50 rounded-lg text-xs font-mono overflow-x-auto border border-gray-200 text-gray-800">
                    {JSON.stringify(parsedData, null, 2)}
                  </pre>
                )}

                {parsedData.source_notes && (
                  <p className="text-[11px] text-gray-400 italic">
                    Grounding Notes: {parsedData.source_notes}
                  </p>
                )}
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-gray-400">
              <Table2 className="w-12 h-12 text-gray-300 mb-3" />
              <h4 className="text-base font-semibold text-gray-700">No Data Extracted</h4>
              <p className="text-xs text-gray-500 max-w-sm mt-1">
                Select a document and choose a template or enter custom instructions on the left to extract structured tables.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
