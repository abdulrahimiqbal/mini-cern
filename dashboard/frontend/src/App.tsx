import { Routes, Route } from 'react-router-dom'
import { Box } from '@chakra-ui/react'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Testing from './pages/Testing'
import Workflows from './pages/Workflows'
import Monitoring from './pages/Monitoring'

function App() {
  return (
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
  )
}

export default App
