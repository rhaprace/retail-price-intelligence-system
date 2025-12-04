import type { ErrorMessageProps } from './types'

export default function ErrorMessage({ message }: ErrorMessageProps) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <p className="text-red-700">{message}</p>
    </div>
  )
}
