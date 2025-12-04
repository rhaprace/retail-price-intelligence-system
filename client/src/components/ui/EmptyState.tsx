import type { EmptyStateProps } from './types'

export default function EmptyState({ message, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      <div className="w-16 h-16 rounded-full border-2 border-dashed border-gray-300 flex items-center justify-center mb-4">
        <span className="text-gray-400 text-2xl">?</span>
      </div>
      <p className="text-gray-500 text-center mb-4">{message}</p>
      {action && (
        <button
          onClick={action.onClick}
          className="text-primary-600 hover:text-primary-700 font-medium"
        >
          {action.label}
        </button>
      )}
    </div>
  )
}
