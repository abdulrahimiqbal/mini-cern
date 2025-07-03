import React, { useState, useEffect } from 'react'
import {
  Box,
  Grid,
  Heading,
  Text,
  Badge,
  Spinner,
} from '@chakra-ui/react'
import apiService from '../services/api'
import websocketService from '../services/websocket'
import type { SystemOverview, ComponentStatus, WebSocketEvent } from '../types'

const getStatusColor = (status: string) => {
  switch (status) {
    case 'healthy': return 'green'
    case 'warning': return 'yellow'
    case 'error': return 'red'
    case 'offline': return 'gray'
    default: return 'gray'
  }
}

const Dashboard: React.FC = () => {
  const [overview, setOverview] = useState<SystemOverview | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadSystemOverview = async () => {
    try {
      setLoading(true)
      const data = await apiService.getSystemOverview()
      setOverview(data)
      setError(null)
    } catch (err) {
      setError('Failed to load system overview')
      console.error('Error loading overview:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSystemOverview()

    const handleSystemUpdate = (event: WebSocketEvent) => {
      if (event.type === 'system_metrics' || event.type === 'component_status') {
        loadSystemOverview()
      }
    }

    websocketService.subscribe('system_metrics', handleSystemUpdate)
    websocketService.subscribe('component_status', handleSystemUpdate)

    const interval = setInterval(loadSystemOverview, 30000)

    return () => {
      clearInterval(interval)
      websocketService.unsubscribe('system_metrics', handleSystemUpdate)
      websocketService.unsubscribe('component_status', handleSystemUpdate)
    }
  }, [])

  if (loading && !overview) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" color="blue.500" />
        <Text mt={4}>Loading system overview...</Text>
      </Box>
    )
  }

  if (error) {
    return (
      <Box bg="red.50" border="1px" borderColor="red.200" borderRadius="md" p={4}>
        <Text color="red.800" fontWeight="bold">Error!</Text>
        <Text color="red.600">{error}</Text>
      </Box>
    )
  }

  if (!overview) {
    return (
      <Box bg="yellow.50" border="1px" borderColor="yellow.200" borderRadius="md" p={4}>
        <Text color="yellow.800" fontWeight="bold">No Data</Text>
        <Text color="yellow.600">Unable to load system overview</Text>
      </Box>
    )
  }

  // Defensive programming: ensure components array exists
  const components = overview.components || []
  const healthyComponents = components.filter(c => c.status === 'healthy').length
  const totalComponents = components.length

  // Defensive programming: ensure metrics exist
  const metrics = overview.metrics || {
    cpu_percent: 0,
    memory_percent: 0,
    disk_percent: 0,
    active_agents: 0,
    response_time_ms: 0
  }

  return (
    <Box>
      <Box mb={6}>
        <Heading size="lg" mb={2}>System Dashboard</Heading>
        <Text color="gray.600">
          Real-time overview of the Science Research Institute system
        </Text>
      </Box>

      {/* Key Metrics */}
      <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(4, 1fr)' }} gap={6} mb={6}>
        <Box bg="white" p={5} borderRadius="md" shadow="sm" border="1px" borderColor="gray.200">
          <Text fontSize="sm" color="gray.500" mb={2}>CPU Usage</Text>
          <Text fontSize="2xl" fontWeight="bold">{metrics.cpu_percent.toFixed(1)}%</Text>
          <Box mt={2} bg="gray.200" borderRadius="md" h={2}>
            <Box 
              bg={metrics.cpu_percent > 80 ? 'red.500' : 'green.500'}
              h="100%" 
              borderRadius="md"
              width={`${metrics.cpu_percent}%`}
            />
          </Box>
        </Box>

        <Box bg="white" p={5} borderRadius="md" shadow="sm" border="1px" borderColor="gray.200">
          <Text fontSize="sm" color="gray.500" mb={2}>Memory Usage</Text>
          <Text fontSize="2xl" fontWeight="bold">{metrics.memory_percent.toFixed(1)}%</Text>
          <Box mt={2} bg="gray.200" borderRadius="md" h={2}>
            <Box 
              bg={metrics.memory_percent > 90 ? 'red.500' : 'blue.500'}
              h="100%" 
              borderRadius="md"
              width={`${metrics.memory_percent}%`}
            />
          </Box>
        </Box>

        <Box bg="white" p={5} borderRadius="md" shadow="sm" border="1px" borderColor="gray.200">
          <Text fontSize="sm" color="gray.500" mb={2}>Active Agents</Text>
          <Text fontSize="2xl" fontWeight="bold">{metrics.active_agents}</Text>
          <Text fontSize="sm" color="green.500" mt={1}>All agents operational</Text>
        </Box>

        <Box bg="white" p={5} borderRadius="md" shadow="sm" border="1px" borderColor="gray.200">
          <Text fontSize="sm" color="gray.500" mb={2}>Response Time</Text>
          <Text fontSize="2xl" fontWeight="bold">{metrics.response_time_ms}ms</Text>
          <Text fontSize="sm" color="gray.500" mt={1}>Average response</Text>
        </Box>
      </Grid>

      {/* System Health */}
      <Grid templateColumns={{ base: '1fr', lg: 'repeat(2, 1fr)' }} gap={6} mb={6}>
        <Box bg="white" p={5} borderRadius="md" shadow="sm" border="1px" borderColor="gray.200">
          <Heading size="md" mb={4}>System Health</Heading>
          <Box>
            <Text mb={2}>Components:</Text>
            <Badge colorScheme={healthyComponents === totalComponents ? 'green' : 'yellow'}>
              {healthyComponents}/{totalComponents} Healthy
            </Badge>
            <Box mt={3} bg="gray.200" borderRadius="md" h={2}>
              <Box 
                bg={healthyComponents === totalComponents ? 'green.500' : 'yellow.500'}
                h="100%" 
                borderRadius="md"
                width={`${(healthyComponents / totalComponents) * 100}%`}
              />
            </Box>
          </Box>
        </Box>

        <Box bg="white" p={5} borderRadius="md" shadow="sm" border="1px" borderColor="gray.200">
          <Heading size="md" mb={4}>System Activity</Heading>
          <Box>
            <Box mb={2} display="flex" justifyContent="space-between">
              <Text>Active Workflows:</Text>
              <Badge colorScheme="blue">{overview.active_workflows}</Badge>
            </Box>
            <Box mb={2} display="flex" justifyContent="space-between">
              <Text>Tests Run:</Text>
              <Badge colorScheme="purple">{overview.total_tests_run}</Badge>
            </Box>
            <Box display="flex" justifyContent="space-between">
              <Text>Uptime:</Text>
              <Badge colorScheme="green">{overview.system_uptime}</Badge>
            </Box>
          </Box>
        </Box>
      </Grid>

      {/* Component Status */}
      <Box bg="white" p={5} borderRadius="md" shadow="sm" border="1px" borderColor="gray.200">
        <Heading size="md" mb={4}>Component Status</Heading>
        <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' }} gap={4}>
          {components.map((component: ComponentStatus) => (
            <Box
              key={component.name}
              p={4}
              bg="gray.50"
              borderRadius="md"
              borderLeft="4px"
              borderColor={`${getStatusColor(component.status)}.500`}
            >
              <Box display="flex" justifyContent="space-between" mb={2}>
                <Text fontWeight="medium" textTransform="capitalize">
                  {component.name.replace('_', ' ')}
                </Text>
                <Badge colorScheme={getStatusColor(component.status)}>
                  {component.status}
                </Badge>
              </Box>
              <Box bg="gray.200" borderRadius="md" h={1}>
                <Box 
                  bg={`${getStatusColor(component.status)}.500`}
                  h="100%" 
                  borderRadius="md"
                  width={`${component.performance}%`}
                />
              </Box>
              <Text fontSize="xs" color="gray.500" mt={1}>
                {component.performance}% performance
              </Text>
            </Box>
          ))}
        </Grid>
      </Box>
    </Box>
  )
}

export default Dashboard 