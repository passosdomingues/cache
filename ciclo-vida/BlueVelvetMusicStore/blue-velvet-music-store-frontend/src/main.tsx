/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025-12-08
 * @brief Application entry point.
 * @us US-0000 Project Configuration - Granularity: Entry Point
 */
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import { ThemeProvider } from './context/ThemeContext.tsx'
import './styles/variables.css'
// import './index.css' // Removed default vite css if we want full control, or let's keep it and override

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider>
      <App />
    </ThemeProvider>
  </React.StrictMode>,
)
