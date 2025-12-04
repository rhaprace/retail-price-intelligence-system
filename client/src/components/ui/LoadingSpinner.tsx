interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const sizes = {
  sm: 'h-6 w-6',
  md: 'h-8 w-8',
  lg: 'h-12 w-12',
}

export default function LoadingSpinner({ size = 'md', className = '' }: LoadingSpinnerProps) {
  return (
    <div className={`flex items-center justify-center py-12 ${className}`}>
      <div className={`animate-spin rounded-full border-b-2 border-primary-600 ${sizes[size]}`} />
    </div>
  )
}
