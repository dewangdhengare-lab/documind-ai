import React from 'react';
import { useDocuments } from '../hooks/useDocuments';
import { FileUpload } from '../components/FileUpload';
import DocumentList from '../components/DocumentList';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';
import { EmptyState } from '../components/EmptyState';
import { deleteDocument, retryDocument } from '../api/client';
import { FolderOpen } from 'lucide-react';

export const Documents: React.FC = () => {
  const { documents, loading, error, refetch } = useDocuments(true);

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this document and all related data?')) {
      try {
        await deleteDocument(id);
        refetch();
      } catch (err: unknown) {
        alert(err instanceof Error ? err.message : 'Failed to delete document');
      }
    }
  };

  const handleRetry = async (id: string) => {
    try {
      await retryDocument(id);
      refetch();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Failed to retry processing');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Document Library</h1>
        <p className="text-sm text-gray-500 mt-1">
          Upload and manage your documents. Supported formats: PDF, DOCX, TXT, and CSV (up to 50MB).
        </p>
      </div>

      {/* Upload Zone */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-xs">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Upload New Document</h2>
        <FileUpload onUploadSuccess={refetch} />
      </div>

      {/* Document Listing */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-gray-900">
            Uploaded Documents ({documents.length})
          </h2>
          <button
            onClick={() => refetch()}
            className="text-xs font-medium text-indigo-600 hover:text-indigo-700 cursor-pointer"
          >
            Refresh List
          </button>
        </div>

        {loading ? (
          <div className="py-12 flex justify-center">
            <LoadingSpinner size="lg" />
          </div>
        ) : error ? (
          <ErrorMessage message={error} onRetry={refetch} />
        ) : documents.length === 0 ? (
          <EmptyState
            icon={FolderOpen}
            title="No documents yet"
            description="Drag and drop or select files above to begin ingesting documents into DocuMind AI."
          />
        ) : (
          <DocumentList
            documents={documents}
            onDelete={handleDelete}
            onRetry={handleRetry}
          />
        )}
      </div>
    </div>
  );
};
