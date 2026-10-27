import React from 'react';
import type { Document } from '../types';
import { FileText, Check, AlertCircle } from 'lucide-react';

interface SingleSelectProps {
  multiple?: false;
  value: string;
  onChange: (id: string) => void;
  documents: Document[];
  label?: string;
  required?: boolean;
}

interface MultiSelectProps {
  multiple: true;
  value: string[];
  onChange: (ids: string[]) => void;
  documents: Document[];
  label?: string;
  required?: boolean;
}

export type DocumentSelectorProps = SingleSelectProps | MultiSelectProps;

export const DocumentSelector: React.FC<DocumentSelectorProps> = (props) => {
  const { documents, label = 'Select Document' } = props;
  const readyDocs = documents.filter((d) => d.status === 'ready');

  if (readyDocs.length === 0) {
    return (
      <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800 flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
        <div>
          <p className="font-semibold">No ready documents available</p>
          <p className="text-xs text-amber-700 mt-0.5">
            Please upload documents in the Document Library and wait until processing completes.
          </p>
        </div>
      </div>
    );
  }

  if (props.multiple) {
    const { value: selectedIds, onChange } = props;
    const toggleId = (id: string) => {
      if (selectedIds.includes(id)) {
        onChange(selectedIds.filter((item) => item !== id));
      } else {
        onChange([...selectedIds, id]);
      }
    };

    return (
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          {label} <span className="text-xs text-gray-500">({selectedIds.length} selected)</span>
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-56 overflow-y-auto p-1 border border-gray-200 rounded-lg bg-white">
          {readyDocs.map((doc) => {
            const isSelected = selectedIds.includes(doc.id);
            return (
              <button
                type="button"
                key={doc.id}
                onClick={() => toggleId(doc.id)}
                className={`flex items-center justify-between p-2.5 rounded-md text-left text-sm border transition-all cursor-pointer ${
                  isSelected
                    ? 'border-indigo-600 bg-indigo-50/70 text-indigo-900 font-medium'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50 text-gray-700'
                }`}
              >
                <div className="flex items-center gap-2 truncate mr-2">
                  <FileText className={`w-4 h-4 shrink-0 ${isSelected ? 'text-indigo-600' : 'text-gray-400'}`} />
                  <span className="truncate">{doc.original_filename}</span>
                </div>
                {isSelected && <Check className="w-4 h-4 text-indigo-600 shrink-0" />}
              </button>
            );
          })}
        </div>
      </div>
    );
  }

  // Single Select
  const { value, onChange } = props;
  return (
    <div className="space-y-1.5">
      <label className="block text-sm font-medium text-gray-700">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-3.5 py-2.5 bg-white border border-gray-300 rounded-lg text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 shadow-xs cursor-pointer"
      >
        <option value="">-- Choose a document --</option>
        {readyDocs.map((doc) => (
          <option key={doc.id} value={doc.id}>
            {doc.original_filename} ({doc.file_type.toUpperCase()})
          </option>
        ))}
      </select>
    </div>
  );
};

export default DocumentSelector;
