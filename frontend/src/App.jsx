import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Dashboard from './layouts/Dashboard'
import Overview from './pages/Overview'
import GenerateLink from './pages/GenerateLink'
import Verifications from './pages/Verifications'
import PublicVerification from './pages/PublicVerification'
import ApiKeys from './pages/ApiKeys'
import Analytics from './pages/Analytics'
import Settings from './pages/Settings'
import ProtectedRoute from './components/ProtectedRoute'
import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/verify" element={<PublicVerification />} />

        {/* Protected Routes */}
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        >
          <Route index element={<Overview />} />
          <Route path="generate-link" element={<GenerateLink />} />
          <Route path="verifications" element={<Verifications />} />
          <Route path="api-keys" element={<ApiKeys />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="settings" element={<Settings />} />
        </Route>

        {/* Redirect root to login or dashboard based on auth */}
        <Route 
          path="/" 
          element={
            localStorage.getItem('isAuthenticated') === 'true' 
              ? <Navigate to="/dashboard" replace /> 
              : <Navigate to="/login" replace />
          } 
        />

        {/* Catch all - redirect to login */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  )
}

export default App
