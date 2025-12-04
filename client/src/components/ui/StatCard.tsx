import Card from './Card'
import type { StatCardProps } from './types'

const colorClasses = {
  primary: 'border-l-primary-500',
  green: 'border-l-green-500',
  red: 'border-l-red-500',
  yellow: 'border-l-yellow-500',
  gray: 'border-l-gray-500',
}

export default function StatCard({ 
  title, 
  value, 
  color = 'primary', 
  trend 
}: StatCardProps) {
  return (
    <Card className={`border-l-4 ${colorClasses[color]}`}>
      <p className="text-sm font-medium text-gray-500">{title}</p>
      <div className="mt-2 flex items-baseline justify-between">
        <p className="text-3xl font-bold text-gray-900">{value}</p>
        {trend && (
          <span className={`text-sm font-medium ${
            trend.direction === 'up' ? 'text-green-600' : 'text-red-600'
          }`}>
            {trend.direction === 'up' ? '↑' : '↓'} {trend.value}
          </span>
        )}
      </div>
    </Card>
  )
}
