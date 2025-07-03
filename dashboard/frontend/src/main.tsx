import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ChakraProvider } from '@chakra-ui/react'
import App from './App.tsx'
import './index.css'

console.log('Main.tsx loading...')

// Add global error handler
window.addEventListener('error', (event) => {
  console.error('Global Error:', event.error)
})

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled Promise Rejection:', event.reason)
})

try {
  const rootElement = document.getElementById('root')
  console.log('Root element found:', rootElement)
  
  if (!rootElement) {
    throw new Error('Root element not found')
  }

  const root = ReactDOM.createRoot(rootElement)
  console.log('React root created')

  root.render(
    <React.StrictMode>
      <ChakraProvider>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </ChakraProvider>
    </React.StrictMode>,
  )
  
  console.log('React app rendered')
} catch (error) {
  console.error('Failed to render app:', error)
  // Fallback display
  document.body.innerHTML = `
    <div style="padding: 20px; color: red; font-family: Arial;">
      <h1>Application Error</h1>
      <p>Failed to load the application. Please check the browser console for details.</p>
      <pre>${error}</pre>
    </div>
  `
}
