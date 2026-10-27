import {
  FileText,
  FileSpreadsheet,
  File,
  Trash2,
  RotateCcw,
} from 'lucide-react';
import type { Document } from '../types';

interface Props {
  documents: Document[];
  onDelete: (id: string) => void;
  onRetry: (id: string) => void;
  className?: string;
}

const statusConfig: Record<
  Document['status'],
  { label: string; color: string }
> = {
  uploading: { label: 'Uploading', color: 'bg-gray-100 text-gray-600' },
  processing: { label: 'Processing', color: 'bg-blue-100 text-blue-700' },
  ready: { label: 'Ready', color: 'bg-emerald-100 text-emerald-700' },
  failed: { label: 'Failed', color: 'bg-red-100 text-red-700' },
};

function fileIcon(type: string) {
  const cleanType = (type || '').replace('.', '').toLowerCase();
  if (cleanType === 'pdf') return <FileText size={20} className="text-red-500" />;
  if (cleanType === 'csv') return <FileSpreadsheet size={20} className="text-emerald-500" />;
  if (cleanType === 'docx') return <FileText size={20} className="text-blue-500" />;
  return <File size={20} className="text-gray-400" />;
}

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1048576).toFixed(1)} MB`;
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export default function DocumentList({
  documents,
  onDelete,
  onRetry,
  className = '',
}: Props) {
  return (
    <div className={`overflow-hidden rounded-lg border border-gray-200 ${className}`}>
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
              Name
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
              Size
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
              Uploaded
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
              Status
            </th>
            <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100 bg-white">
          {documents.map((doc) => {
            const sc = statusConfig[doc.status];
            return (
              <tr key={doc.id} className="hover:bg-gray-50">
                <td className="whitespace-nowrap px-4 py-3">
                  <div className="flex items-center gap-2">
                    {fileIcon(doc.file_type)}
                    <span className="text-sm font-medium text-gray-900 truncate max-w-xs">
                      {doc.original_filename}
                    </span>
                  </div>
                </td>
                <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-500">
                  {formatSize(doc.file_size)}
                </td>
                <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-500">
                  {formatDate(doc.created_at)}
                </td>
                <td className="whitespace-nowrap px-4 py-3">
                  <span
                    className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${sc.color}`}
                  >
                    {sc.label}
                  </span>
                  {doc.error_message && (
                    <p
                      className="mt-1 text-xs text-red-600 max-w-xs break-words"
                      title={doc.error_message}
                    >
                      {doc.error_message}
                    </p>
                  )}
                </td>
                <td className="whitespace-nowrap px-4 py-3 text-right">
                  <div className="flex items-center justify-end gap-1">
                    {doc.status === 'failed' && (
                      <button
                        onClick={() => onRetry(doc.id)}
                        className="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-blue-600"
                        title="Retry"
                      >
                        <RotateCcw size={16} />
                      </button>
                    )}
                    <button
                      onClick={() => onDelete(doc.id)}
                      className="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-red-600"
                      title="Delete"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
