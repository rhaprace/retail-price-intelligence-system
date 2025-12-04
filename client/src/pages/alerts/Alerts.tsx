import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { alertsApi, productsApi, type PriceAlert } from '../../lib/api'
import { PageHeader, Card, StatCard, Button, LoadingSpinner, EmptyState } from '../../components/ui'
import { AlertRow } from './AlertRow'
import { CreateAlertModal } from './CreateAlertModal'

export function Alerts() {
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
          <Button onClick={() => setShowCreateModal(true)}>
            New Alert
          </Button>
        }
      />

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard title="Active Alerts" value={activeAlerts.length} color="green" />
        <StatCard title="Inactive Alerts" value={inactiveAlerts.length} color="gray" />
        <StatCard title="Total Triggers" value={totalTriggers} color="primary" />
      </div>

      <Card padding="none">
        <div className="p-4 border-b border-gray-200">
          <h2 className="font-semibold text-gray-900">All Alerts</h2>
        </div>

        {isLoading ? (
          <LoadingSpinner />
        ) : !alertList.length ? (
          <EmptyState
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
