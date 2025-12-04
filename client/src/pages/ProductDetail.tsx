import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { productsApi, type Product, type ProductSource, type ProductPrice } from '../lib/api'
import { formatCurrency, formatDate, calculatePercentChange } from '../lib/utils'
import { Card, Badge, LoadingSpinner } from '../components/ui'

export default function ProductDetail() {
  const { id } = useParams<{ id: string }>()

  const { data: product, isLoading } = useQuery({
    queryKey: ['product', id],
    queryFn: () => productsApi.getById(id!),
    enabled: !!id,
  })

  const { data: sources } = useQuery({
    queryKey: ['productSources', id],
    queryFn: () => productsApi.getSources(id!),
    enabled: !!id,
  })

  const { data: prices } = useQuery({
    queryKey: ['productPrices', id],
    queryFn: () => productsApi.getPrices(id!, 30),
    enabled: !!id,
  })

  if (isLoading) return <LoadingSpinner />

  if (!product?.data) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Product not found</p>
        <Link to="/products" className="text-primary-600 hover:text-primary-700 mt-2 inline-block">
          Back to products
        </Link>
      </div>
    )
  }

  const p = product.data
  const priceData: ProductPrice[] = prices?.data ?? []
  const chartData = priceData
    .map(price => ({
      date: formatDate(price.scraped_at),
      price: price.price,
    }))
    .reverse()

  const currentPrice = priceData[0]?.price
  const oldestPrice = priceData[priceData.length - 1]?.price
  const priceChange = currentPrice && oldestPrice ? calculatePercentChange(currentPrice, oldestPrice) : null

  return (
    <div className="space-y-6">
      <BackLink />
      <ProductInfo product={p} currentPrice={currentPrice} priceChange={priceChange} />
      {chartData.length > 0 && <PriceChart data={chartData} />}
      <SourcesList sources={sources?.data} />
    </div>
  )
}

function BackLink() {
  return (
    <Link to="/products" className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900">
      <span>←</span>
      Back to products
    </Link>
  )
}

interface ProductInfoProps {
  product: Product
  currentPrice: number | undefined
  priceChange: number | null
}

function ProductInfo({ product, currentPrice, priceChange }: ProductInfoProps) {
  const isDown = priceChange !== null && priceChange < 0

  return (
    <Card>
      <div className="flex flex-col lg:flex-row gap-6">
        <div className="w-full lg:w-64 h-64 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
          {product.image_url ? (
            <img src={product.image_url} alt={product.name} className="w-full h-full object-cover rounded-lg" />
          ) : (
            <span className="text-gray-400">No image</span>
          )}
        </div>

        <div className="flex-1">
          <h1 className="text-2xl font-bold text-gray-900">{product.name}</h1>

          <div className="mt-4 flex flex-wrap gap-2">
            {product.brand && <Badge>{product.brand}</Badge>}
            {product.category && <Badge variant="primary">{product.category}</Badge>}
            {product.sku && <Badge>SKU: {product.sku}</Badge>}
          </div>

          {product.description && <p className="mt-4 text-gray-600">{product.description}</p>}

          {currentPrice && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Current Best Price</p>
                  <p className="text-3xl font-bold text-gray-900">{formatCurrency(currentPrice)}</p>
                </div>
                {priceChange !== null && (
                  <div className={`flex items-center gap-1 ${isDown ? 'text-green-600' : 'text-red-600'}`}>
                    <span>{isDown ? '↓' : '↑'}</span>
                    <span className="text-lg font-semibold">{priceChange.toFixed(1)}%</span>
                    <span className="text-sm">30d</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </Card>
  )
}

function PriceChart({ data }: { data: { date: string; price: number }[] }) {
  return (
    <Card>
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Price History (30 days)</h2>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" axisLine={false} tickLine={false} />
            <YAxis axisLine={false} tickLine={false} tickFormatter={v => `$${v}`} />
            <Tooltip formatter={(value: number) => [formatCurrency(value), 'Price']} />
            <Line type="monotone" dataKey="price" stroke="#3b82f6" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Card>
  )
}

function SourcesList({ sources }: { sources: ProductSource[] | undefined }) {
  return (
    <Card>
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Available Sources</h2>
      {sources?.length ? (
        <div className="divide-y divide-gray-200">
          {sources.map(source => (
            <SourceRow key={source.id} source={source} />
          ))}
        </div>
      ) : (
        <p className="text-gray-500">No sources available</p>
      )}
    </Card>
  )
}

function SourceRow({ source }: { source: ProductSource }) {
  const hasValidUrl = source.source_product_url && 
    (source.source_product_url.startsWith('http://') || source.source_product_url.startsWith('https://'))

  return (
    <div className="py-4 flex items-center justify-between">
      <div>
        <p className="font-medium text-gray-900">{source.source_name}</p>
        <p className="text-sm text-gray-500">{source.source_product_name}</p>
      </div>
      <div className="flex items-center gap-4">
        {source.latest_price && (
          <span className="text-lg font-semibold text-gray-900">{formatCurrency(source.latest_price)}</span>
        )}
        {hasValidUrl ? (
          <a
            href={source.source_product_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            Visit
          </a>
        ) : (
          <span className="text-gray-400">No link</span>
        )}
      </div>
    </div>
  )
}
