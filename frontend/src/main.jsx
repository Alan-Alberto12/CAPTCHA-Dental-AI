import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// to run docker
// docker compose up -d
// then go to http://localhost:5173 for frontend
// http://localhost:8000/health for API
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
    <h1 className="font-bold text-blue-400">if this text is blue, tailwind works :D</h1>
  </StrictMode>,
)
