import { useAuth0 } from '@auth0/auth0-react'

export const useAuthToken = () => {
  const { getAccessTokenSilently } = useAuth0()

  const getToken = async () => {
    try {
      const token = await getAccessTokenSilently()
      return token
    } catch (error) {
      console.error('Error getting access token:', error)
      return null
    }
  }

  return { getToken }
}
