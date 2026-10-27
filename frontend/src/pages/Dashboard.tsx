import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  MessageSquare,
  FileText,
  Table2,
  GitCompare,
  Brain,
  FileOutput,
  FolderOpen,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Upload,
} from 'lucide-react';
import { getDocuments } from '../api/client';
import type { Document } from '../types';
import { FileUpload } from '../components/FileUpload';

export const Dashboard: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchDocs = async () => {
    try {
      const data = await getDocuments();
      setDocuments(data);
    } catch (err) {
      console.error('Failed to load documents:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const readyDocs = documents.filter((d) => d.status === 'ready');
  const processingDocs = documents.filter((d) => d.status === 'processing');
  const failedDocs = documents.filter((d) => d.status === 'failed');

  const features = [
    {
      title: 'AI Document Chat',
      desc: 'Ask questions, retrieve facts, and receive citation-backed answers from your documents.',
      path: '/chat',
      icon: MessageSquare,
      color: 'bg-blue-50 text-blue-600 border-blue-200',
    },
    {
      title: 'Summarization',
      desc: 'Generate executive summaries, key points, section-wise analysis, and structured takeaways.',
      path: '/summarize',
      icon: FileText,
      color: 'bg-indigo-50 text-indigo-600 border-indigo-200',
    },
    {
      title: 'Information Extraction',
      desc: 'Extract key entities, dates, metrics, and structured tables with CSV and JSON exports.',
      path: '/extract',
      icon: Table2,
      color: 'bg-emerald-50 text-emerald-600 border-emerald-200',
    },
    {
      title: 'Document Comparison',
      desc: 'Compare multiple documents side-by-side to detect contradictions, nuances, and commonalities.',
      path: '/compare',
      icon: GitCompare,
      color: 'bg-purple-50 text-purple-600 border-purple-200',
    },
    {
      title: 'Quiz Generator',
      desc: 'Create interactive multiple-choice, true/false, and short answer quizzes grounded in your files.',
      path: '/quiz',
      icon: Brain,
      color: 'bg-amber-50 text-amber-600 border-amber-200',
    },
    {
      title: 'Report Generator',
      desc: 'Synthesize research and analytical reports, edit sections, and export to PDF and DOCX.',
      path: '/reports',
      icon: FileOutput,
      color: 'bg-rose-50 text-rose-600 border-rose-200',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Hero Welcome Header */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-indigo-900 via-indigo-800 to-indigo-950 p-8 text-white shadow-md">
        <div className="relative z-10 max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-2 rounded-full bg-indigo-700/60 px-3 py-1 text-xs font-semibold text-indigo-200 border border-indigo-500/30">
            <Sparkles className="w-3.5 h-3.5 text-indigo-300" />
            Document Intelligence Platform
          </div>
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Welcome to DocuMind AI
          </h1>
          <p className="text-indigo-200 text-sm sm:text-base leading-relaxed">
            Upload PDFs, DOCX files, TXTs, or CSVs. Leverage grounded semantic retrieval,
            instant summarization, structured extraction, cross-document comparison, quizzes, and formatted reports.
          </p>
        </div>
      </div>

      {/* Metrics Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-xs">
          <div className="flex items-center justify-between text-gray-500 text-xs font-medium">
            <span>Total Documents</span>
            <FolderOpen className="w-4 h-4 text-gray-400" />
          </div>
          <p className="text-2xl font-bold text-gray-900 mt-2">{documents.length}</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-xs">
          <div className="flex items-center justify-between text-emerald-600 text-xs font-medium">
            <span>Ready / Indexed</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          </div>
          <p className="text-2xl font-bold text-gray-900 mt-2">{readyDocs.length}</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-xs">
          <div className="flex items-center justify-between text-blue-600 text-xs font-medium">
            <span>Processing</span>
            <Clock className="w-4 h-4 text-blue-500" />
          </div>
          <p className="text-2xl font-bold text-gray-900 mt-2">{processingDocs.length}</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-xs">
          <div className="flex items-center justify-between text-red-600 text-xs font-medium">
            <span>Failed</span>
            <AlertTriangle className="w-4 h-4 text-red-500" />
          </div>
          <p className="text-2xl font-bold text-gray-900 mt-2">{failedDocs.length}</p>
        </div>
      </div>

      {/* Core Features Grid */}
      <div className="space-y-4">
        <h2 className="text-lg font-bold text-gray-900">Core Capabilities</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map((feat) => {
            const Icon = feat.icon;
            return (
              <Link
                key={feat.path}
                to={feat.path}
                className="group relative bg-white p-6 rounded-xl border border-gray-200/90 shadow-xs hover:shadow-md hover:border-indigo-300 transition-all duration-200 flex flex-col justify-between"
              >
                <div>
                  <div className={`w-11 h-11 rounded-lg flex items-center justify-center border mb-4 ${feat.color}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <h3 className="text-base font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors">
                    {feat.title}
                  </h3>
                  <p className="text-xs text-gray-500 mt-1.5 leading-relaxed">
                    {feat.desc}
                  </p>
                </div>
                <div className="mt-5 flex items-center gap-1.5 text-xs font-semibold text-indigo-600 group-hover:translate-x-0.5 transition-transform">
                  <span>Open Workspace</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Quick Upload and Recent Documents */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 bg-white p-6 rounded-xl border border-gray-200 shadow-xs space-y-4">
          <div className="flex items-center gap-2">
            <Upload className="w-4 h-4 text-indigo-600" />
            <h3 className="text-base font-semibold text-gray-900">Quick Upload</h3>
          </div>
          <FileUpload onUploadSuccess={fetchDocs} />
        </div>

        <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-gray-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FolderOpen className="w-4 h-4 text-indigo-600" />
              <h3 className="text-base font-semibold text-gray-900">Recent Documents</h3>
            </div>
            <Link to="/documents" className="text-xs font-medium text-indigo-600 hover:text-indigo-700">
              View All ({documents.length})
            </Link>
          </div>

          {loading ? (
            <div className="py-8 text-center text-sm text-gray-400">Loading documents...</div>
          ) : documents.length === 0 ? (
            <div className="py-8 text-center text-sm text-gray-500 border border-dashed rounded-lg">
              No documents uploaded yet. Upload your first PDF, DOCX, TXT, or CSV file above!
            </div>
          ) : (
            <div className="divide-y divide-gray-100">
              {documents.slice(0, 5).map((doc) => (
                <div key={doc.id} className="py-3 flex items-center justify-between text-sm">
                  <div className="truncate mr-4">
                    <p className="font-medium text-gray-900 truncate">{doc.original_filename}</p>
                    <p className="text-xs text-gray-400">
                      {(doc.file_size / 1024).toFixed(1)} KB &bull; {doc.file_type.toUpperCase()}
                      {doc.chunk_count > 0 && ` &bull; ${doc.chunk_count} chunks`}
                    </p>
                  </div>
                  <div>
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                        doc.status === 'ready'
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : doc.status === 'processing'
                          ? 'bg-blue-50 text-blue-700 border border-blue-200 animate-pulse'
                          : 'bg-red-50 text-red-700 border border-red-200'
                      }`}
                    >
                      {doc.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
