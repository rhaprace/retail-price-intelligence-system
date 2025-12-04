import { useQuery } from '@tanstack/react-query'
import { Package, DollarSign, AlertTriangle, ShoppingCart, Activity } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { pricesApi, productsApi, analyticsApi, comparisonsApi } from '../lib/api'
import { formatCurrency } from '../lib/utils'
import { StatCard, Card, PageHeader } from '../components/ui'

const CHART_DATA = [
  { date: 'Mon', price: 120 },
  { date: 'Tue', price: 115 },
  { date: 'Wed', price: 118 },
  { date: 'Thu', price: 110 },
  { date: 'Fri', price: 105 },
  { date: 'Sat', price: 108 },
  { date: 'Sun', price: 102 },
]

export default function Dashboard() {
  const { data: products } = useQuery({
    queryKey: ['products'],
    queryFn: () => productsApi.getAll({ limit: 100 }),
  })

  const { data: latestPrices } = useQuery({
    queryKey: ['latestPrices'],
    queryFn: () => pricesApi.getLatest(50),
  })

  const { data: fakeDiscounts } = useQuery({
    queryKey: ['fakeDiscounts'],
    queryFn: () => analyticsApi.getFakeDiscounts(10),
  })

  const { data: comparisons } = useQuery({
    queryKey: ['comparisons'],
    queryFn: () => comparisonsApi.getAll(20),
  })

  const productCount = products?.data?.length ?? 0
  const prices = latestPrices?.data ?? []
  const avgPrice = prices.length
    ? formatCurrency(prices.reduce((sum, p) => sum + p.price, 0) / prices.length)
    : '$0.00'
  const fakeDiscountCount = fakeDiscounts?.data?.length ?? 0
  const savingsOpportunities =
    comparisons?.data?.filter(c => c.min_price && c.max_price && c.max_price - c.min_price > 10).length ?? 0

  return (
    <div className="space-y-6">
      <PageHeader title="Dashboard" description="Overview of your price intelligence data" />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Products" value={productCount} icon={Package} color="primary" />
        <StatCard
          title="Average Price"
          value={avgPrice}
          icon={DollarSign}
          color="green"
          trend={{ direction: 'down', value: '3.2%' }}
        />
        <StatCard title="Fake Discounts" value={fakeDiscountCount} icon={AlertTriangle} color="yellow" />
        <StatCard title="Savings Found" value={savingsOpportunities} icon={ShoppingCart} color="green" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Price Trends</h2>
            <Activity className="h-5 w-5 text-gray-400" />
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={CHART_DATA}>
                <XAxis dataKey="date" axisLine={false} tickLine={false} />
                <YAxis axisLine={false} tickLine={false} />
                <Tooltip />
                <Line type="monotone" dataKey="price" stroke="#3b82f6" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Stats</h2>
          <div className="space-y-4">
            <QuickStatRow label="Products tracked" value={productCount} />
            <QuickStatRow label="Price alerts active" value={fakeDiscountCount} />
            <QuickStatRow label="Sources monitored" value={3} />
            <QuickStatRow label="Savings opportunities" value={savingsOpportunities} />
          </div>
        </Card>
      </div>
    </div>
  )
}

function QuickStatRow({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
      <span className="text-gray-600">{label}</span>
      <span className="font-semibold text-gray-900">{value}</span>
    </div>
  )
}
