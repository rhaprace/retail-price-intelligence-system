import type { LucideIcon } from 'lucide-react'

interface EmptyStateProps {
  icon: LucideIcon
  message: string
  action?: {
    label: string
    onClick: () => void
  }
}

export default function EmptyState({ icon: Icon, message, action }: EmptyStateProps) {
  return (
    <div className="text-center py-12">
      <Icon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
      <p className="text-gray-500">{message}</p>
      {action && (
        <button
          onClick={action.onClick}
          className="mt-4 text-primary-600 hover:text-primary-700"
        >
          {action.label}
        </button>
      )}
    </div>
  )
}
