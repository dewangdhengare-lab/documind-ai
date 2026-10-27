import axios from 'axios';
import type {
  Document,
  Conversation,
  Message,
  Summary,
  Extraction,
  Comparison,
  Quiz,
  QuizAttempt,
  Report,
} from '../types';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: { 'Content-Type': 'application/json' },
});

// ── Documents ──────────────────────────────────────────────
export const uploadDocument = async (file: File): Promise<Document> => {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post<Document>('/documents', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
};

export const getDocuments = async (): Promise<Document[]> => {
  const { data } = await api.get<Document[]>('/documents');
  return data;
};

export const getDocument = async (id: string): Promise<Document> => {
  const { data } = await api.get<Document>(`/documents/${id}`);
  return data;
};

export const deleteDocument = async (id: string): Promise<void> => {
  await api.delete(`/documents/${id}`);
};

export const retryDocument = async (id: string): Promise<Document> => {
  const { data } = await api.post<Document>(`/documents/${id}/retry`);
  return data;
};

// ── Conversations ──────────────────────────────────────────
export const createConversation = async (
  documentIds: string[]
): Promise<Conversation> => {
  const { data } = await api.post<Conversation>('/conversations', {
    document_ids: documentIds,
  });
  return data;
};

export const getConversations = async (): Promise<Conversation[]> => {
  const { data } = await api.get<Conversation[]>('/conversations');
  return data;
};

export const getConversation = async (id: string): Promise<Conversation> => {
  const { data } = await api.get<Conversation>(`/conversations/${id}`);
  return data;
};

export const sendMessage = async (
  conversationId: string,
  content: string
): Promise<Message> => {
  const { data } = await api.post<Message>(
    `/conversations/${conversationId}/messages`,
    { content }
  );
  return data;
};

export const deleteConversation = async (id: string): Promise<void> => {
  await api.delete(`/conversations/${id}`);
};

// ── Summaries ──────────────────────────────────────────────
export const summarize = async (
  documentId: string,
  summaryType: string
): Promise<Summary> => {
  const { data } = await api.post<Summary>('/summaries', {
    document_id: documentId,
    summary_type: summaryType,
  });
  return data;
};

export const getSummaries = async (): Promise<Summary[]> => {
  const { data } = await api.get<Summary[]>('/summaries');
  return data;
};

export const getSummary = async (id: string): Promise<Summary> => {
  const { data } = await api.get<Summary>(`/summaries/${id}`);
  return data;
};

export const deleteSummary = async (id: string): Promise<void> => {
  await api.delete(`/summaries/${id}`);
};

// ── Extractions ────────────────────────────────────────────
export const extract = async (
  documentId: string,
  instruction: string,
  fields?: string[]
): Promise<Extraction> => {
  const { data } = await api.post<Extraction>('/extractions', {
    document_id: documentId,
    instruction,
    fields,
  });
  return data;
};

export const getExtractions = async (): Promise<Extraction[]> => {
  const { data } = await api.get<Extraction[]>('/extractions');
  return data;
};

export const getExtraction = async (id: string): Promise<Extraction> => {
  const { data } = await api.get<Extraction>(`/extractions/${id}`);
  return data;
};

export const deleteExtraction = async (id: string): Promise<void> => {
  await api.delete(`/extractions/${id}`);
};

export const exportExtraction = async (
  id: string,
  format: 'csv' | 'json'
): Promise<Blob> => {
  const { data } = await api.get(`/extractions/${id}/export`, {
    params: { format },
    responseType: 'blob',
  });
  return data;
};

// ── Comparisons ────────────────────────────────────────────
export const compare = async (documentIds: string[]): Promise<Comparison> => {
  const { data } = await api.post<Comparison>('/comparisons', {
    document_ids: documentIds,
  });
  return data;
};

export const getComparisons = async (): Promise<Comparison[]> => {
  const { data } = await api.get<Comparison[]>('/comparisons');
  return data;
};

export const getComparison = async (id: string): Promise<Comparison> => {
  const { data } = await api.get<Comparison>(`/comparisons/${id}`);
  return data;
};

export const deleteComparison = async (id: string): Promise<void> => {
  await api.delete(`/comparisons/${id}`);
};

// ── Quizzes ────────────────────────────────────────────────
export const generateQuiz = async (
  documentId: string,
  config: {
    num_questions: number;
    difficulty: string;
    question_types: string[];
  }
): Promise<Quiz> => {
  const { data } = await api.post<Quiz>('/quizzes', {
    document_id: documentId,
    ...config,
  });
  return data;
};

export const getQuizzes = async (): Promise<Quiz[]> => {
  const { data } = await api.get<Quiz[]>('/quizzes');
  return data;
};

export const getQuiz = async (id: string): Promise<Quiz> => {
  const { data } = await api.get<Quiz>(`/quizzes/${id}`);
  return data;
};

export const submitQuiz = async (
  quizId: string,
  answers: Record<number, string>
): Promise<QuizAttempt> => {
  const { data } = await api.post<QuizAttempt>(`/quizzes/${quizId}/attempts`, {
    answers,
  });
  return data;
};

export const getQuizAttempts = async (
  quizId: string
): Promise<QuizAttempt[]> => {
  const { data } = await api.get<QuizAttempt[]>(
    `/quizzes/${quizId}/attempts`
  );
  return data;
};

export const deleteQuiz = async (id: string): Promise<void> => {
  await api.delete(`/quizzes/${id}`);
};

// ── Reports ────────────────────────────────────────────────
export const generateReport = async (
  documentIds: string[],
  reportType: string,
  config: {
    title: string;
    purpose: string;
    audience: string;
    sections: string[];
    detail_level: string;
  }
): Promise<Report> => {
  const { data } = await api.post<Report>('/reports', {
    document_ids: documentIds,
    report_type: reportType,
    ...config,
  });
  return data;
};

export const getReports = async (): Promise<Report[]> => {
  const { data } = await api.get<Report[]>('/reports');
  return data;
};

export const getReport = async (id: string): Promise<Report> => {
  const { data } = await api.get<Report>(`/reports/${id}`);
  return data;
};

export const updateReport = async (
  id: string,
  content: string
): Promise<Report> => {
  const { data } = await api.put<Report>(`/reports/${id}`, { content });
  return data;
};

export const deleteReport = async (id: string): Promise<void> => {
  await api.delete(`/reports/${id}`);
};

export const exportReport = async (
  id: string,
  format: 'pdf' | 'docx'
): Promise<Blob> => {
  const { data } = await api.get(`/reports/${id}/export`, {
    params: { format },
    responseType: 'blob',
  });
  return data;
};
