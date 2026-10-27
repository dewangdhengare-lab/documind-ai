import { Loader2 } from 'lucide-react';

interface Props {
  className?: string;
  size?: 'sm' | 'md' | 'lg' | number;
  text?: string;
}

export function LoadingSpinner({ className = '', size = 'md', text }: Props) {
  const pixelSize =
    typeof size === 'number'
      ? size
      : size === 'sm'
      ? 16
      : size === 'lg'
      ? 36
      : 24;

  return (
    <div className={`flex flex-col items-center justify-center gap-2 ${className}`}>
      <Loader2 className="animate-spin text-indigo-600" size={pixelSize} />
      {text && <p className="text-xs text-gray-500">{text}</p>}
    </div>
  );
}

export default LoadingSpinner;
