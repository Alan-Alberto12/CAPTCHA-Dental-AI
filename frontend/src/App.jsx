import { useState } from 'react'
import Login from './pages/Login'
import SignUp from './pages/SignUp'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Play from './pages/Play'
import Leaderboard from './pages/Leaderboard'
import AdminPage from './pages/AdminPage'
import ProtectedLayout from './layouts/ProtectedLayout'

function App() {
  const [currentPage, setCurrentPage] = useState('login')

  const renderPage = () => {
    switch(currentPage) {
      case 'login':
        return <Login onNavigateToSignUp={() => setCurrentPage('signup')} />
      case 'signup':
        return <SignUp onNavigateToLogin={() => setCurrentPage('login')} />
      case 'dashboard':
        return <Dashboard />
      case 'play':
        return <Play />
      case 'leaderboard':
        return <Leaderboard />
      default:
        return <Login onNavigateToSignUp={() => setCurrentPage('signup')} />
    }
  }

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<SignUp />} />
      <Route element={<ProtectedLayout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/play" element={<Play />} />
        <Route path="/leaderboard" element={<Leaderboard />} />
      </Route>
      <Route path="/" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

export default App