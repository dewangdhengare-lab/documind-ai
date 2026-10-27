import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Documents } from './pages/Documents';
import { Chat } from './pages/Chat';
import { Summarize } from './pages/Summarize';
import { Extract } from './pages/Extract';
import { Compare } from './pages/Compare';
import { QuizPage } from './pages/Quiz';
import { Reports } from './pages/Reports';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="documents" element={<Documents />} />
          <Route path="chat" element={<Chat />} />
          <Route path="summarize" element={<Summarize />} />
          <Route path="extract" element={<Extract />} />
          <Route path="compare" element={<Compare />} />
          <Route path="quiz" element={<QuizPage />} />
          <Route path="reports" element={<Reports />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
