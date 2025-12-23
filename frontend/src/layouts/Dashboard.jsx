import { useState } from 'react'
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth0 } from '@auth0/auth0-react'
import { Button } from '@/components/ui/button'
import { 
  ShieldCheck, 
  Home, 
  FileCheck, 
  BarChart3, 
  Settings, 
  LogOut,
  Menu,
  X,
  Link as LinkIcon,
  Key
} from 'lucide-react'

function Dashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const { logout } = useAuth0()

  const handleLogout = () => {
    logout({ 
      logoutParams: { 
        returnTo: window.location.origin + '/login' 
      } 
    })
  }

  const navigation = [
    { name: 'Overview', href: '/dashboard', icon: Home },
    { name: 'Generate Link', href: '/dashboard/generate-link', icon: LinkIcon },
    { name: 'Verifications', href: '/dashboard/verifications', icon: FileCheck },
    { name: 'API Keys', href: '/dashboard/api-keys', icon: Key },
    { name: 'Analytics', href: '/dashboard/analytics', icon: BarChart3 },
    { name: 'Settings', href: '/dashboard/settings', icon: Settings },
  ]

  const isActive = (path) => {
    if (path === '/dashboard') {
      return location.pathname === '/dashboard'
    }
    return location.pathname.startsWith(path)
  }

  return (
    <div className="min-h-screen text-slate-50">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-gray-900/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed top-0 left-0 z-50 h-full w-64 bg-white/10 backdrop-blur-xl border-r border-white/15 shadow-xl text-slate-50
        transform transition-transform duration-200 ease-in-out lg:translate-x-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200/80">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-8 h-8 text-blue-600" />
              <span className="text-xl font-bold text-gray-900">VerifAi</span>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden text-gray-500 hover:text-gray-700"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const Icon = item.icon
              const active = isActive(item.href)
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`
                    flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium
                    transition-all duration-200 ease-out
                    ${active 
                      ? 'bg-white/20 text-white shadow-sm' 
                      : 'text-slate-100 hover:bg-white/10 hover:shadow-sm hover:-translate-x-0.5'
                    }
                  `}
                >
                  <Icon className="w-5 h-5" />
                  {item.name}
                </Link>
              )
            })}
          </nav>

          {/* User section */}
          <div className="p-4 border-t border-white/15">
            <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-white/10">
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                <span className="text-sm font-medium text-white">
                  {localStorage.getItem('userEmail')?.[0]?.toUpperCase() || 'U'}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  {localStorage.getItem('userEmail') || 'User'}
                </p>
                <p className="text-xs text-slate-200/80">Administrator</p>
              </div>
            </div>
            <Button
              onClick={handleLogout}
              variant="ghost"
              className="w-full mt-2 justify-start text-slate-100 hover:text-red-200 hover:bg-white/10 transition-colors duration-200"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <header className="sticky top-0 z-30 bg-white/10 backdrop-blur-xl border-b border-white/15 shadow-sm h-16 flex items-center px-4 lg:px-8 text-white">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden text-slate-200 hover:text-white mr-4 transition-colors"
          >
            <Menu className="w-6 h-6" />
          </button>
          <h1 className="text-xl font-semibold text-white">
            {navigation.find(item => isActive(item.href))?.name || 'Dashboard'}
          </h1>
        </header>

        {/* Page content */}
        <main className="p-4 lg:p-8 text-slate-50">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default Dashboard
