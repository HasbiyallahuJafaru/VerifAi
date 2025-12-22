import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ShieldCheck, Loader2 } from 'lucide-react'
import { API_BASE_URL } from '../config'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const persistSession = (data) => {
    localStorage.setItem('isAuthenticated', 'true')
    localStorage.setItem('userEmail', data?.user?.email || email)
    if (data?.access_token) {
      localStorage.setItem('accessToken', data.access_token)
    }
    if (data?.refresh_token) {
      localStorage.setItem('refreshToken', data.refresh_token)
    }
  }

  const apiCall = async (path, body) => {
    const res = await fetch(`${API_BASE_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(body)
    })
    const data = await res.json().catch(() => ({}))
    if (!res.ok) {
      throw new Error(data.error || 'Authentication failed')
    }
    return data
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      // Try login first; if credentials are new, create user then login
      let authData
      try {
        authData = await apiCall('/api/auth/login', { email, password })
      } catch (loginErr) {
        // Attempt signup for first-time user, then login
        await apiCall('/api/auth/signup', { email, password })
        authData = await apiCall('/api/auth/login', { email, password })
      }

      persistSession(authData)
      navigate('/dashboard')
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4">
      <Card className="w-full max-w-md shadow-xl">
        <CardHeader className="text-center space-y-4">
          <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
            <ShieldCheck className="w-10 h-10 text-blue-600" />
          </div>
          <CardTitle className="text-3xl font-bold">VerifAi</CardTitle>
          <CardDescription className="text-base">
            Sign in to access the verification dashboard
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="admin@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={isLoading}
              />
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <Button 
              type="submit" 
              className="w-full h-11 bg-blue-600 hover:bg-blue-700"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Demo credentials: any email and password
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Login
