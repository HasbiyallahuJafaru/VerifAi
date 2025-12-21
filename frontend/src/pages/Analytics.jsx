import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

function Analytics() {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Analytics & Reports</CardTitle>
          <CardDescription>Detailed verification statistics and trends</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <p className="text-gray-500">Analytics dashboard coming soon...</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Analytics
