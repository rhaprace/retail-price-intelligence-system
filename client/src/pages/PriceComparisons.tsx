import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { comparisonsApi, type PriceComparison } from '../lib/api'
import { formatCurrency } from '../lib/utils'
import { PageHeader, Card, LoadingSpinner, EmptyState, ErrorMessage, Badge } from '../components/ui'

export default function PriceComparisons() {
  const { data: comparisons, isLoading, error } = useQuery({
    queryKey: ['comparisons'],
    queryFn: () => comparisonsApi.getAll(50),
  })

  return (
    <div className="space-y-6">
      <PageHeader title="Price Comparisons" description="Compare prices across different retailers" />

      <Card padding="none">
        <ComparisonContent comparisons={comparisons?.data} isLoading={isLoading} error={error} />
      </Card>
    </div>
  )
}

interface ComparisonContentProps {
  comparisons: PriceComparison[] | undefined
  isLoading: boolean
  error: Error | null
}

function ComparisonContent({ comparisons, isLoading, error }: ComparisonContentProps) {
  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message="Error loading comparisons" />
  if (!comparisons?.length) return <EmptyState message="No comparisons available" />

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {['Product', 'Sources', 'Min Price', 'Max Price', 'Avg Price', 'Savings', 'Actions'].map(header => (
              <th key={header} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {comparisons.map(comparison => (
            <ComparisonRow key={comparison.product_id} comparison={comparison} />
          ))}
        </tbody>
      </table>
    </div>
  )
}

function ComparisonRow({ comparison }: { comparison: PriceComparison }) {
  const savings = comparison.min_price && comparison.max_price ? comparison.max_price - comparison.min_price : null

  return (
    <tr className="hover:bg-gray-50">
      <td className="px-6 py-4">
        <Link
          to={`/products/${comparison.product_id}`}
          className="text-gray-900 font-medium hover:text-primary-600 line-clamp-2"
        >
          {comparison.product_name}
        </Link>
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        <Badge>{comparison.source_count} sources</Badge>
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        <span className="text-green-600 font-semibold">{formatCurrency(comparison.min_price)}</span>
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-gray-900">{formatCurrency(comparison.max_price)}</td>
      <td className="px-6 py-4 whitespace-nowrap text-gray-600">{formatCurrency(comparison.avg_price)}</td>
      <td className="px-6 py-4 whitespace-nowrap">
        {savings && savings > 0 ? (
          <span className="inline-flex items-center gap-1 text-green-600 font-medium">
            ↓ {formatCurrency(savings)}
          </span>
        ) : (
          <span className="text-gray-400">—</span>
        )}
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        <Link to={`/products/${comparison.product_id}`} className="text-primary-600 hover:text-primary-700">
          View
        </Link>
      </td>
    </tr>
  )
}
