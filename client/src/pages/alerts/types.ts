import type { PriceAlert, Product } from '../../lib/api'

export interface AlertRowProps {
  alert: PriceAlert
  onToggle: () => void
  onDelete: () => void
}

export interface CreateAlertModalProps {
  products: Product[]
  onClose: () => void
}
