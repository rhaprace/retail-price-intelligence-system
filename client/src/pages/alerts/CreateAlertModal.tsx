import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { alertsApi } from '../../lib/api'
import { Card, Button } from '../../components/ui'
import type { CreateAlertModalProps } from './types'

export function CreateAlertModal({ products, onClose }: CreateAlertModalProps) {
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
      <Card className="w-full max-w-md m-4" onClick={(e: React.MouseEvent) => e.stopPropagation()}>
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
