import { useState } from 'react'
import { useAuth0 } from '@auth0/auth0-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { CheckCircle2, Copy, ExternalLink, Loader2 } from 'lucide-react'
import { API_BASE_URL } from '../config'

function GenerateLink() {
  const { getAccessTokenSilently } = useAuth0()
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    address: '',
    city: '',
    state: '',
    zipCode: '',
    organizationName: 'VerifAi'
  })
  const [isLoading, setIsLoading] = useState(false)
  const [generatedLink, setGeneratedLink] = useState(null)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)
    setGeneratedLink(null)

    try {
      const token = await getAccessTokenSilently()
      const response = await fetch(`${API_BASE_URL}/api/generate-verification-link`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate link')
      }

      setGeneratedLink(data)
      // Reset form
      setFormData({
        fullName: '',
        email: '',
        address: '',
        city: '',
        state: '',
        zipCode: '',
        organizationName: 'VerifAi'
      })
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  const copyToClipboard = () => {
    if (generatedLink?.verificationUrl) {
      navigator.clipboard.writeText(generatedLink.verificationUrl)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const openLink = () => {
    if (generatedLink?.verificationUrl) {
      window.open(generatedLink.verificationUrl, '_blank')
    }
  }

  return (
    <div className="space-y-6 text-slate-50">
      <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/15 shadow-lg">
        <h2 className="text-2xl font-bold text-white">Generate Verification Link</h2>
        <p className="text-slate-200 mt-1">Create a secure, personalized verification link for a customer</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form */}
        <Card className="shadow-xl">
          <CardHeader>
            <CardTitle>Customer Information</CardTitle>
            <CardDescription>Enter the customer's details to generate their unique verification link</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="fullName">Full Name *</Label>
                <Input
                  id="fullName"
                  name="fullName"
                  value={formData.fullName}
                  onChange={handleChange}
                  required
                  placeholder="John Doe"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email Address *</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  placeholder="john@example.com"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="address">Street Address *</Label>
                <Input
                  id="address"
                  name="address"
                  value={formData.address}
                  onChange={handleChange}
                  required
                  placeholder="123 Main Street"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="city">City *</Label>
                  <Input
                    id="city"
                    name="city"
                    value={formData.city}
                    onChange={handleChange}
                    required
                    placeholder="New York"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="state">State *</Label>
                  <Input
                    id="state"
                    name="state"
                    value={formData.state}
                    onChange={handleChange}
                    required
                    placeholder="NY"
                    maxLength={2}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="zipCode">ZIP Code *</Label>
                <Input
                  id="zipCode"
                  name="zipCode"
                  value={formData.zipCode}
                  onChange={handleChange}
                  required
                  placeholder="10001"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="organizationName">Organization Name</Label>
                <Input
                  id="organizationName"
                  name="organizationName"
                  value={formData.organizationName}
                  onChange={handleChange}
                  placeholder="Your Organization"
                />
              </div>

              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <Button 
                type="submit" 
                className="w-full bg-blue-600 hover:bg-blue-700"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  'Generate Verification Link'
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Generated Link Display */}
        <Card className="shadow-xl">
          <CardHeader>
            <CardTitle>Generated Link</CardTitle>
            <CardDescription>Share this unique link with your customer</CardDescription>
          </CardHeader>
          <CardContent>
            {generatedLink ? (
              <div className="space-y-4">
                <Alert className="border-green-200 bg-green-50">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-900">
                    Verification link generated successfully!
                  </AlertDescription>
                </Alert>

                <div className="space-y-2">
                  <Label>Verification URL</Label>
                  <div className="flex gap-2">
                    <Input
                      value={generatedLink.verificationUrl}
                      readOnly
                      className="font-mono text-sm"
                    />
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={copyToClipboard}
                      title="Copy to clipboard"
                    >
                      {copied ? (
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                      ) : (
                        <Copy className="h-4 w-4" />
                      )}
                    </Button>
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={openLink}
                      title="Open in new tab"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                  <h4 className="font-medium text-gray-900">Link Details</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Recipient:</span>
                      <span className="font-medium">{generatedLink.recipient.name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Email:</span>
                      <span className="font-medium">{generatedLink.recipient.email}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Expires:</span>
                      <span className="font-medium">{generatedLink.expiresIn}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Token ID:</span>
                      <span className="font-mono text-xs">{generatedLink.tokenId.substring(0, 16)}...</span>
                    </div>
                  </div>
                </div>

                <Alert className="border-blue-200 bg-blue-50">
                  <AlertDescription className="text-sm text-blue-900">
                    <strong>Security:</strong> This link is unique and can only be used once. 
                    It will expire in {generatedLink.expiresIn}. Do not share publicly.
                  </AlertDescription>
                </Alert>
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <ExternalLink className="w-8 h-8 text-gray-400" />
                </div>
                <p className="text-gray-500">
                  Fill out the form to generate a verification link
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Instructions */}
      <Card>
        <CardHeader>
          <CardTitle>How It Works</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mb-3">
                <span className="text-blue-600 font-bold">1</span>
              </div>
              <h4 className="font-medium text-gray-900 mb-2">Generate Link</h4>
              <p className="text-sm text-gray-600">
                Enter customer information to create a unique, secure verification link tailored to their address.
              </p>
            </div>
            <div>
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mb-3">
                <span className="text-blue-600 font-bold">2</span>
              </div>
              <h4 className="font-medium text-gray-900 mb-2">Send to Customer</h4>
              <p className="text-sm text-gray-600">
                Share the link via email or SMS. The link contains encrypted customer data and is single-use only.
              </p>
            </div>
            <div>
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mb-3">
                <span className="text-blue-600 font-bold">3</span>
              </div>
              <h4 className="font-medium text-gray-900 mb-2">Verify Location</h4>
              <p className="text-sm text-gray-600">
                Customer clicks the link, grants location permission, and their GPS coordinates verify their address.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default GenerateLink
