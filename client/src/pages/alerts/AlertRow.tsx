import { formatCurrency } from '../../lib/utils'
import { Button } from '../../components/ui'
import type { AlertRowProps } from './types'

export function AlertRow({ alert, onToggle, onDelete }: AlertRowProps) {
  return (
    <div className="p-4 flex items-center justify-between">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${alert.is_active ? 'bg-green-500' : 'bg-gray-400'}`} />
          <p className="font-medium text-gray-900 truncate">Product: {alert.product_id.slice(0, 8)}...</p>
        </div>
        <div className="mt-1 flex items-center gap-4 text-sm text-gray-500">
          {alert.target_price && <span>Target: {formatCurrency(alert.target_price)}</span>}
          {alert.price_drop_percentage && <span>Drop: {alert.price_drop_percentage}%</span>}
          <span>Triggered: {alert.trigger_count}x</span>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          onClick={onToggle}
          className={alert.is_active ? 'text-green-600 hover:bg-green-50' : 'text-gray-400'}
        >
          {alert.is_active ? 'On' : 'Off'}
        </Button>
        <Button variant="ghost" onClick={onDelete} className="text-red-500 hover:bg-red-50">
          Delete
        </Button>
      </div>
    </div>
  )
}
