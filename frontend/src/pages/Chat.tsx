import React, { useState, useEffect, useRef } from 'react';
import { useDocuments } from '../hooks/useDocuments';
import {
  createConversation,
  getConversations,
  getConversation,
  sendMessage,
  deleteConversation,
} from '../api/client';
import type { Conversation, Message } from '../types';
import { DocumentSelector } from '../components/DocumentSelector';
import { MarkdownRenderer } from '../components/MarkdownRenderer';
import { LoadingSpinner } from '../components/LoadingSpinner';
import {
  MessageSquare,
  Send,
  Plus,
  Trash2,
  FileText,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Bot,
  User,
} from 'lucide-react';

export const Chat: React.FC = () => {
  const { documents } = useDocuments();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const [currentConv, setCurrentConv] = useState<Conversation | null>(null);
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [convLoading, setConvLoading] = useState(false);
  const [expandedCitation, setExpandedCitation] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const fetchConversations = async () => {
    try {
      const data = await getConversations();
      setConversations(data);
      if (data.length > 0 && !activeConvId) {
        setActiveConvId(data[0].id);
      }
    } catch (err) {
      console.error('Failed to load conversations:', err);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    if (!activeConvId) {
      setCurrentConv(null);
      return;
    }
    const loadConversation = async () => {
      setConvLoading(true);
      try {
        const conv = await getConversation(activeConvId);
        setCurrentConv(conv);
      } catch (err) {
        console.error('Failed to load conversation details:', err);
      } finally {
        setConvLoading(false);
      }
    };
    loadConversation();
  }, [activeConvId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentConv?.messages, loading]);

  const handleCreateNewChat = async () => {
    if (selectedDocIds.length === 0) {
      alert('Please select at least one document to start a chat.');
      return;
    }
    try {
      const newConv = await createConversation(selectedDocIds);
      setConversations([newConv, ...conversations]);
      setActiveConvId(newConv.id);
      setCurrentConv(newConv);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Failed to create conversation');
    }
  };

  const handleDeleteConv = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Delete this conversation?')) {
      try {
        await deleteConversation(id);
        const updated = conversations.filter((c) => c.id !== id);
        setConversations(updated);
        if (activeConvId === id) {
          setActiveConvId(updated.length > 0 ? updated[0].id : null);
        }
      } catch (err) {
        console.error('Failed to delete conversation:', err);
      }
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || !activeConvId || loading) return;

    const userText = inputMessage;
    setInputMessage('');
    setLoading(true);

    // Optimistic UI update for user message
    const tempUserMsg: Message = {
      id: 'temp-' + Date.now(),
      conversation_id: activeConvId,
      role: 'user',
      content: userText,
      created_at: new Date().toISOString(),
    };

    if (currentConv) {
      setCurrentConv({
        ...currentConv,
        messages: [...(currentConv.messages || []), tempUserMsg],
      });
    }

    try {
      const assistantMsg = await sendMessage(activeConvId, userText);
      if (currentConv) {
        setCurrentConv({
          ...currentConv,
          messages: [...(currentConv.messages || []), assistantMsg],
        });
      }
      fetchConversations();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-[calc(100vh-6rem)] flex flex-col md:flex-row gap-6">
      {/* Sidebar: Conversation history & New chat */}
      <div className="w-full md:w-80 flex flex-col bg-white rounded-xl border border-gray-200 shadow-xs overflow-hidden shrink-0">
        <div className="p-4 border-b border-gray-100 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold text-gray-900 text-sm flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-indigo-600" />
              Conversations
            </h2>
          </div>
          <DocumentSelector
            multiple={true}
            documents={documents}
            value={selectedDocIds}
            onChange={setSelectedDocIds}
            label="Chat Documents"
          />
          <button
            onClick={handleCreateNewChat}
            disabled={selectedDocIds.length === 0}
            className="w-full flex items-center justify-center gap-2 py-2 px-3 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-200 disabled:text-gray-400 text-white rounded-lg text-sm font-medium transition-colors cursor-pointer shadow-xs"
          >
            <Plus className="w-4 h-4" />
            Start New Chat
          </button>
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto divide-y divide-gray-50 p-2">
          {conversations.length === 0 ? (
            <div className="p-4 text-center text-xs text-gray-400">
              No conversations yet. Select documents above and start a chat!
            </div>
          ) : (
            conversations.map((conv) => {
              const isActive = conv.id === activeConvId;
              return (
                <div
                  key={conv.id}
                  onClick={() => setActiveConvId(conv.id)}
                  className={`group flex items-center justify-between p-3 rounded-lg cursor-pointer text-sm transition-colors ${
                    isActive
                      ? 'bg-indigo-50/80 text-indigo-900 font-medium'
                      : 'hover:bg-gray-50 text-gray-700'
                  }`}
                >
                  <div className="truncate mr-2">
                    <p className="truncate text-xs font-semibold">{conv.title || 'Conversation'}</p>
                    <p className="text-[11px] text-gray-400 mt-0.5">
                      {new Date(conv.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <button
                    onClick={(e) => handleDeleteConv(conv.id, e)}
                    className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-red-500 rounded transition-opacity"
                    title="Delete conversation"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Main Chat Workspace */}
      <div className="flex-1 flex flex-col bg-white rounded-xl border border-gray-200 shadow-xs overflow-hidden">
        {activeConvId && currentConv ? (
          <>
            {/* Header */}
            <div className="px-6 py-3.5 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                <h3 className="font-semibold text-gray-900 text-sm">{currentConv.title || 'Document Chat'}</h3>
              </div>
              <span className="text-xs text-gray-500">
                {currentConv.document_ids?.length || 0} document(s) in context
              </span>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {convLoading ? (
                <div className="py-12 flex justify-center">
                  <LoadingSpinner size="md" />
                </div>
              ) : !currentConv.messages || currentConv.messages.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center p-8 text-gray-400">
                  <div className="w-12 h-12 rounded-2xl bg-indigo-50 flex items-center justify-center text-indigo-600 mb-3">
                    <Sparkles className="w-6 h-6" />
                  </div>
                  <h4 className="text-base font-semibold text-gray-800">Ask anything about your documents</h4>
                  <p className="text-xs text-gray-500 max-w-sm mt-1">
                    DocuMind retrieves relevant passages and computes calculations directly from your uploaded content.
                  </p>
                </div>
              ) : (
                currentConv.messages.map((msg) => {
                  const isUser = msg.role === 'user';
                  return (
                    <div
                      key={msg.id}
                      className={`flex gap-3 max-w-3xl ${isUser ? 'ml-auto flex-row-reverse' : ''}`}
                    >
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-xs ${
                          isUser
                            ? 'bg-indigo-600 text-white'
                            : 'bg-emerald-600 text-white shadow-xs'
                        }`}
                      >
                        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                      </div>

                      <div
                        className={`rounded-2xl px-4 py-3 text-sm shadow-xs ${
                          isUser
                            ? 'bg-indigo-600 text-white'
                            : 'bg-gray-50 border border-gray-200/80 text-gray-800'
                        }`}
                      >
                        {isUser ? (
                          <p className="whitespace-pre-wrap">{msg.content}</p>
                        ) : (
                          <div className="space-y-3">
                            <MarkdownRenderer content={msg.content} />

                            {/* Grounded Citations */}
                            {msg.citations && msg.citations.length > 0 && (
                              <div className="pt-3 mt-3 border-t border-gray-200/70">
                                <p className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-2">
                                  Grounding Sources & Citations
                                </p>
                                <div className="space-y-1.5">
                                  {msg.citations.map((cite, cIdx) => {
                                    const citeKey = `${msg.id}-${cIdx}`;
                                    const isExpanded = expandedCitation === citeKey;
                                    return (
                                      <div
                                        key={cIdx}
                                        className="rounded-md border border-gray-200 bg-white p-2 text-xs"
                                      >
                                        <button
                                          type="button"
                                          onClick={() =>
                                            setExpandedCitation(isExpanded ? null : citeKey)
                                          }
                                          className="w-full flex items-center justify-between text-left font-medium text-indigo-700 hover:text-indigo-900 cursor-pointer"
                                        >
                                          <div className="flex items-center gap-1.5 truncate mr-2">
                                            <FileText className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
                                            <span className="truncate">{cite.filename}</span>
                                            {cite.page && (
                                              <span className="text-gray-400 font-normal">
                                                (Page {cite.page})
                                              </span>
                                            )}
                                          </div>
                                          {isExpanded ? (
                                            <ChevronUp className="w-3.5 h-3.5 shrink-0" />
                                          ) : (
                                            <ChevronDown className="w-3.5 h-3.5 shrink-0" />
                                          )}
                                        </button>
                                        {isExpanded && (
                                          <p className="mt-2 text-gray-600 text-[11px] bg-gray-50 p-2 rounded border border-gray-100 font-mono leading-relaxed">
                                            "{cite.chunk_text}"
                                          </p>
                                        )}
                                      </div>
                                    );
                                  })}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })
              )}

              {loading && (
                <div className="flex gap-3 items-center text-sm text-gray-500">
                  <div className="w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center shrink-0">
                    <Bot className="w-4 h-4" />
                  </div>
                  <div className="bg-gray-50 border border-gray-200 rounded-2xl px-4 py-2.5 flex items-center gap-2">
                    <LoadingSpinner size="sm" />
                    <span>Analyzing documents & generating response...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Chat Input Bar */}
            <form onSubmit={handleSendMessage} className="p-4 border-t border-gray-100 bg-white">
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Ask a question about the document(s)..."
                  className="flex-1 px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
                  disabled={loading}
                />
                <button
                  type="submit"
                  disabled={!inputMessage.trim() || loading}
                  className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-200 disabled:text-gray-400 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 cursor-pointer shadow-xs"
                >
                  <Send className="w-4 h-4" />
                  <span>Send</span>
                </button>
              </div>
            </form>
          </>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-center p-8 text-gray-400">
            <MessageSquare className="w-12 h-12 text-gray-300 mb-3" />
            <h3 className="text-base font-semibold text-gray-700">Select or Start a Conversation</h3>
            <p className="text-xs text-gray-500 max-w-sm mt-1">
              Pick one or more documents from the left panel and click "Start New Chat" to begin exploring your documents.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
