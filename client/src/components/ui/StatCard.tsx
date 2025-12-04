import { TrendingUp, TrendingDown } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

type ColorVariant = 'primary' | 'green' | 'red' | 'yellow' | 'gray'

interface StatCardProps {
  title: string
  value: string | number
  icon: LucideIcon
  color?: ColorVariant
  trend?: { direction: 'up' | 'down'; value: string }
}

const colorClasses: Record<ColorVariant, string> = {
  primary: 'bg-primary-50 text-primary-600',
  green: 'bg-green-50 text-green-600',
  red: 'bg-red-50 text-red-600',
  yellow: 'bg-yellow-50 text-yellow-600',
  gray: 'bg-gray-100 text-gray-600',
}

export default function StatCard({ title, value, icon: Icon, color = 'primary', trend }: StatCardProps) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <div className="flex items-center justify-between">
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon className="h-6 w-6" />
        </div>
        {trend && (
          <div className={`flex items-center gap-1 text-sm ${trend.direction === 'up' ? 'text-green-600' : 'text-red-600'}`}>
            {trend.direction === 'up' ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
            {trend.value}
          </div>
        )}
      </div>
      <div className="mt-4">
        <h3 className="text-sm font-medium text-gray-500">{title}</h3>
        <p className="mt-1 text-2xl font-semibold text-gray-900">{value}</p>
      </div>
    </div>
  )
}
