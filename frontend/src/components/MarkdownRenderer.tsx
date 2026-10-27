import ReactMarkdown from 'react-markdown';

interface Props {
  content: string;
  className?: string;
}

export function MarkdownRenderer({ content, className = '' }: Props) {
  return (
    <div className={`prose prose-sm max-w-none text-gray-800 leading-relaxed space-y-3 ${className}`}>
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  );
}

export default MarkdownRenderer;
