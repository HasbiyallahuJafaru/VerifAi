import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth0 } from '@auth0/auth0-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ShieldCheck, Loader2 } from 'lucide-react'

function Login() {
  const { loginWithRedirect, isAuthenticated, isLoading } = useAuth0()
  const navigate = useNavigate()

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard')
    }
  }, [isAuthenticated, navigate])

  const handleLogin = async () => {
    await loginWithRedirect({
      appState: { returnTo: '/dashboard' }
    })
  }

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 bg-cover bg-center bg-no-repeat" style={{backgroundImage: "url('https://images.unsplash.com/photo-1491156855053-9cdff72c7f85?q=80&w=1828&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D')"}}>
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
      <Card className="relative z-10 w-full max-w-md shadow-xl">
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
          <div className="space-y-4">
            <Button
              onClick={handleLogin}
              disabled={isLoading}
              className="w-full h-11 text-base font-medium"
              size="lg"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Loading...
                </>
              ) : (
                'Sign in with Auth0'
              )}
            </Button>
            <p className="text-center text-sm text-muted-foreground">
              Secure authentication powered by Auth0
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Login
