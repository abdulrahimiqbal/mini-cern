import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Box, Text } from '@chakra-ui/react'

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

// Simple test components
const Dashboard = () => (
  <Box p={8}>
    <Text fontSize="2xl" fontWeight="bold" color="blue.600">
      Dashboard Working!
    </Text>
    <Text>Mini CERN Science Research Institute</Text>
  </Box>
)

const Testing = () => (
  <Box p={8}>
    <Text fontSize="2xl" fontWeight="bold" color="green.600">
      Testing Page Working!
    </Text>
  </Box>
)

function App() {
  console.log('App component rendering')
  
  return (
    <ErrorBoundary>
      <Box minHeight="100vh" bg="gray.50">
        <Box p={4} bg="blue.600" color="white">
          <Text fontSize="xl" fontWeight="bold">Mini CERN Dashboard</Text>
        </Box>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/testing" element={<Testing />} />
        </Routes>
      </Box>
    </ErrorBoundary>
  )
}

export default App
