import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { CheckCircle2, XCircle, AlertCircle, TrendingUp } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

function Overview() {
  const navigate = useNavigate()

  const goToGenerate = () => navigate('/dashboard/generate-link')
  const goToVerifications = () => navigate('/dashboard/verifications')
  const handleExport = () => alert('Export report will be available soon. In the meantime, view verifications to filter and copy data.')

  const stats = [
    {
      title: 'Total Verifications',
      value: '1,234',
      change: '+12.5%',
      trend: 'up',
      icon: CheckCircle2,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      title: 'Successful',
      value: '1,089',
      change: '+8.2%',
      trend: 'up',
      icon: CheckCircle2,
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      title: 'Failed',
      value: '89',
      change: '-3.1%',
      trend: 'down',
      icon: XCircle,
      color: 'text-red-600',
      bgColor: 'bg-red-100'
    },
    {
      title: 'Pending',
      value: '56',
      change: '+15.3%',
      trend: 'up',
      icon: AlertCircle,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100'
    }
  ]

  const recentVerifications = [
    { id: 'VER-001', user: 'John Doe', status: 'success', time: '2 min ago' },
    { id: 'VER-002', user: 'Jane Smith', status: 'success', time: '5 min ago' },
    { id: 'VER-003', user: 'Bob Johnson', status: 'failed', time: '12 min ago' },
    { id: 'VER-004', user: 'Alice Brown', status: 'success', time: '18 min ago' },
    { id: 'VER-005', user: 'Charlie Wilson', status: 'pending', time: '25 min ago' },
  ]

  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return 'text-green-600 bg-green-100'
      case 'failed': return 'text-red-600 bg-red-100'
      case 'pending': return 'text-yellow-600 bg-yellow-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <Card key={stat.title} className="shadow-xl">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                    <p className="text-2xl font-bold text-gray-900 mt-2">{stat.value}</p>
                    <p className={`text-sm mt-2 ${stat.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                      {stat.change} from last month
                    </p>
                  </div>
                  <div className={`w-12 h-12 rounded-lg ${stat.bgColor} flex items-center justify-center`}>
                    <Icon className={`w-6 h-6 ${stat.color}`} />
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
              {recentVerifications.map((verification) => (
                <div key={verification.id} className="flex items-center justify-between py-3 border-b last:border-0">
                  <div>
                    <p className="font-medium text-gray-900">{verification.user}</p>
                    <p className="text-sm text-gray-500">{verification.id}</p>
                  </div>
                  <div className="text-right">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(verification.status)}`}>
                      {verification.status}
                    </span>
                    <p className="text-xs text-gray-500 mt-1">{verification.time}</p>
                  </div>
                </div>
              ))}
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
