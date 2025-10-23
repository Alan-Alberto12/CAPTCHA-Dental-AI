import { useState } from 'react'
import SignUp from './pages/SignUp'
import Dashboard from './pages/Dashboard'
import Play from './pages/Play'
import Leaderboard from './pages/Leaderboard'


function App() {
  const [count, setCount] = useState(0)

  return (
    <div>
      <SignUp/>
    </div>
  )
}

export default App
