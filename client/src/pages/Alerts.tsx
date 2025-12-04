import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Bell, BellOff, Trash2, Plus } from 'lucide-react'
import { useState } from 'react'
import { alertsApi, productsApi, type PriceAlert, type Product } from '../lib/api'
import { formatCurrency } from '../lib/utils'
import { PageHeader, Card, StatCard, Button, LoadingSpinner, EmptyState } from '../components/ui'

export default function Alerts() {
  const queryClient = useQueryClient()
  const [showCreateModal, setShowCreateModal] = useState(false)

  const { data: alerts, isLoading } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => alertsApi.getAll(),
  })

  const { data: products } = useQuery({
    queryKey: ['products'],
    queryFn: () => productsApi.getAll({ limit: 100 }),
  })

  const activateMutation = useMutation({
    mutationFn: alertsApi.activate,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['alerts'] }),
  })

  const deactivateMutation = useMutation({
    mutationFn: alertsApi.deactivate,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['alerts'] }),
  })

  const deleteMutation = useMutation({
    mutationFn: alertsApi.delete,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['alerts'] }),
  })

  const alertList: PriceAlert[] = alerts?.data ?? []
  const activeAlerts = alertList.filter(a => a.is_active)
  const inactiveAlerts = alertList.filter(a => !a.is_active)
  const totalTriggers = alertList.reduce((sum, a) => sum + a.trigger_count, 0)

  const handleToggle = (alert: PriceAlert) => {
    if (alert.is_active) {
      deactivateMutation.mutate(alert.id)
    } else {
      activateMutation.mutate(alert.id)
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Price Alerts"
        description="Get notified when prices drop"
        action={
          <Button icon={Plus} onClick={() => setShowCreateModal(true)}>
            New Alert
          </Button>
        }
      />

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard title="Active Alerts" value={activeAlerts.length} icon={Bell} color="green" />
        <StatCard title="Inactive Alerts" value={inactiveAlerts.length} icon={BellOff} color="gray" />
        <StatCard title="Total Triggers" value={totalTriggers} icon={Bell} color="primary" />
      </div>

      <Card padding="none">
        <div className="p-4 border-b border-gray-200">
          <h2 className="font-semibold text-gray-900">All Alerts</h2>
        </div>

        {isLoading ? (
          <LoadingSpinner />
        ) : !alertList.length ? (
          <EmptyState
            icon={Bell}
            message="No alerts yet"
            action={{ label: 'Create your first alert', onClick: () => setShowCreateModal(true) }}
          />
        ) : (
          <div className="divide-y divide-gray-200">
            {alertList.map(alert => (
              <AlertRow
                key={alert.id}
                alert={alert}
                onToggle={() => handleToggle(alert)}
                onDelete={() => deleteMutation.mutate(alert.id)}
              />
            ))}
          </div>
        )}
      </Card>

      {showCreateModal && (
        <CreateAlertModal products={products?.data ?? []} onClose={() => setShowCreateModal(false)} />
      )}
    </div>
  )
}

interface AlertRowProps {
  alert: PriceAlert
  onToggle: () => void
  onDelete: () => void
}

function AlertRow({ alert, onToggle, onDelete }: AlertRowProps) {
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
          {alert.is_active ? <Bell className="h-5 w-5" /> : <BellOff className="h-5 w-5" />}
        </Button>
        <Button variant="ghost" onClick={onDelete} className="text-red-500 hover:bg-red-50">
          <Trash2 className="h-5 w-5" />
        </Button>
      </div>
    </div>
  )
}

interface CreateAlertModalProps {
  products: Product[]
  onClose: () => void
}

function CreateAlertModal({ products, onClose }: CreateAlertModalProps) {
  const queryClient = useQueryClient()
  const [productId, setProductId] = useState('')
  const [targetPrice, setTargetPrice] = useState('')

  const createMutation = useMutation({
    mutationFn: alertsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      onClose()
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!productId) return
    createMutation.mutate({
      product_id: productId,
      target_price: targetPrice ? parseFloat(targetPrice) : undefined,
    })
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <Card className="w-full max-w-md m-4" onClick={e => e.stopPropagation()}>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Create Alert</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Product</label>
            <select
              value={productId}
              onChange={e => setProductId(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Select a product</option>
              {products.map(p => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Target Price</label>
            <input
              type="number"
              step="0.01"
              value={targetPrice}
              onChange={e => setTargetPrice(e.target.value)}
              placeholder="e.g., 99.99"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div className="flex gap-3 justify-end">
            <Button type="button" variant="secondary" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Creating...' : 'Create Alert'}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  )
}
