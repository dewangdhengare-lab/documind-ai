import { useCallback, useState, useRef } from 'react';
import { Upload, X, FileText, CheckCircle2, AlertCircle } from 'lucide-react';
import { uploadDocument } from '../api/client';
import type { Document } from '../types';

interface UploadItem {
  file: File;
  progress: 'pending' | 'uploading' | 'done' | 'error';
  error?: string;
  doc?: Document;
}

interface Props {
  onUploaded?: (doc: Document) => void;
  onUploadSuccess?: () => void;
  compact?: boolean;
  className?: string;
}

const ACCEPTED = '.pdf,.docx,.txt,.csv';

export function FileUpload({ onUploaded, onUploadSuccess, compact, className = '' }: Props) {
  const [items, setItems] = useState<UploadItem[]>([]);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFiles = useCallback(
    async (files: FileList | File[]) => {
      const fileArr = Array.from(files);
      const newItems: UploadItem[] = fileArr.map((f) => ({
        file: f,
        progress: 'pending' as const,
      }));
      setItems((prev) => [...prev, ...newItems]);

      for (let i = 0; i < fileArr.length; i++) {
        const file = fileArr[i];
        setItems((prev) =>
          prev.map((it) =>
            it.file === file ? { ...it, progress: 'uploading' as const } : it
          )
        );
        try {
          const doc = await uploadDocument(file);
          setItems((prev) =>
            prev.map((it) =>
              it.file === file
                ? { ...it, progress: 'done' as const, doc }
                : it
            )
          );
          onUploaded?.(doc);
          onUploadSuccess?.();
        } catch (err: unknown) {
          const msg =
            err instanceof Error ? err.message : 'Upload failed';
          setItems((prev) =>
            prev.map((it) =>
              it.file === file
                ? { ...it, progress: 'error' as const, error: msg }
                : it
            )
          );
        }
      }
    },
    [onUploaded, onUploadSuccess]
  );

  const removeItem = (idx: number) => {
    setItems((prev) => prev.filter((_, i) => i !== idx));
  };

  return (
    <div className={`space-y-4 ${className}`}>
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          if (e.dataTransfer.files?.length) {
            handleFiles(e.dataTransfer.files);
          }
        }}
        onClick={() => inputRef.current?.click()}
        className={`flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-6 text-center transition-colors cursor-pointer ${
          dragOver
            ? 'border-indigo-500 bg-indigo-50/50'
            : 'border-gray-300 hover:border-gray-400 bg-gray-50/50'
        } ${compact ? 'py-4' : 'py-8'}`}
      >
        <Upload className="mb-2 text-indigo-500" size={compact ? 24 : 32} />
        <p className="text-sm font-medium text-gray-700">
          <span className="text-indigo-600 hover:underline">Click to upload</span> or drag and drop
        </p>
        <p className="mt-1 text-xs text-gray-500">PDF, DOCX, TXT, or CSV (max 50 MB)</p>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED}
          multiple
          className="hidden"
          onChange={(e) => {
            if (e.target.files?.length) {
              handleFiles(e.target.files);
              e.target.value = '';
            }
          }}
        />
      </div>

      {items.length > 0 && (
        <ul className="divide-y divide-gray-100 rounded-lg border border-gray-200 bg-white">
          {items.map((it, idx) => (
            <li
              key={idx}
              className="flex items-center justify-between px-4 py-2.5 text-sm"
            >
              <div className="flex items-center gap-2 truncate">
                <FileText size={16} className="shrink-0 text-gray-400" />
                <span className="truncate text-gray-700">{it.file.name}</span>
              </div>
              <div className="flex items-center gap-2">
                {it.progress === 'uploading' && (
                  <span className="text-xs text-indigo-600">Uploading...</span>
                )}
                {it.progress === 'done' && (
                  <CheckCircle2 size={16} className="text-emerald-500" />
                )}
                {it.progress === 'error' && (
                  <span className="flex items-center gap-1 text-xs text-red-500" title={it.error}>
                    <AlertCircle size={14} /> Failed
                  </span>
                )}
                <button
                  type="button"
                  onClick={() => removeItem(idx)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X size={14} />
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default FileUpload;
