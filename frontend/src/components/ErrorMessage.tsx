import { AlertCircle, X, RotateCcw } from 'lucide-react';

interface Props {
  message: string;
  onDismiss?: () => void;
  onRetry?: () => void;
  className?: string;
}

export function ErrorMessage({ message, onDismiss, onRetry, className = '' }: Props) {
  return (
    <div
      className={`flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4 ${className}`}
    >
      <AlertCircle className="mt-0.5 shrink-0 text-red-500" size={20} />
      <div className="flex-1">
        <p className="text-sm text-red-700">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-2 inline-flex items-center gap-1.5 text-xs font-semibold text-red-700 hover:text-red-900 cursor-pointer"
          >
            <RotateCcw size={13} />
            <span>Try Again</span>
          </button>
        )}
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="shrink-0 text-red-400 hover:text-red-600 cursor-pointer"
        >
          <X size={16} />
        </button>
      )}
    </div>
  );
}

export default ErrorMessage;
