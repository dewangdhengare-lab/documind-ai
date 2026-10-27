import React, { useState, useEffect } from 'react';
import { useDocuments } from '../hooks/useDocuments';
import {
  generateQuiz,
  getQuizzes,
  submitQuiz,
  deleteQuiz,
} from '../api/client';
import type { Quiz, QuizAttempt } from '../types';
import { DocumentSelector } from '../components/DocumentSelector';
import { LoadingSpinner } from '../components/LoadingSpinner';
import {
  Brain,
  CheckCircle,
  XCircle,
  RotateCcw,
  Award,
  Trash2,
  Check,
} from 'lucide-react';

export const QuizPage: React.FC = () => {
  const { documents } = useDocuments();
  const [selectedDocId, setSelectedDocId] = useState('');
  const [numQuestions, setNumQuestions] = useState(5);
  const [difficulty, setDifficulty] = useState('medium');
  const [questionTypes, setQuestionTypes] = useState<string[]>([
    'multiple_choice',
    'true_false',
  ]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [activeQuiz, setActiveQuiz] = useState<Quiz | null>(null);
  const [userAnswers, setUserAnswers] = useState<Record<string, string>>({});
  const [quizResult, setQuizResult] = useState<QuizAttempt | null>(null);

  const fetchQuizzes = async () => {
    try {
      const data = await getQuizzes();
      setQuizzes(data);
      if (data.length > 0 && !activeQuiz) {
        setActiveQuiz(data[0]);
      }
    } catch (err) {
      console.error('Failed to load quizzes:', err);
    }
  };

  useEffect(() => {
    fetchQuizzes();
  }, []);

  const handleToggleType = (type: string) => {
    if (questionTypes.includes(type)) {
      if (questionTypes.length > 1) {
        setQuestionTypes(questionTypes.filter((t) => t !== type));
      }
    } else {
      setQuestionTypes([...questionTypes, type]);
    }
  };

  const handleGenerateQuiz = async () => {
    if (!selectedDocId) {
      alert('Please select a document.');
      return;
    }
    setLoading(true);
    setQuizResult(null);
    setUserAnswers({});
    try {
      const newQuiz = await generateQuiz(selectedDocId, {
        num_questions: numQuestions,
        difficulty,
        question_types: questionTypes,
      });
      setActiveQuiz(newQuiz);
      setQuizzes([newQuiz, ...quizzes]);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Quiz generation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (qId: number, answer: string) => {
    setUserAnswers({
      ...userAnswers,
      [String(qId)]: answer,
    });
  };

  const handleSubmitQuiz = async () => {
    if (!activeQuiz) return;
    setSubmitting(true);
    try {
      const attempt = await submitQuiz(activeQuiz.id, userAnswers as any);
      setQuizResult(attempt);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Failed to submit quiz');
    } finally {
      setSubmitting(false);
    }
  };

  const handleRetake = () => {
    setUserAnswers({});
    setQuizResult(null);
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Delete this quiz?')) {
      try {
        await deleteQuiz(id);
        const updated = quizzes.filter((q) => q.id !== id);
        setQuizzes(updated);
        if (activeQuiz?.id === id) {
          setActiveQuiz(updated.length > 0 ? updated[0] : null);
          setQuizResult(null);
        }
      } catch (err) {
        console.error('Failed to delete quiz:', err);
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Quiz Generator</h1>
        <p className="text-sm text-gray-500 mt-1">
          Generate interactive assessments from uploaded documents to test comprehension and retain core knowledge.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Setup Column */}
        <div className="lg:col-span-1 space-y-5">
          <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-xs space-y-4">
            <DocumentSelector
              multiple={false}
              documents={documents}
              value={selectedDocId}
              onChange={setSelectedDocId}
              label="Select Document"
            />

            <div>
              <div className="flex justify-between text-sm font-medium text-gray-700 mb-1.5">
                <span>Number of Questions</span>
                <span className="text-indigo-600 font-semibold">{numQuestions}</span>
              </div>
              <input
                type="range"
                min={3}
                max={15}
                value={numQuestions}
                onChange={(e) => setNumQuestions(Number(e.target.value))}
                className="w-full accent-indigo-600 cursor-pointer"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Difficulty</label>
              <div className="grid grid-cols-3 gap-2">
                {['easy', 'medium', 'hard'].map((lvl) => (
                  <button
                    key={lvl}
                    type="button"
                    onClick={() => setDifficulty(lvl)}
                    className={`py-2 text-xs font-semibold rounded-lg capitalize border cursor-pointer transition-all ${
                      difficulty === lvl
                        ? 'border-indigo-600 bg-indigo-50 text-indigo-700'
                        : 'border-gray-200 text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    {lvl}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Question Formats
              </label>
              <div className="space-y-2 text-xs">
                {[
                  { id: 'multiple_choice', label: 'Multiple Choice (4 options)' },
                  { id: 'true_false', label: 'True / False' },
                  { id: 'short_answer', label: 'Short Answer' },
                ].map((type) => {
                  const isChecked = questionTypes.includes(type.id);
                  return (
                    <label
                      key={type.id}
                      className="flex items-center gap-2 p-2 rounded-md hover:bg-gray-50 cursor-pointer text-gray-700"
                    >
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => handleToggleType(type.id)}
                        className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                      />
                      <span>{type.label}</span>
                    </label>
                  );
                })}
              </div>
            </div>

            <button
              onClick={handleGenerateQuiz}
              disabled={!selectedDocId || loading}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-200 disabled:text-gray-400 text-white rounded-lg text-sm font-medium transition-colors cursor-pointer shadow-xs"
            >
              {loading ? (
                <>
                  <LoadingSpinner size="sm" />
                  <span>Synthesizing Questions...</span>
                </>
              ) : (
                <>
                  <Brain className="w-4 h-4" />
                  <span>Generate Interactive Quiz</span>
                </>
              )}
            </button>
          </div>

          {/* Past Quizzes */}
          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-xs space-y-3">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Saved Quizzes ({quizzes.length})
            </h3>
            <div className="divide-y divide-gray-100 max-h-64 overflow-y-auto">
              {quizzes.length === 0 ? (
                <p className="text-xs text-gray-400 py-3 text-center">No quizzes generated yet.</p>
              ) : (
                quizzes.map((q) => {
                  const isSelected = activeQuiz?.id === q.id;
                  return (
                    <div
                      key={q.id}
                      onClick={() => {
                        setActiveQuiz(q);
                        setUserAnswers({});
                        setQuizResult(null);
                      }}
                      className={`group py-2.5 px-2 flex items-center justify-between text-xs rounded-md cursor-pointer transition-colors ${
                        isSelected ? 'bg-indigo-50 text-indigo-900 font-semibold' : 'hover:bg-gray-50 text-gray-700'
                      }`}
                    >
                      <div className="truncate mr-2">
                        <span className="font-medium">
                          {q.questions?.length || 5} Questions ({q.config?.difficulty || 'Quiz'})
                        </span>
                        <p className="text-[10px] text-gray-400">
                          {new Date(q.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <button
                        onClick={(e) => handleDelete(q.id, e)}
                        className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-red-500 transition-opacity"
                        title="Delete"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>

        {/* Quiz Interaction Column */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 shadow-xs flex flex-col min-h-[500px]">
          {activeQuiz && activeQuiz.questions && activeQuiz.questions.length > 0 ? (
            <div className="flex-1 flex flex-col">
              {/* Header */}
              <div className="p-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
                <div>
                  <h3 className="text-sm font-semibold text-gray-900">
                    Interactive Assessment ({activeQuiz.questions.length} Questions)
                  </h3>
                  <p className="text-xs text-gray-400 capitalize">
                    Difficulty: {activeQuiz.config?.difficulty || 'Medium'}
                  </p>
                </div>
                {quizResult && (
                  <button
                    onClick={handleRetake}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-md hover:bg-indigo-100 transition-colors cursor-pointer"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>Retake Quiz</span>
                  </button>
                )}
              </div>

              {/* Score Banner (when submitted) */}
              {quizResult && (
                <div className="p-6 bg-gradient-to-r from-indigo-50 to-purple-50 border-b border-indigo-100 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-indigo-600 text-white flex items-center justify-center shadow-md">
                      <Award className="w-6 h-6" />
                    </div>
                    <div>
                      <h4 className="text-lg font-bold text-indigo-950">
                        Score: {quizResult.score}%
                      </h4>
                      <p className="text-xs text-indigo-700 mt-0.5">
                        Answered {quizResult.results?.filter((r) => r.is_correct).length || 0} of{' '}
                        {quizResult.total || activeQuiz.questions.length} questions correctly.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Questions List */}
              <div className="flex-1 p-6 overflow-y-auto space-y-6">
                {activeQuiz.questions.map((q, idx) => {
                  const qKey = String(q.id);
                  const userAns = userAnswers[qKey] || '';
                  const resultDetail = quizResult?.results?.find(
                    (r) => String(r.question_id) === qKey
                  );

                  return (
                    <div
                      key={q.id || idx}
                      className={`p-5 rounded-xl border transition-all ${
                        resultDetail
                          ? resultDetail.is_correct
                            ? 'border-emerald-200 bg-emerald-50/20'
                            : 'border-red-200 bg-red-50/20'
                          : 'border-gray-200 bg-white'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3 mb-3">
                        <div className="flex items-start gap-2.5">
                          <span className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-xs font-bold shrink-0">
                            {idx + 1}
                          </span>
                          <p className="text-sm font-semibold text-gray-900 leading-relaxed">
                            {q.question}
                          </p>
                        </div>
                        {resultDetail && (
                          <div className="shrink-0">
                            {resultDetail.is_correct ? (
                              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
                                <CheckCircle className="w-3.5 h-3.5" /> Correct
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-100 text-red-800">
                                <XCircle className="w-3.5 h-3.5" /> Incorrect
                              </span>
                            )}
                          </div>
                        )}
                      </div>

                      {/* Multiple Choice Options */}
                      {q.type === 'multiple_choice' && q.options && (
                        <div className="space-y-2 mt-3 pl-8">
                          {q.options.map((opt, oIdx) => {
                            const isSelected = userAns === opt;
                            return (
                              <button
                                key={oIdx}
                                type="button"
                                disabled={Boolean(quizResult)}
                                onClick={() => handleAnswerChange(q.id, opt)}
                                className={`w-full flex items-center justify-between p-3 rounded-lg border text-left text-xs transition-all cursor-pointer ${
                                  isSelected
                                    ? 'border-indigo-600 bg-indigo-50/80 text-indigo-900 font-medium'
                                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50 text-gray-700'
                                }`}
                              >
                                <span>{opt}</span>
                                {isSelected && <Check className="w-4 h-4 text-indigo-600 shrink-0" />}
                              </button>
                            );
                          })}
                        </div>
                      )}

                      {/* True / False */}
                      {q.type === 'true_false' && (
                        <div className="flex gap-3 mt-3 pl-8">
                          {['True', 'False'].map((tf) => {
                            const isSelected = userAns.toLowerCase() === tf.toLowerCase();
                            return (
                              <button
                                key={tf}
                                type="button"
                                disabled={Boolean(quizResult)}
                                onClick={() => handleAnswerChange(q.id, tf)}
                                className={`flex-1 py-2.5 rounded-lg border text-xs font-semibold transition-all cursor-pointer ${
                                  isSelected
                                    ? 'border-indigo-600 bg-indigo-50 text-indigo-900'
                                    : 'border-gray-200 hover:bg-gray-50 text-gray-700'
                                }`}
                              >
                                {tf}
                              </button>
                            );
                          })}
                        </div>
                      )}

                      {/* Short Answer */}
                      {q.type === 'short_answer' && (
                        <div className="mt-3 pl-8">
                          <input
                            type="text"
                            disabled={Boolean(quizResult)}
                            value={userAns}
                            onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                            placeholder="Type your answer here..."
                            className="w-full px-3.5 py-2 bg-gray-50 border border-gray-200 rounded-lg text-xs text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white"
                          />
                        </div>
                      )}

                      {/* Explanation & Correct Answer (Visible after submit) */}
                      {resultDetail && (
                        <div className="mt-4 pt-3 border-t border-gray-200/60 pl-8 space-y-1 text-xs">
                          <p className="font-semibold text-gray-900">
                            Correct Answer: <span className="text-emerald-700">{q.correct_answer}</span>
                          </p>
                          <p className="text-gray-600 leading-relaxed text-[11px] bg-white/80 p-2.5 rounded border border-gray-100">
                            {q.explanation}
                          </p>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Submit Footer */}
              {!quizResult && (
                <div className="p-4 border-t border-gray-100 bg-gray-50/50 flex justify-end">
                  <button
                    onClick={handleSubmitQuiz}
                    disabled={submitting || Object.keys(userAnswers).length === 0}
                    className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-200 disabled:text-gray-400 text-white rounded-lg text-sm font-semibold transition-colors flex items-center gap-2 cursor-pointer shadow-xs"
                  >
                    {submitting ? (
                      <>
                        <LoadingSpinner size="sm" />
                        <span>Evaluating Responses...</span>
                      </>
                    ) : (
                      <>
                        <CheckCircle className="w-4 h-4" />
                        <span>Submit Answers & Score</span>
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-gray-400">
              <Brain className="w-12 h-12 text-gray-300 mb-3" />
              <h4 className="text-base font-semibold text-gray-700">No Quiz Active</h4>
              <p className="text-xs text-gray-500 max-w-sm mt-1">
                Configure quiz settings on the left and click "Generate Interactive Quiz" to test your knowledge.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
