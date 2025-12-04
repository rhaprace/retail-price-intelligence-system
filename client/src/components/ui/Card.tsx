interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  className?: string
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

const paddings = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
}

export default function Card({ children, className = '', padding = 'md', ...props }: CardProps) {
  return (
    <div className={`bg-white rounded-xl border border-gray-200 ${paddings[padding]} ${className}`} {...props}>
      {children}
    </div>
  )
}
