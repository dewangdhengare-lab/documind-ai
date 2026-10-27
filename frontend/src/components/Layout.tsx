import React, { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Key } from 'lucide-react';
import axios from 'axios';

export const Layout: React.FC = () => {
  const [groqConfigured, setGroqConfigured] = useState<boolean | null>(null);

  useEffect(() => {
    axios
      .get('/api/health')
      .then((res) => {
        setGroqConfigured(Boolean(res.data?.groq_configured));
      })
      .catch(() => {
        setGroqConfigured(null);
      });
  }, []);

  return (
    <div className="flex min-h-screen bg-gray-50 text-gray-900">
      <Sidebar />
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {groqConfigured === false && (
          <div className="bg-amber-50 border-b border-amber-200 px-6 py-2.5 flex items-center justify-between text-xs text-amber-800">
            <div className="flex items-center gap-2">
              <Key className="w-4 h-4 text-amber-600 shrink-0" />
              <span>
                <strong>Groq API Key Required for AI Features:</strong> Ingestion and vector search work locally, but AI Chat, Summaries, Extractions, Comparisons, Quizzes, and Reports require a free API key in{' '}
                <code className="bg-amber-100 px-1 py-0.5 rounded text-amber-900 font-mono">
                  backend/.env
                </code>
                .
              </span>
            </div>
            <a
              href="https://console.groq.com/keys"
              target="_blank"
              rel="noreferrer"
              className="font-semibold text-indigo-700 hover:text-indigo-900 underline shrink-0 ml-4"
            >
              Get Free Key &rarr;
            </a>
          </div>
        )}
        <div className="flex-1 p-6 md:p-8 max-w-7xl mx-auto w-full">
          <Outlet />
        </div>
      </main>
    </div>
  );
};
