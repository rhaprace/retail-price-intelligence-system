import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { useState, useMemo } from 'react'
import { productsApi, type Product } from '../lib/api'
import { PageHeader, LoadingSpinner, EmptyState, ErrorMessage, Badge } from '../components/ui'

export default function Products() {
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')

  const { data: products, isLoading, error } = useQuery({
    queryKey: ['products', search, category],
    queryFn: () =>
      productsApi.getAll({
        search: search || undefined,
        category: category || undefined,
        limit: 50,
      }),
  })

  const categories = useMemo(
    () => [...new Set(products?.data?.map(p => p.category).filter(Boolean))],
    [products?.data]
  )

  return (
    <div className="space-y-6">
      <PageHeader title="Products" description="Track prices across all your products" />

      <SearchFilters
        search={search}
        category={category}
        categories={categories as string[]}
        onSearchChange={setSearch}
        onCategoryChange={setCategory}
      />

      <ProductGrid products={products?.data} isLoading={isLoading} error={error} />
    </div>
  )
}

interface SearchFiltersProps {
  search: string
  category: string
  categories: string[]
  onSearchChange: (value: string) => void
  onCategoryChange: (value: string) => void
}

function SearchFilters({ search, category, categories, onSearchChange, onCategoryChange }: SearchFiltersProps) {
  return (
    <div className="flex flex-col sm:flex-row gap-4">
      <div className="relative flex-1">
        <input
          type="text"
          placeholder="Search products..."
          value={search}
          onChange={e => onSearchChange(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        />
      </div>
      <div className="relative">
        <select
          value={category}
          onChange={e => onCategoryChange(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 appearance-none bg-white"
        >
          <option value="">All Categories</option>
          {categories.map(cat => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>
    </div>
  )
}

interface ProductGridProps {
  products: Product[] | undefined
  isLoading: boolean
  error: Error | null
}

function ProductGrid({ products, isLoading, error }: ProductGridProps) {
  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message="Error loading products" />
  if (!products?.length) return <EmptyState message="No products found" />

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {products.map(product => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  )
}

function ProductCard({ product }: { product: Product }) {
  return (
    <Link
      to={`/products/${product.id}`}
      className="bg-white rounded-xl border border-gray-200 p-4 hover:shadow-md transition-shadow"
    >
      <div className="aspect-square bg-gray-100 rounded-lg mb-4 flex items-center justify-center">
        {product.image_url ? (
          <img src={product.image_url} alt={product.name} className="w-full h-full object-cover rounded-lg" />
        ) : (
          <span className="text-gray-400 text-sm">No image</span>
        )}
      </div>
      <div>
        <h3 className="font-medium text-gray-900 line-clamp-2">{product.name}</h3>
        <div className="mt-2 flex items-center gap-2">
          {product.brand && <span className="text-xs text-gray-500">{product.brand}</span>}
          {product.category && <Badge>{product.category}</Badge>}
        </div>
      </div>
    </Link>
  )
}
