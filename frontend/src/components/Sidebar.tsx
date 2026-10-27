import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FolderOpen,
  MessageSquare,
  FileText,
  Table2,
  GitCompare,
  Brain,
  FileOutput,
  Sparkles,
} from 'lucide-react';

interface NavItem {
  name: string;
  path: string;
  icon: React.ComponentType<{ className?: string }>;
}

const navItems: NavItem[] = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Document Library', path: '/documents', icon: FolderOpen },
  { name: 'AI Document Chat', path: '/chat', icon: MessageSquare },
  { name: 'Summarization', path: '/summarize', icon: FileText },
  { name: 'Information Extraction', path: '/extract', icon: Table2 },
  { name: 'Document Comparison', path: '/compare', icon: GitCompare },
  { name: 'Quiz Generator', path: '/quiz', icon: Brain },
  { name: 'Report Generator', path: '/reports', icon: FileOutput },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col h-screen sticky top-0 shadow-xs z-20">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-gray-100 gap-3">
        <div className="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-sm shadow-indigo-200">
          <Brain className="w-5 h-5" />
        </div>
        <div>
          <span className="font-bold text-gray-900 text-lg tracking-tight">DocuMind</span>
          <span className="text-xs font-semibold text-indigo-600 ml-1.5 px-1.5 py-0.5 bg-indigo-50 rounded-full border border-indigo-100">
            AI
          </span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-gray-400">
          Core Workspaces
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-indigo-50 text-indigo-700 font-semibold shadow-xs'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span className="truncate">{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-gray-100 bg-gray-50/50">
        <div className="flex items-center gap-2.5 px-3 py-2 rounded-lg bg-indigo-50/80 border border-indigo-100/60">
          <Sparkles className="w-4 h-4 text-indigo-600 shrink-0" />
          <div className="text-xs text-indigo-900">
            <p className="font-medium">RAG Document Intelligence</p>
            <p className="text-[11px] text-indigo-600/80">Groq & ChromaDB Powered</p>
          </div>
        </div>
      </div>
    </aside>
  );
};
