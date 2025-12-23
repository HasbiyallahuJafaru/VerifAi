import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { CheckCircle2, XCircle, AlertCircle, TrendingUp, Loader2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { API_BASE_URL } from '../config'

function Overview() {
  const navigate = useNavigate()
  const [stats, setStats] = useState(null)
  const [recentVerifications, setRecentVerifications] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const token = localStorage.getItem('accessToken')
        const response = await fetch(`${API_BASE_URL}/api/dashboard-stats`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        const data = await response.json()
        
        if (response.ok) {
          setStats(data.stats)
          setRecentVerifications(data.recent || [])
        }
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err)
      } finally {
        setIsLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  const goToGenerate = () => navigate('/dashboard/generate-link')
  const goToVerifications = () => navigate('/dashboard/verifications')
  const handleExport = () => alert('Export report will be available soon. In the meantime, view verifications to filter and copy data.')

  const statsConfig = [
    {
      title: 'Total Verifications',
      key: 'total',
      change: '+12.5%',
      trend: 'up',
      icon: CheckCircle2,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      title: 'Successful',
      key: 'successful',
      change: '+8.2%',
      trend: 'up',
      icon: CheckCircle2,
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      title: 'Failed',
      key: 'failed',
      change: '-3.1%',
      trend: 'down',
      icon: XCircle,
      color: 'text-red-600',
      bgColor: 'bg-red-100'
    },
    {
      title: 'Pending',
      key: 'pending',
      change: '+15.3%',
      trend: 'up',
      icon: AlertCircle,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100'
    }
  ]

  const getStatusColor = (status) => {
    switch (status) {
      case 'success':
      case 'verified': return 'text-green-600 bg-green-100'
      case 'failed': return 'text-red-600 bg-red-100'
      case 'pending': return 'text-yellow-600 bg-yellow-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const formatTimeAgo = (dateString) => {
    if (!dateString) return 'Unknown'
    const date = new Date(dateString)
    const now = new Date()
    const diffInSeconds = Math.floor((now - date) / 1000)
    
    if (diffInSeconds < 60) return `${diffInSeconds}s ago`
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
    return `${Math.floor(diffInSeconds / 86400)}d ago`
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statsConfig.map((statConfig) => {
          const Icon = statConfig.icon
          const value = stats ? stats[statConfig.key] : 0
          return (
            <Card key={statConfig.title} className="shadow-xl">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">{statConfig.title}</p>
                    <p className="text-2xl font-bold text-gray-900 mt-2">{value.toLocaleString()}</p>
                    <p className={`text-sm mt-2 ${statConfig.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                      {statConfig.change} from last month
                    </p>
                  </div>
                  <div className={`w-12 h-12 rounded-lg ${statConfig.bgColor} flex items-center justify-center`}>
                    <Icon className={`w-6 h-6 ${statConfig.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="shadow-xl">
          <CardHeader>
            <CardTitle>Recent Verifications</CardTitle>
            <CardDescription>Latest verification requests</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentVerifications.length > 0 ? (
                recentVerifications.map((verification, index) => (
                  <div key={verification.tokenId || index} className="flex items-center justify-between py-3 border-b last:border-0">
                    <div>
                      <p className="font-medium text-gray-900">{verification.fullName || 'Unknown'}</p>
                      <p className="text-sm text-gray-500">{verification.tokenId?.substring(0, 12)}...</p>
                    </div>
                    <div className="text-right">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(verification.verificationStatus)}`}>
                        {verification.verificationStatus || 'pending'}
                      </span>
                      <p className="text-xs text-gray-500 mt-1">{formatTimeAgo(verification.createdAt)}</p>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-center text-gray-500 py-8">No recent verifications</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-xl">
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common tasks and operations</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <button onClick={goToGenerate} className="w-full text-left px-4 py-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-all duration-200 hover:-translate-y-0.5">
                <p className="font-medium text-gray-900">New Verification Request</p>
                <p className="text-sm text-gray-500">Initiate a new address verification</p>
              </button>
              <button onClick={goToVerifications} className="w-full text-left px-4 py-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-all duration-200 hover:-translate-y-0.5">
                <p className="font-medium text-gray-900">View All Verifications</p>
                <p className="text-sm text-gray-500">See complete verification history</p>
              </button>
              <button onClick={handleExport} className="w-full text-left px-4 py-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-all duration-200 hover:-translate-y-0.5">
                <p className="font-medium text-gray-900">Export Report</p>
                <p className="text-sm text-gray-500">Download verification data</p>
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Overview
