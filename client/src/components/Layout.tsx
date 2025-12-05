import { Link, Outlet, useLocation } from 'react-router-dom'
import { useState } from 'react'
import clsx from 'clsx'

const navigation = [
  { name: 'Dashboard', href: '/' },
  { name: 'Products', href: '/products' },
  { name: 'Comparisons', href: '/comparisons' },
  { name: 'Alerts', href: '/alerts' },
  { name: 'Analytics', href: '/analytics' },
]

export default function Layout() {
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen">
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-gray-900/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      <aside className={clsx(
        "fixed inset-y-0 left-0 z-50 w-64 bg-gray-900 border-r border-gray-800 transform transition-transform duration-200 ease-in-out lg:translate-x-0",
        sidebarOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-800">
          <Link to="/" className="flex items-center gap-2">
            <span className="text-xl font-bold text-white tracking-tight">PriceIntel</span>
          </Link>
          <button 
            className="lg:hidden p-2 text-gray-400 hover:text-white"
            onClick={() => setSidebarOpen(false)}
          >
            Close
          </button>
        </div>

        <nav className="p-4 space-y-2">
          <div className="px-3 mb-2">
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Menu</span>
          </div>
          {navigation.map((item) => {
            const isActive = location.pathname === item.href || 
              (item.href !== '/' && location.pathname.startsWith(item.href))
            
            return (
              <Link
                key={item.name}
                to={item.href}
                onClick={() => setSidebarOpen(false)}
                className={clsx(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
                  isActive 
                    ? "bg-gray-800 text-white shadow-sm" 
                    : "text-gray-400 hover:bg-gray-800/50 hover:text-white"
                )}
              >
                {item.name}
              </Link>
            )
          })}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-800">
          <div className="px-3">
            <p className="text-xs text-gray-500">Retail Price Intelligence</p>
            <p className="text-xs text-gray-600 mt-0.5">v1.0.0</p>
          </div>
        </div>
      </aside>

      <div className="lg:pl-64">
        <header className="sticky top-0 z-30 bg-white border-b border-gray-200">
          <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
            <button 
              className="lg:hidden p-2 text-gray-500 hover:text-gray-700"
              onClick={() => setSidebarOpen(true)}
            >
              Menu
            </button>
            
            <div className="flex-1 lg:flex-none" />
            
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-500">
                {new Date().toLocaleDateString('en-US', { 
                  weekday: 'long', 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </span>
            </div>
          </div>
        </header>

        <main className="p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
