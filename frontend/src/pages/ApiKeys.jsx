import { useState, useEffect, useCallback } from 'react'
import { useAuth0 } from '@auth0/auth0-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle,
  DialogFooter
} from '@/components/ui/dialog'
import { 
  Key, 
  Copy, 
  Trash2, 
  Power, 
  PowerOff, 
  Plus,
  CheckCircle2,
  AlertCircle,
  Eye,
  EyeOff,
  Calendar,
  TrendingUp
} from 'lucide-react'
import { API_BASE_URL } from '../config'

function ApiKeys() {
  const { getAccessTokenSilently } = useAuth0()
  const [apiKeys, setApiKeys] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [newKey, setNewKey] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    company: '',
    description: '',
    expiresInDays: '',
  })
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)
  const [showKey, setShowKey] = useState(false)

  const fetchApiKeys = useCallback(async () => {
    try {
      const token = await getAccessTokenSilently()
      const response = await fetch(`${API_BASE_URL}/api/api-keys`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      setApiKeys(data.apiKeys || [])
    } catch {
      setError('Failed to load API keys')
    } finally {
      setIsLoading(false)
    }
  }, [getAccessTokenSilently])

  useEffect(() => {
    fetchApiKeys()
  }, [fetchApiKeys])

  const handleCreate = async (e) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      const payload = {
        name: formData.name,
        company: formData.company,
        description: formData.description,
        createdBy: localStorage.getItem('userEmail') || 'admin'
      }

      if (formData.expiresInDays) {
        payload.expiresInDays = parseInt(formData.expiresInDays)
      }

      const token = await getAccessTokenSilently()
      const response = await fetch(`${API_BASE_URL}/api/api-keys`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to create API key')
      }

      setNewKey(data)
      setFormData({ name: '', company: '', description: '', expiresInDays: '' })
      await fetchApiKeys()
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  const toggleKeyStatus = async (keyId, currentStatus) => {
    try {
      const token = await getAccessTokenSilently()
      const response = await fetch(`${API_BASE_URL}/api/api-keys/${keyId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ active: !currentStatus })
      })

      if (response.ok) {
        await fetchApiKeys()
      }
    } catch {
      setError('Failed to update API key')
    }
  }

  const deleteKey = async (keyId) => {
    if (!confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
      return
    }

    try {
      const token = await getAccessTokenSilently()
      const response = await fetch(`${API_BASE_URL}/api/api-keys/${keyId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        await fetchApiKeys()
      }
    } catch {
      setError('Failed to delete API key')
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Never'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">API Keys</h2>
          <p className="text-gray-600 mt-1">Manage API keys for programmatic access to VerifAi</p>
        </div>
        <Button 
          onClick={() => setShowCreateDialog(true)}
          className="bg-blue-600 hover:bg-blue-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create API Key
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Keys</p>
                <p className="text-2xl font-bold text-gray-900">{apiKeys.length}</p>
              </div>
              <Key className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Keys</p>
                <p className="text-2xl font-bold text-green-600">
                  {apiKeys.filter(k => k.active).length}
                </p>
              </div>
              <CheckCircle2 className="w-8 h-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Usage</p>
                <p className="text-2xl font-bold text-gray-900">
                  {apiKeys.reduce((sum, k) => sum + (k.usageCount || 0), 0)}
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* API Keys List */}
      <Card>
        <CardHeader>
          <CardTitle>Your API Keys</CardTitle>
          <CardDescription>API keys are used to authenticate requests to the VerifAi API</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading && !apiKeys.length ? (
            <div className="text-center py-8">
              <p className="text-gray-500">Loading API keys...</p>
            </div>
          ) : apiKeys.length === 0 ? (
            <div className="text-center py-8">
              <Key className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No API keys yet</p>
              <p className="text-sm text-gray-400 mt-1">Create your first API key to get started</p>
            </div>
          ) : (
            <div className="space-y-4">
              {apiKeys.map((apiKey) => (
                <div 
                  key={apiKey.id} 
                  className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h4 className="font-semibold text-gray-900">{apiKey.name}</h4>
                        <Badge variant={apiKey.active ? "default" : "secondary"}>
                          {apiKey.active ? 'Active' : 'Inactive'}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mb-3">{apiKey.company}</p>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <p className="text-gray-500">API Key</p>
                          <code className="text-xs font-mono bg-gray-100 px-2 py-1 rounded">
                            {apiKey.keyPrefix}
                          </code>
                        </div>
                        <div>
                          <p className="text-gray-500">Created</p>
                          <p className="text-gray-900">{formatDate(apiKey.createdAt)}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Last Used</p>
                          <p className="text-gray-900">{formatDate(apiKey.lastUsedAt)}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Usage Count</p>
                          <p className="text-gray-900">{apiKey.usageCount || 0}</p>
                        </div>
                      </div>

                      {apiKey.expiresAt && (
                        <div className="mt-3">
                          <Alert className="border-amber-200 bg-amber-50">
                            <Calendar className="h-4 w-4 text-amber-600" />
                            <AlertDescription className="text-amber-900 text-sm">
                              Expires: {formatDate(apiKey.expiresAt)}
                            </AlertDescription>
                          </Alert>
                        </div>
                      )}
                    </div>

                    <div className="flex gap-2 ml-4">
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={() => toggleKeyStatus(apiKey.id, apiKey.active)}
                        title={apiKey.active ? 'Disable' : 'Enable'}
                      >
                        {apiKey.active ? (
                          <PowerOff className="w-4 h-4 text-red-600" />
                        ) : (
                          <Power className="w-4 h-4 text-green-600" />
                        )}
                      </Button>
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={() => deleteKey(apiKey.id)}
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4 text-red-600" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create API Key Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Create New API Key</DialogTitle>
            <DialogDescription>
              Generate a new API key for programmatic access to VerifAi
            </DialogDescription>
          </DialogHeader>

          {!newKey ? (
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Key Name *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Production API Key"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="company">Company Name *</Label>
                <Input
                  id="company"
                  value={formData.company}
                  onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                  placeholder="Acme Corporation"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Brief description of this key's purpose"
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="expiresInDays">Expires In (days)</Label>
                <Input
                  id="expiresInDays"
                  type="number"
                  value={formData.expiresInDays}
                  onChange={(e) => setFormData({ ...formData, expiresInDays: e.target.value })}
                  placeholder="Leave empty for no expiration"
                />
              </div>

              {error && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <DialogFooter>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => setShowCreateDialog(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? 'Creating...' : 'Create API Key'}
                </Button>
              </DialogFooter>
            </form>
          ) : (
            <div className="space-y-4">
              <Alert className="border-green-200 bg-green-50">
                <CheckCircle2 className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-900">
                  API key created successfully!
                </AlertDescription>
              </Alert>

              <div className="space-y-2">
                <Label>Your API Key</Label>
                <div className="flex gap-2">
                  <Input
                    value={newKey.apiKey}
                    readOnly
                    type={showKey ? 'text' : 'password'}
                    className="font-mono text-sm"
                  />
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => setShowKey(!showKey)}
                  >
                    {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </Button>
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => copyToClipboard(newKey.apiKey)}
                  >
                    {copied ? (
                      <CheckCircle2 className="w-4 h-4 text-green-600" />
                    ) : (
                      <Copy className="w-4 h-4" />
                    )}
                  </Button>
                </div>
              </div>

              <Alert className="border-amber-200 bg-amber-50">
                <AlertCircle className="h-4 w-4 text-amber-600" />
                <AlertDescription className="text-amber-900 text-sm">
                  <strong>Important:</strong> Save this key securely. You won't be able to see it again!
                </AlertDescription>
              </Alert>

              <div className="bg-gray-50 rounded-lg p-4 space-y-2 text-sm">
                <p><strong>Company:</strong> {newKey.apiKeyData.company}</p>
                <p><strong>Name:</strong> {newKey.apiKeyData.name}</p>
                <p><strong>Created:</strong> {formatDate(newKey.apiKeyData.createdAt)}</p>
                {newKey.apiKeyData.expiresAt && (
                  <p><strong>Expires:</strong> {formatDate(newKey.apiKeyData.expiresAt)}</p>
                )}
              </div>

              <DialogFooter>
                <Button 
                  onClick={() => {
                    setNewKey(null)
                    setShowCreateDialog(false)
                  }}
                  className="w-full"
                >
                  Done
                </Button>
              </DialogFooter>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Documentation */}
      <Card>
        <CardHeader>
          <CardTitle>API Documentation</CardTitle>
          <CardDescription>How to use your API keys to integrate with VerifAi</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Authentication</h4>
            <p className="text-sm text-gray-600 mb-2">
              Include your API key in the request header:
            </p>
            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg text-xs overflow-x-auto">
{`X-API-Key: your_api_key_here
# or
Authorization: Bearer your_api_key_here`}
            </pre>
          </div>

          <div>
            <h4 className="font-medium text-gray-900 mb-2">Generate Verification Link</h4>
            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg text-xs overflow-x-auto">
{`POST ${API_BASE_URL}/api/v1/generate-verification
Content-Type: application/json
X-API-Key: your_api_key_here

{
  "fullName": "John Doe",
  "email": "john@example.com",
  "address": "123 Main Street",
  "city": "New York",
  "state": "NY",
  "zipCode": "10001"
}`}
            </pre>
          </div>

          <div>
            <h4 className="font-medium text-gray-900 mb-2">Get Verification Status</h4>
            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg text-xs overflow-x-auto">
{`GET ${API_BASE_URL}/api/v1/verifications/{verification_id}
X-API-Key: your_api_key_here`}
            </pre>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default ApiKeys
