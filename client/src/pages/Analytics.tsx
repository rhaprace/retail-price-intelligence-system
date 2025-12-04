import { useQuery } from '@tanstack/react-query'
import { analyticsApi, type DiscountAnalysis } from '../lib/api'
import { formatCurrency, formatPercent, formatDate } from '../lib/utils'
import { PageHeader, Card, StatCard, LoadingSpinner, EmptyState, Badge } from '../components/ui'

export default function Analytics() {
  const { data: discounts, isLoading } = useQuery({
    queryKey: ['discounts'],
    queryFn: () => analyticsApi.getDiscounts(50),
  })

  const { data: fakeDiscounts } = useQuery({
    queryKey: ['fakeDiscounts'],
    queryFn: () => analyticsApi.getFakeDiscounts(20),
  })

  const fakeCount = fakeDiscounts?.data?.length ?? 0
  const totalCount = discounts?.data?.length ?? 0
  const legitimateCount = totalCount - fakeCount

  return (
    <div className="space-y-6">
      <PageHeader title="Analytics" description="Discount analysis and fake discount detection" />

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard title="Total Analyzed" value={totalCount} color="primary" />
        <StatCard title="Fake Discounts" value={fakeCount} color="red" />
        <StatCard title="Legitimate Discounts" value={legitimateCount} color="green" />
      </div>

      {fakeCount > 0 && <FakeDiscountWarning count={fakeCount} />}

      <Card padding="none">
        <div className="p-4 border-b border-gray-200">
          <h2 className="font-semibold text-gray-900">Discount Analysis</h2>
        </div>
        <AnalysisTable data={discounts?.data} isLoading={isLoading} />
      </Card>
    </div>
  )
}

function FakeDiscountWarning({ count }: { count: number }) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-xl p-6">
      <div className="flex items-start gap-4">
        <div>
          <h2 className="text-lg font-semibold text-red-800">{count} Fake Discounts Detected</h2>
          <p className="mt-1 text-sm text-red-700">
            These products are advertised with discounts, but our analysis shows the current price is not lower than the
            historical average.
          </p>
        </div>
      </div>
    </div>
  )
}

interface AnalysisTableProps {
  data: DiscountAnalysis[] | undefined
  isLoading: boolean
}

function AnalysisTable({ data, isLoading }: AnalysisTableProps) {
  if (isLoading) return <LoadingSpinner />
  if (!data?.length) return <EmptyState message="No analysis data available" />

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {['Product', 'Current Price', 'Claimed Discount', 'Actual Discount', 'Trend', 'Status'].map(header => (
              <th key={header} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {data.map(analysis => (
            <AnalysisRow key={analysis.id} analysis={analysis} />
          ))}
        </tbody>
      </table>
    </div>
  )
}

function AnalysisRow({ analysis }: { analysis: DiscountAnalysis }) {
  return (
    <tr className="hover:bg-gray-50">
      <td className="px-6 py-4">
        <p className="text-gray-900 font-medium">Product Source #{analysis.product_source_id}</p>
        <p className="text-sm text-gray-500">{formatDate(analysis.analysis_date)}</p>
      </td>
      <td className="px-6 py-4 whitespace-nowrap font-semibold text-gray-900">
        {formatCurrency(analysis.current_price)}
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-gray-600">
        {analysis.claimed_discount_percentage ? `${analysis.claimed_discount_percentage.toFixed(0)}%` : '—'}
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        {analysis.actual_discount_percentage ? (
          <span className={analysis.actual_discount_percentage > 0 ? 'text-green-600' : 'text-gray-600'}>
            {formatPercent(analysis.actual_discount_percentage)}
          </span>
        ) : (
          <span className="text-gray-400">—</span>
        )}
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        <TrendIcon trend={analysis.price_trend} />
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        <Badge variant={analysis.is_fake_discount ? 'error' : 'success'}>
          {analysis.is_fake_discount ? 'Fake' : 'Legitimate'}
        </Badge>
      </td>
    </tr>
  )
}

function TrendIcon({ trend }: { trend: string }) {
  switch (trend) {
    case 'increasing':
      return <span className="text-red-500 font-medium">↑</span>
    case 'decreasing':
      return <span className="text-green-500 font-medium">↓</span>
    default:
      return <span className="text-gray-400">—</span>
  }
}
