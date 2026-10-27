import React, { type ReactNode } from 'react';
import { FileX } from 'lucide-react';

interface Props {
  icon?: ReactNode | React.ComponentType<{ size?: number; className?: string }>;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  className = '',
}: Props) {
  let renderedIcon: ReactNode = <FileX size={48} />;
  if (icon) {
    if (React.isValidElement(icon)) {
      renderedIcon = icon;
    } else if (typeof icon === 'function') {
      const IconComponent = icon as React.ComponentType<{ size?: number; className?: string }>;
      renderedIcon = <IconComponent size={48} />;
    }
  }

  return (
    <div
      className={`flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-200 p-12 text-center ${className}`}
    >
      <div className="mb-4 text-gray-300">{renderedIcon}</div>
      <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
      {description && (
        <p className="mt-1 max-w-sm text-sm text-gray-500">{description}</p>
      )}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export default EmptyState;
