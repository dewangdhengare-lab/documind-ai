export interface Document {
  id: string;
  filename: string;
  original_filename: string;
  file_type: string;
  file_size: number;
  status: 'uploading' | 'processing' | 'ready' | 'failed';
  error_message?: string;
  page_count?: number;
  chunk_count: number;
  created_at: string;
  updated_at: string;
}

export interface Conversation {
  id: string;
  title?: string;
  document_ids: string[];
  created_at: string;
  updated_at: string;
  messages?: Message[];
}

export interface Citation {
  filename: string;
  page?: number;
  chunk_text: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  created_at: string;
}

export interface Summary {
  id: string;
  document_id: string;
  summary_type: string;
  content: string;
  created_at: string;
}

export interface Extraction {
  id: string;
  document_id: string;
  instruction: string;
  result: Record<string, unknown>;
  created_at: string;
}

export interface Comparison {
  id: string;
  document_ids: string[];
  result: {
    similarities: string[];
    differences: string[];
    contradictions: string[];
    conclusion: string;
    details: Array<{
      aspect: string;
      doc1: string;
      doc2: string;
    }>;
  };
  created_at: string;
}

export interface QuizQuestion {
  id: number;
  question: string;
  type: 'multiple_choice' | 'true_false' | 'short_answer';
  options?: string[];
  correct_answer: string;
  explanation: string;
}

export interface Quiz {
  id: string;
  document_id: string;
  config: {
    num_questions: number;
    difficulty: string;
    question_types: string[];
  };
  questions: QuizQuestion[];
  created_at: string;
}

export interface QuizAttempt {
  id: string;
  quiz_id: string;
  answers: Record<string, string>;
  score: number;
  total: number;
  created_at: string;
  results?: Array<{
    question_id: number;
    question: string;
    user_answer: string;
    correct_answer: string;
    is_correct: boolean;
    explanation: string;
  }>;
}

export interface Report {
  id: string;
  document_ids: string[];
  report_type: string;
  config: {
    title: string;
    purpose: string;
    audience: string;
    sections: string[];
    detail_level: string;
  };
  content: string;
  created_at: string;
  updated_at: string;
}
