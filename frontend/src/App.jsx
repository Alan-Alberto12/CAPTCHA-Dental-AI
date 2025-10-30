import { useState } from 'react'
import Login from './pages/Login'
import SignUp from './pages/SignUp'
import Dashboard from './pages/Dashboard'
import Play from './pages/PlayPage'
import Leaderboard from './pages/Leaderboard'


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
  <div>
    {renderPage()}
  </div>
  )
}

export default App