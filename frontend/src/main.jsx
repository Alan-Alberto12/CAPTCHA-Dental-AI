import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
    <h1 className="font-bold text-blue-400">does tailwind work?</h1>
  </StrictMode>,
)
