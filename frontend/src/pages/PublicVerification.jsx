import { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { CheckCircle2, XCircle, Loader2, AlertTriangle, ShieldCheck } from 'lucide-react'
import { API_BASE_URL } from '../config'

function PublicVerification() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token')
  
  const [status, setStatus] = useState('validating') // validating, pending, processing, success, denied, error, invalid
  const [verificationData, setVerificationData] = useState(null)
  const [verificationResult, setVerificationResult] = useState(null)
  const [errorMessage, setErrorMessage] = useState(null)

  // Validate token on mount
  useEffect(() => {
    if (!token) {
      setStatus('invalid')
      setErrorMessage('No verification token provided')
      return
    }

    validateToken(token)
  }, [token])

  const validateToken = async (token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/validate-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Invalid verification token')
      }

      // Token is valid, store the verification data
      setVerificationData(data.verification_data)
      setStatus('pending')
    } catch (error) {
      setErrorMessage(error.message)
      setStatus('invalid')
    }
  }

  const handleConsent = async (consented) => {
    if (!consented) {
      setStatus('denied')
      // Notify backend that user declined
      await notifyDeclined()
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

    // Get user's location with high accuracy
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const location = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            altitude: position.coords.altitude,
            altitudeAccuracy: position.coords.altitudeAccuracy,
            heading: position.coords.heading,
            speed: position.coords.speed,
            timestamp: position.timestamp
          }

          // Submit verification with token and location
          const response = await fetch(`${API_BASE_URL}/api/submit-verification`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              token: token,
              consent: true,
              location: location,
              userAgent: navigator.userAgent,
              screenResolution: `${window.screen.width}x${window.screen.height}`,
              timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
            })
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
        let errorMsg = 'Unable to access your location. '
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMsg += 'Please enable location permissions and try again.'
            break
          case error.POSITION_UNAVAILABLE:
            errorMsg += 'Location information is unavailable.'
            break
          case error.TIMEOUT:
            errorMsg += 'Location request timed out. Please try again.'
            break
          default:
            errorMsg += error.message
        }
        setErrorMessage(errorMsg)
        setStatus('error')
      },
      {
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 0
      }
    )
  }

  const notifyDeclined = async () => {
    try {
      await fetch(`${API_BASE_URL}/api/verification-declined`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token })
      })
    } catch (error) {
      console.error('Failed to notify declined:', error)
    }
  }

  const resetVerification = () => {
    setStatus('pending')
    setVerificationResult(null)
    setErrorMessage(null)
  }

  // Validating Token
  if (status === 'validating') {
    return (
      <div className="min-h-screen flex items-center justify-center py-12 px-4 bg-cover bg-center bg-no-repeat" style={{backgroundImage: "url('https://images.unsplash.com/photo-1491156855053-9cdff72c7f85?q=80&w=1828&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D')"}}>
        <div className="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
        <Card className="relative z-10 max-w-lg w-full shadow-lg">
          <CardContent className="py-12">
            <div className="text-center space-y-4">
              <Loader2 className="w-16 h-16 mx-auto text-blue-600 animate-spin" />
              <div>
                <h3 className="text-xl font-semibold text-gray-900">Validating Request</h3>
                <p className="text-gray-600 mt-2">Please wait while we verify your verification link...</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Invalid Token
  if (status === 'invalid') {
    return (
      <div className="min-h-screen flex items-center justify-center py-12 px-4 bg-cover bg-center bg-no-repeat" style={{backgroundImage: "url('https://images.unsplash.com/photo-1491156855053-9cdff72c7f85?q=80&w=1828&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D')"}}>
        <div className="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
        <Card className="relative z-10 max-w-lg w-full shadow-lg">
          <CardContent className="py-8">
            <div className="text-center space-y-4">
              <AlertTriangle className="w-16 h-16 mx-auto text-red-600" />
              <div>
                <h3 className="text-2xl font-semibold text-gray-900">Invalid Verification Link</h3>
                <p className="text-gray-600 mt-2">
                  This verification link is invalid, expired, or has already been used.
                </p>
              </div>

              {errorMessage && (
                <Alert variant="destructive">
                  <AlertDescription>{errorMessage}</AlertDescription>
                </Alert>
              )}

              <div className="pt-4 space-y-3">
                <p className="text-sm text-gray-600">
                  If you believe this is an error, please contact the organization that sent you this link.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 bg-cover bg-center bg-no-repeat" style={{backgroundImage: "url('https://images.unsplash.com/photo-1491156855053-9cdff72c7f85?q=80&w=1828&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D')"}}>
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
      <div className="relative z-10 max-w-lg w-full">
        {/* Pending - Show Consent Request */}
        {status === 'pending' && verificationData && (
          <Card className="shadow-lg">
            <CardHeader className="text-center">
              <div className="mx-auto mb-4 w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                <ShieldCheck className="w-10 h-10 text-blue-600" />
              </div>
              <CardTitle className="text-2xl">Address Verification Request</CardTitle>
              <CardDescription className="text-base mt-2">
                {verificationData.organizationName} wants to verify your address
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Personalized Information */}
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <p className="text-sm font-medium text-gray-900 mb-2">Verification Details:</p>
                <div className="space-y-1 text-sm text-gray-700">
                  <p><strong>Name:</strong> {verificationData.fullName}</p>
                  <p><strong>Email:</strong> {verificationData.email}</p>
                  <p><strong>Address to Verify:</strong></p>
                  <p className="pl-4">
                    {verificationData.address}<br />
                    {verificationData.city}, {verificationData.state} {verificationData.zipCode}
                  </p>
                </div>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-gray-700 leading-relaxed">
                  <strong>{verificationData.organizationName}</strong> is requesting to verify your current location to confirm you are at the address above. 
                  This process will:
                </p>
                <ul className="mt-3 space-y-2 text-sm text-gray-600">
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Access your device's precise GPS location</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Calculate the distance from your registered address</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Share verification results with {verificationData.organizationName}</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Collect device metadata for fraud prevention</span>
                  </li>
                </ul>
              </div>

              <Alert className="border-amber-200 bg-amber-50">
                <AlertDescription className="text-sm text-amber-900">
                  <strong>Security Note:</strong> This link is unique to you and can only be used once. 
                  Do not share this link with anyone else.
                </AlertDescription>
              </Alert>

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
                This link expires in {verificationData.expiresIn || '24 hours'}.
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
                  <p className="text-sm text-gray-500 mt-2">This may take a few moments</p>
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
                      {verificationResult.risk_score !== undefined && (
                        <p><strong>Risk Score:</strong> {(verificationResult.risk_score * 100).toFixed(0)}%</p>
                      )}
                    </div>
                  </AlertDescription>
                </Alert>

                <div className="pt-4">
                  <p className="text-sm text-gray-600 mb-4">
                    {verificationData?.organizationName} has been notified of your verification results.
                    You may now close this window.
                  </p>
                  <Button variant="outline" className="w-full" onClick={() => window.close()}>
                    Close Window
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
                    {verificationData?.organizationName} has been notified that you declined the verification request. 
                    You may need to complete verification through an alternative method.
                  </AlertDescription>
                </Alert>

                <div className="pt-4 space-y-3">
                  <Button onClick={resetVerification} className="w-full">
                    Change My Mind
                  </Button>
                  <Button variant="outline" className="w-full" onClick={() => window.close()}>
                    Close Window
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
                    If the problem persists, please contact {verificationData?.organizationName} for assistance.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Footer */}
        <div className="mt-6 text-center">
          <p className="text-xs text-gray-500">
            Secure • Private • Encrypted • Compliant
          </p>
        </div>
      </div>
    </div>
  )
}

export default PublicVerification
