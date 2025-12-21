import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

function Settings() {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Settings</CardTitle>
          <CardDescription>Manage your account and application preferences</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <p className="text-gray-500">Settings panel coming soon...</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Settings
