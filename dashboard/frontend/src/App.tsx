import React, { Suspense } from 'react'
import { Routes, Route } from 'react-router-dom'
import { Box, Text, Spinner } from '@chakra-ui/react'

// Error Boundary Component
class ErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback?: string },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode; fallback?: string }) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error Boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box p={8} bg="red.50" border="1px" borderColor="red.200" borderRadius="md">
          <h1 style={{ color: 'red', marginBottom: '16px' }}>
            {this.props.fallback || 'Something went wrong'}
          </h1>
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

// Lazy load components with error boundaries
const LazyDashboard = React.lazy(() => import('./pages/Dashboard').catch(err => {
  console.error('Failed to load Dashboard:', err)
  return { default: () => <Text color="red.500">Failed to load Dashboard</Text> }
}))

const LazyTesting = React.lazy(() => import('./pages/Testing').catch(err => {
  console.error('Failed to load Testing:', err)
  return { default: () => <Text color="red.500">Failed to load Testing</Text> }
}))

const LazyWorkflows = React.lazy(() => import('./pages/Workflows').catch(err => {
  console.error('Failed to load Workflows:', err)
  return { default: () => <Text color="red.500">Failed to load Workflows</Text> }
}))

const LazyResearch = React.lazy(() => import('./pages/Research').catch(err => {
  console.error('Failed to load Research:', err)
  return { default: () => <Text color="red.500">Failed to load Research</Text> }
}))

const LazyMonitoring = React.lazy(() => import('./pages/Monitoring').catch(err => {
  console.error('Failed to load Monitoring:', err)
  return { default: () => <Text color="red.500">Failed to load Monitoring</Text> }
}))

const LazyLayout = React.lazy(() => import('./components/Layout').catch(err => {
  console.error('Failed to load Layout:', err)
  return { default: ({ children }: { children: React.ReactNode }) => <Box>{children}</Box> }
}))

// Loading component
const LoadingSpinner = () => (
  <Box display="flex" justifyContent="center" alignItems="center" height="200px">
    <Spinner size="xl" color="blue.500" />
  </Box>
)

function App() {
  console.log('App component rendering')
  
  return (
    <ErrorBoundary fallback="App crashed">
      <Box minHeight="100vh" bg="gray.50">
        <Suspense fallback={<LoadingSpinner />}>
          <ErrorBoundary fallback="Layout failed to load">
            <LazyLayout>
              <Routes>
                <Route path="/" element={
                  <Suspense fallback={<LoadingSpinner />}>
                    <ErrorBoundary fallback="Dashboard failed to load">
                      <LazyDashboard />
                    </ErrorBoundary>
                  </Suspense>
                } />
                <Route path="/testing" element={
                  <Suspense fallback={<LoadingSpinner />}>
                    <ErrorBoundary fallback="Testing failed to load">
                      <LazyTesting />
                    </ErrorBoundary>
                  </Suspense>
                } />
                <Route path="/workflows" element={
                  <Suspense fallback={<LoadingSpinner />}>
                    <ErrorBoundary fallback="Workflows failed to load">
                      <LazyWorkflows />
                    </ErrorBoundary>
                  </Suspense>
                } />
                <Route path="/research" element={
                  <Suspense fallback={<LoadingSpinner />}>
                    <ErrorBoundary fallback="Research failed to load">
                      <LazyResearch />
                    </ErrorBoundary>
                  </Suspense>
                } />
                <Route path="/monitoring" element={
                  <Suspense fallback={<LoadingSpinner />}>
                    <ErrorBoundary fallback="Monitoring failed to load">
                      <LazyMonitoring />
                    </ErrorBoundary>
                  </Suspense>
                } />
              </Routes>
            </LazyLayout>
          </ErrorBoundary>
        </Suspense>
      </Box>
    </ErrorBoundary>
  )
}

export default App
