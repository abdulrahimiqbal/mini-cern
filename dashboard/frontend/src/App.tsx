import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Box } from '@chakra-ui/react'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Testing from './pages/Testing'
import Workflows from './pages/Workflows'
import Monitoring from './pages/Monitoring'

// Error Boundary Component
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('App Error Boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box p={8} bg="red.50" border="1px" borderColor="red.200" borderRadius="md">
          <h1 style={{ color: 'red', marginBottom: '16px' }}>Something went wrong</h1>
          <details style={{ color: 'red' }}>
            <summary>Error Details</summary>
            <pre>{this.state.error?.stack}</pre>
          </details>
        </Box>
      )
    }

    return this.props.children
  }
}

function App() {
  console.log('App component rendering')
  
  return (
    <ErrorBoundary>
      <Box minHeight="100vh" bg="gray.50">
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/testing" element={<Testing />} />
            <Route path="/workflows" element={<Workflows />} />
            <Route path="/monitoring" element={<Monitoring />} />
          </Routes>
        </Layout>
      </Box>
    </ErrorBoundary>
  )
}

export default App
