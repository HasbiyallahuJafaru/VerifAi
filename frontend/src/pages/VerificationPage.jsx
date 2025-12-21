import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { CheckCircle2, XCircle, Loader2 } from 'lucide-react'
import { API_BASE_URL } from '../config'

// This would come from URL parameters in production
const ORGANIZATION_NAME = 'ABC Bank'

function VerificationPage() {
  const [status, setStatus] = useState('pending') // pending, processing, success, denied, error
  const [verificationResult, setVerificationResult] = useState(null)
  const [errorMessage, setErrorMessage] = useState(null)

  const handleConsent = async (consented) => {
    if (!consented) {
      setStatus('denied')
      return
    }

    setStatus('processing')
    setErrorMessage(null)

    // Check if geolocation is supported
    if (!navigator.geolocation) {
      setErrorMessage('Geolocation is not supported by your browser')
      setStatus('error')
      return
    }

    // Get user's location
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const location = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy
          }

          // In a real implementation, you would get these from URL parameters
          // or a session that was initiated by the organization
          const verificationData = {
            fullName: 'User Name', // Would come from organization's request
            email: 'user@example.com', // Would come from organization's request
            address: '123 Main Street', // Would come from organization's request
            city: 'New York',
            state: 'NY',
            zipCode: '10001',
            consent: true,
            location: location
          }

          const response = await fetch(`${API_BASE_URL}/api/submit-verification`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(verificationData)
          })

          const data = await response.json()

          if (!response.ok) {
            throw new Error(data.error || 'Verification failed')
          }

          setVerificationResult(data)
          setStatus('success')
        } catch (error) {
          setErrorMessage(error.message)
          setStatus('error')
        }
      },
      (error) => {
        setErrorMessage(`Location access denied: ${error.message}`)
        setStatus('error')
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    )
  }

  const resetVerification = () => {
    setStatus('pending')
    setVerificationResult(null)
    setErrorMessage(null)
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Address Verification</h2>
        <p className="text-gray-600 mt-1">Verify user addresses with location-based confirmation</p>
      </div>

      <div className="max-w-lg mx-auto">
        {/* Pending - Show Consent Request */}
        {status === 'pending' && (
          <Card className="shadow-lg">
            <CardHeader className="text-center">
              <div className="mx-auto mb-4 w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <CardTitle className="text-2xl">Address Verification Request</CardTitle>
              <CardDescription className="text-base mt-2">
                {ORGANIZATION_NAME} wants to verify your address
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-gray-700 leading-relaxed">
                  <strong>{ORGANIZATION_NAME}</strong> is requesting to verify your current location to confirm your address. 
                  This process will:
                </p>
                <ul className="mt-3 space-y-2 text-sm text-gray-600">
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Access your device's location (GPS)</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Compare your location with your registered address</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Share verification results with {ORGANIZATION_NAME}</span>
                  </li>
                </ul>
              </div>

              <div className="text-center">
                <p className="text-sm font-medium text-gray-900 mb-4">
                  Do you consent to the use of your location data for address verification?
                </p>
                <div className="flex gap-3">
                  <Button
                    onClick={() => handleConsent(false)}
                    variant="outline"
                    className="flex-1 h-12 text-base"
                  >
                    No, Decline
                  </Button>
                  <Button
                    onClick={() => handleConsent(true)}
                    className="flex-1 h-12 text-base bg-blue-600 hover:bg-blue-700"
                  >
                    Yes, I Consent
                  </Button>
                </div>
              </div>

              <p className="text-xs text-gray-500 text-center">
                Your location data will only be used for this verification and will be handled according to our privacy policy.
              </p>
            </CardContent>
          </Card>
        )}

        {/* Processing - Show Loading */}
        {status === 'processing' && (
          <Card className="shadow-lg">
            <CardContent className="py-12">
              <div className="text-center space-y-4">
                <Loader2 className="w-16 h-16 mx-auto text-blue-600 animate-spin" />
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">Verifying Your Location</h3>
                  <p className="text-gray-600 mt-2">Please wait while we verify your address...</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Success - Show Results */}
        {status === 'success' && verificationResult && (
          <Card className="shadow-lg">
            <CardContent className="py-8">
              <div className="text-center space-y-4">
                <CheckCircle2 className="w-16 h-16 mx-auto text-green-600" />
                <div>
                  <h3 className="text-2xl font-semibold text-gray-900">Verification Complete</h3>
                  <p className="text-gray-600 mt-2">{verificationResult.message}</p>
                </div>

                <Alert className={verificationResult.location_verified ? 'border-green-200 bg-green-50' : 'border-yellow-200 bg-yellow-50'}>
                  <AlertDescription>
                    <div className="space-y-2 text-sm">
                      <p><strong>Status:</strong> {verificationResult.status.replace('_', ' ').toUpperCase()}</p>
                      <p><strong>Verification ID:</strong> {verificationResult.verification_id}</p>
                      {verificationResult.distance_from_address !== null && (
                        <p><strong>Distance from Address:</strong> {Math.round(verificationResult.distance_from_address)}m</p>
                      )}
                      <p><strong>Risk Score:</strong> {(verificationResult.risk_score * 100).toFixed(0)}%</p>
                    </div>
                  </AlertDescription>
                </Alert>

                <div className="pt-4">
                  <p className="text-sm text-gray-600 mb-4">
                    {ORGANIZATION_NAME} has been notified of your verification results.
                  </p>
                  <Button onClick={resetVerification} variant="outline" className="w-full">
                    New Verification
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Denied - User Declined */}
        {status === 'denied' && (
          <Card className="shadow-lg">
            <CardContent className="py-8">
              <div className="text-center space-y-4">
                <XCircle className="w-16 h-16 mx-auto text-gray-400" />
                <div>
                  <h3 className="text-2xl font-semibold text-gray-900">Verification Declined</h3>
                  <p className="text-gray-600 mt-2">
                    You have declined the address verification request.
                  </p>
                </div>

                <Alert className="border-gray-200 bg-gray-50">
                  <AlertDescription className="text-sm text-gray-700">
                    {ORGANIZATION_NAME} has been notified that you declined the verification request. 
                    You may need to complete verification through an alternative method.
                  </AlertDescription>
                </Alert>

                <div className="pt-4 space-y-3">
                  <Button onClick={resetVerification} className="w-full">
                    Try Again
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Error - Something Went Wrong */}
        {status === 'error' && (
          <Card className="shadow-lg">
            <CardContent className="py-8">
              <div className="text-center space-y-4">
                <XCircle className="w-16 h-16 mx-auto text-red-600" />
                <div>
                  <h3 className="text-2xl font-semibold text-gray-900">Verification Failed</h3>
                  <p className="text-gray-600 mt-2">
                    We encountered an error during verification.
                  </p>
                </div>

                {errorMessage && (
                  <Alert variant="destructive">
                    <AlertDescription>{errorMessage}</AlertDescription>
                  </Alert>
                )}

                <div className="pt-4 space-y-3">
                  <Button onClick={resetVerification} className="w-full">
                    Try Again
                  </Button>
                  <p className="text-xs text-gray-500">
                    If the problem persists, please contact {ORGANIZATION_NAME} for assistance.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

export default VerificationPage
