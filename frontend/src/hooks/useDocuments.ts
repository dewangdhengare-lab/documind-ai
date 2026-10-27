import { useState, useEffect, useCallback } from 'react';
import type { Document } from '../types';
import { getDocuments } from '../api/client';

export function useDocuments(pollWhileProcessing = true) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = useCallback(async () => {
    try {
      const docs = await getDocuments();
      setDocuments(docs);
      setError(null);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : 'Failed to fetch documents';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  // Poll every 3 seconds while any document is processing
  useEffect(() => {
    if (!pollWhileProcessing) return;
    const hasProcessing = documents.some(
      (d) => d.status === 'processing' || d.status === 'uploading'
    );
    if (!hasProcessing) return;

    const interval = setInterval(fetchDocuments, 3000);
    return () => clearInterval(interval);
  }, [documents, pollWhileProcessing, fetchDocuments]);

  const readyDocuments = documents.filter((d) => d.status === 'ready');

  return { documents, readyDocuments, loading, error, refetch: fetchDocuments };
}
