type BadgeVariant = 'default' | 'primary' | 'success' | 'warning' | 'error'

interface BadgeProps {
  children: React.ReactNode
  variant?: BadgeVariant
}

const variantClasses: Record<BadgeVariant, string> = {
  default: 'bg-gray-100 text-gray-700',
  primary: 'bg-primary-100 text-primary-700',
  success: 'bg-green-100 text-green-700',
  warning: 'bg-yellow-100 text-yellow-700',
  error: 'bg-red-100 text-red-700',
}

export default function Badge({ children, variant = 'default' }: BadgeProps) {
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium ${variantClasses[variant]}`}>
      {children}
    </span>
  )
}
