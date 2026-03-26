import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import SignUp from './pages/SignUp'
import Dashboard from './pages/Dashboard'
import Play from './pages/PlayPage'
import Leaderboard from './pages/Leaderboard'
import EditUser from './pages/EditUser'
import ProtectedLayout from './layouts/ProtectedLayout'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<SignUp />} />
      <Route element={<ProtectedLayout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/play" element={<Play />} />
        <Route path="/leaderboard" element={<Leaderboard />} />
      </Route>
      <Route path="/edit-user" element={<EditUser />} />
      <Route path="/" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

export default App
