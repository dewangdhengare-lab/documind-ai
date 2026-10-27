import React, { useState, useEffect } from 'react';
import { useDocuments } from '../hooks/useDocuments';
import {
  generateReport,
  getReports,
  updateReport,
  deleteReport,
  exportReport,
} from '../api/client';
import type { Report } from '../types';
import { DocumentSelector } from '../components/DocumentSelector';
import { MarkdownRenderer } from '../components/MarkdownRenderer';
import { LoadingSpinner } from '../components/LoadingSpinner';
import {
  FileOutput,
  Sparkles,
  Download,
  Edit3,
  Save,
  Trash2,
  Eye,
} from 'lucide-react';

const AVAILABLE_SECTIONS = [
  'Executive Summary',
  'Introduction & Objectives',
  'Key Findings & Metrics',
  'Detailed Analysis & Themes',
  'Risk Assessment',
  'Recommendations & Next Steps',
  'Conclusion',
];

export const Reports: React.FC = () => {
  const { documents } = useDocuments();
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);
  const [reportType, setReportType] = useState('analysis');
  const [title, setTitle] = useState('');
  const [purpose, setPurpose] = useState('');
  const [audience, setAudience] = useState('');
  const [sections, setSections] = useState<string[]>(AVAILABLE_SECTIONS);
  const [detailLevel, setDetailLevel] = useState('medium');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [exporting, setExporting] = useState<string | null>(null);

  const [reports, setReports] = useState<Report[]>([]);
  const [currentReport, setCurrentReport] = useState<Report | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState('');

  const fetchReports = async () => {
    try {
      const data = await getReports();
      setReports(data);
      if (data.length > 0 && !currentReport) {
        setCurrentReport(data[0]);
        setEditedContent(data[0].content);
      }
    } catch (err) {
      console.error('Failed to load reports:', err);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleToggleSection = (sec: string) => {
    if (sections.includes(sec)) {
      if (sections.length > 1) {
        setSections(sections.filter((s) => s !== sec));
      }
    } else {
      setSections([...sections, sec]);
    }
  };

  const handleGenerate = async () => {
    if (selectedDocIds.length === 0) {
      alert('Please select at least one document.');
      return;
    }
    setLoading(true);
    setIsEditing(false);
    try {
      const newReport = await generateReport(selectedDocIds, reportType, {
        title: title || 'Executive Document Intelligence Report',
        purpose: purpose || 'Strategic assessment of uploaded documentation',
        audience: audience || 'Management and Key Stakeholders',
        sections,
        detail_level: detailLevel,
      });
      setCurrentReport(newReport);
      setEditedContent(newReport.content);
      setReports([newReport, ...reports]);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Report generation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveEdit = async () => {
    if (!currentReport) return;
    setSaving(true);
    try {
      const updated = await updateReport(currentReport.id, editedContent);
      setCurrentReport(updated);
      setIsEditing(false);
      setReports(reports.map((r) => (r.id === updated.id ? updated : r)));
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Failed to save report edit');
    } finally {
      setSaving(false);
    }
  };

  const handleExport = async (format: 'pdf' | 'docx') => {
    if (!currentReport) return;
    setExporting(format);
    try {
      const blob = await exportReport(currentReport.id, format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report_${currentReport.id.slice(0, 8)}.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export failed:', err);
      alert('Failed to export report');
    } finally {
      setExporting(null);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Delete this report?')) {
      try {
        await deleteReport(id);
        const updated = reports.filter((r) => r.id !== id);
        setReports(updated);
        if (currentReport?.id === id) {
          setCurrentReport(updated.length > 0 ? updated[0] : null);
          setEditedContent(updated.length > 0 ? updated[0].content : '');
        }
      } catch (err) {
        console.error('Failed to delete report:', err);
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Report Generator</h1>
        <p className="text-sm text-gray-500 mt-1">
          Synthesize professional, executive-ready reports from single or multi-document inputs with custom sections and direct PDF/DOCX export.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Setup Column */}
        <div className="lg:col-span-1 space-y-5">
          <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-xs space-y-4">
            <DocumentSelector
              multiple={true}
              documents={documents}
              value={selectedDocIds}
              onChange={setSelectedDocIds}
              label="Select Source Documents"
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Report Type
              </label>
              <select
                value={reportType}
                onChange={(e) => setReportType(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-white border border-gray-300 rounded-lg text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-xs cursor-pointer"
              >
                <option value="analysis">Document Analysis Report</option>
                <option value="summary">Executive Summary Report</option>
                <option value="research">Research & Insights Report</option>
                <option value="comparison">Comparative Evaluation Report</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Report Title (Optional)
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Q3 Strategic Operations Review"
                className="w-full px-3.5 py-2 bg-white border border-gray-300 rounded-lg text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-xs"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Purpose</label>
                <input
                  type="text"
                  value={purpose}
                  onChange={(e) => setPurpose(e.target.value)}
                  placeholder="Decision making..."
                  className="w-full px-3 py-1.5 bg-white border border-gray-300 rounded-md text-xs text-gray-900"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Audience</label>
                <input
                  type="text"
                  value={audience}
                  onChange={(e) => setAudience(e.target.value)}
                  placeholder="Executives / Board"
                  className="w-full px-3 py-1.5 bg-white border border-gray-300 rounded-md text-xs text-gray-900"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1.5">
                Sections to Include
              </label>
              <div className="space-y-1.5 max-h-40 overflow-y-auto p-1 border border-gray-200 rounded-md">
                {AVAILABLE_SECTIONS.map((sec) => {
                  const isChecked = sections.includes(sec);
                  return (
                    <label
                      key={sec}
                      className="flex items-center gap-2 p-1.5 rounded hover:bg-gray-50 cursor-pointer text-xs text-gray-700"
                    >
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => handleToggleSection(sec)}
                        className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                      />
                      <span>{sec}</span>
                    </label>
                  );
                })}
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1.5">
                Level of Detail
              </label>
              <div className="grid grid-cols-3 gap-2">
                {['brief', 'medium', 'detailed'].map((lvl) => (
                  <button
                    key={lvl}
                    type="button"
                    onClick={() => setDetailLevel(lvl)}
                    className={`py-1.5 text-xs font-medium rounded-md capitalize border cursor-pointer transition-all ${
                      detailLevel === lvl
                        ? 'border-indigo-600 bg-indigo-50 text-indigo-700 font-semibold'
                        : 'border-gray-200 text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    {lvl}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={handleGenerate}
              disabled={selectedDocIds.length === 0 || loading}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-200 disabled:text-gray-400 text-white rounded-lg text-sm font-medium transition-colors cursor-pointer shadow-xs"
            >
              {loading ? (
                <>
                  <LoadingSpinner size="sm" />
                  <span>Synthesizing Report...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Generate Report</span>
                </>
              )}
            </button>
          </div>

          {/* Past Reports List */}
          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-xs space-y-3">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Saved Reports ({reports.length})
            </h3>
            <div className="divide-y divide-gray-100 max-h-64 overflow-y-auto">
              {reports.length === 0 ? (
                <p className="text-xs text-gray-400 py-3 text-center">No reports generated yet.</p>
              ) : (
                reports.map((r) => {
                  const isSelected = currentReport?.id === r.id;
                  const cfg = r.config as any;
                  return (
                    <div
                      key={r.id}
                      onClick={() => {
                        setCurrentReport(r);
                        setEditedContent(r.content);
                        setIsEditing(false);
                      }}
                      className={`group py-2.5 px-2 flex items-center justify-between text-xs rounded-md cursor-pointer transition-colors ${
                        isSelected ? 'bg-indigo-50 text-indigo-900 font-semibold' : 'hover:bg-gray-50 text-gray-700'
                      }`}
                    >
                      <div className="truncate mr-2">
                        <span className="font-medium truncate block">
                          {cfg?.title || `${r.report_type} Report`}
                        </span>
                        <p className="text-[10px] text-gray-400">
                          {new Date(r.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <button
                        onClick={(e) => handleDelete(r.id, e)}
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

        {/* Report Workspace Column */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 shadow-xs flex flex-col min-h-[500px]">
          {currentReport ? (
            <>
              {/* Toolbar */}
              <div className="p-4 border-b border-gray-100 flex flex-wrap items-center justify-between gap-3 bg-gray-50/50">
                <div>
                  <h3 className="text-sm font-semibold text-gray-900">
                    {(currentReport.config as any)?.title || 'Document Intelligence Report'}
                  </h3>
                  <p className="text-xs text-gray-400">
                    Created on {new Date(currentReport.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setIsEditing(!isEditing)}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-700 bg-white border border-gray-200 rounded-md hover:bg-gray-50 transition-colors cursor-pointer"
                  >
                    {isEditing ? <Eye className="w-3.5 h-3.5" /> : <Edit3 className="w-3.5 h-3.5" />}
                    <span>{isEditing ? 'Preview' : 'Edit Text'}</span>
                  </button>
                  {isEditing && (
                    <button
                      onClick={handleSaveEdit}
                      disabled={saving}
                      className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 transition-colors cursor-pointer"
                    >
                      {saving ? <LoadingSpinner size="sm" /> : <Save className="w-3.5 h-3.5" />}
                      <span>Save</span>
                    </button>
                  )}
                  <button
                    onClick={() => handleExport('pdf')}
                    disabled={exporting !== null}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-rose-700 bg-rose-50 border border-rose-200 rounded-md hover:bg-rose-100 transition-colors cursor-pointer disabled:opacity-50"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>{exporting === 'pdf' ? 'Exporting...' : 'PDF'}</span>
                  </button>
                  <button
                    onClick={() => handleExport('docx')}
                    disabled={exporting !== null}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-blue-700 bg-blue-50 border border-blue-200 rounded-md hover:bg-blue-100 transition-colors cursor-pointer disabled:opacity-50"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>{exporting === 'docx' ? 'Exporting...' : 'DOCX'}</span>
                  </button>
                </div>
              </div>

              {/* Body */}
              <div className="flex-1 p-6 overflow-y-auto">
                {isEditing ? (
                  <textarea
                    value={editedContent}
                    onChange={(e) => setEditedContent(e.target.value)}
                    rows={24}
                    className="w-full p-4 font-mono text-xs text-gray-900 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none leading-relaxed"
                  />
                ) : (
                  <MarkdownRenderer content={currentReport.content} />
                )}
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-gray-400">
              <FileOutput className="w-12 h-12 text-gray-300 mb-3" />
              <h4 className="text-base font-semibold text-gray-700">No Report Generated</h4>
              <p className="text-xs text-gray-500 max-w-sm mt-1">
                Configure your report parameters on the left and click "Generate Report" to author a comprehensive document.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
