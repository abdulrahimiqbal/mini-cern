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

const Monitoring: React.FC = () => {
  const [overview, setOverview] = useState<SystemOverview | null>(null)
  const [agentStatus, setAgentStatus] = useState<any>(null)
  const [safetyStatus, setSafetyStatus] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const loadMonitoringData = async () => {
    try {
      const [overviewData, agentsData, safetyData] = await Promise.all([
        apiService.getSystemOverview(),
        apiService.getAgents(),
        apiService.getSafetyStatus()
      ])
      
      setOverview(overviewData)
      setAgentStatus(agentsData)
      setSafetyStatus(safetyData)
    } catch (error) {
      console.error('Failed to load monitoring data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadMonitoringData()

    const handleSystemUpdate = (event: WebSocketEvent) => {
      if (event.type === 'system_metrics' || event.type === 'component_status') {
        loadMonitoringData()
      }
    }

    websocketService.subscribe('system_metrics', handleSystemUpdate)
    websocketService.subscribe('component_status', handleSystemUpdate)

    const interval = setInterval(loadMonitoringData, 10000)

    return () => {
      clearInterval(interval)
      websocketService.unsubscribe('system_metrics', handleSystemUpdate)
      websocketService.unsubscribe('component_status', handleSystemUpdate)
    }
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'green'
      case 'warning': return 'yellow'
      case 'error': return 'red'
      case 'offline': return 'gray'
      default: return 'gray'
    }
  }

  if (loading) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" color="blue.500" />
        <Text mt={4}>Loading monitoring data...</Text>
      </Box>
    )
  }

  return (
    <Box>
      <Box mb={6}>
        <Heading size="lg" mb={2}>System Monitoring</Heading>
        <Text color="gray.600">
          Detailed monitoring of all system components and performance metrics
        </Text>
      </Box>

      {/* Real-time Metrics */}
      {overview && (
        <Box bg="white" p={5} borderRadius="md" shadow="sm" border="1px" borderColor="gray.200" mb={6}>
          <Heading size="md" mb={4}>Real-time Performance</Heading>
          <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(4, 1fr)' }} gap={4}>
            <Box textAlign="center" p={4} bg="gray.50" borderRadius="md">
              <Text fontSize="xs" color="gray.500" mb={1}>CPU USAGE</Text>
              <Text fontSize="2xl" fontWeight="bold" color={overview.metrics.cpu_percent > 80 ? 'red.500' : 'green.500'}>
                {overview.metrics.cpu_percent.toFixed(1)}%
              </Text>
              <Box mt={2} bg="gray.200" borderRadius="md" h={1}>
                <Box 
                  bg={overview.metrics.cpu_percent > 80 ? 'red.500' : 'green.500'}
                  h="100%" 
                  borderRadius="md"
                  width={`${overview.metrics.cpu_percent}%`}
                />
              </Box>
            </Box>

            <Box textAlign="center" p={4} bg="gray.50" borderRadius="md">
              <Text fontSize="xs" color="gray.500" mb={1}>MEMORY USAGE</Text>
              <Text fontSize="2xl" fontWeight="bold" color={overview.metrics.memory_percent > 90 ? 'red.500' : 'blue.500'}>
                {overview.metrics.memory_percent.toFixed(1)}%
              </Text>
              <Box mt={2} bg="gray.200" borderRadius="md" h={1}>
                <Box 
                  bg={overview.metrics.memory_percent > 90 ? 'red.500' : 'blue.500'}
                  h="100%" 
                  borderRadius="md"
                  width={`${overview.metrics.memory_percent}%`}
                />
              </Box>
            </Box>

            <Box textAlign="center" p={4} bg="gray.50" borderRadius="md">
              <Text fontSize="xs" color="gray.500" mb={1}>RESPONSE TIME</Text>
              <Text fontSize="2xl" fontWeight="bold" color="purple.500">
                {overview.metrics.response_time_ms}ms
              </Text>
              <Text fontSize="xs" color="gray.500" mt={1}>
                {overview.metrics.response_time_ms < 100 ? 'Excellent' : 'Good'}
              </Text>
            </Box>

            <Box textAlign="center" p={4} bg="gray.50" borderRadius="md">
              <Text fontSize="xs" color="gray.500" mb={1}>ACTIVE AGENTS</Text>
              <Text fontSize="2xl" fontWeight="bold" color="green.500">
                {overview.metrics.active_agents}
              </Text>
              <Text fontSize="xs" color="gray.500" mt={1}>
                All operational
              </Text>
            </Box>
          </Grid>
        </Box>
      )}

      {/* Component Health Details */}
      {overview && (
        <Box bg="white" p={5} borderRadius="md" shadow="sm" border="1px" borderColor="gray.200" mb={6}>
          <Heading size="md" mb={4}>Component Health Status</Heading>
          <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={4}>
            {overview.components.map((component: ComponentStatus) => (
              <Box
                key={component.name}
                p={4}
                bg="gray.50"
                borderRadius="md"
                borderLeft="4px"
                borderColor={`${getStatusColor(component.status)}.500`}
              >
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Text fontWeight="medium" textTransform="capitalize">
                    {component.name.replace('_', ' ')}
                  </Text>
                  <Badge colorScheme={getStatusColor(component.status)}>
                    {component.status}
                  </Badge>
                </Box>
                
                <Box mb={2}>
                  <Text fontSize="sm" color="gray.600">
                    Performance: {component.performance}%
                  </Text>
                  <Box bg="gray.200" borderRadius="md" h={1} mt={1}>
                    <Box 
                      bg={`${getStatusColor(component.status)}.500`}
                      h="100%" 
                      borderRadius="md"
                      width={`${component.performance}%`}
                    />
                  </Box>
                </Box>

                <Text fontSize="xs" color="gray.500">
                  Last Check: {new Date(component.last_check).toLocaleTimeString()}
                </Text>
                
                {component.details && (
                  <Text fontSize="xs" color="gray.600" mt={1}>
                    {component.details}
                  </Text>
                )}
              </Box>
            ))}
          </Grid>
        </Box>
      )}

      {/* Agent Status */}
      <Grid templateColumns={{ base: '1fr', lg: 'repeat(2, 1fr)' }} gap={6}>
        <Box bg="white" p={5} borderRadius="md" shadow="sm" border="1px" borderColor="gray.200">
          <Heading size="md" mb={4}>Agent Registry Status</Heading>
          {agentStatus ? (
            <Box>
              <Text fontSize="sm" color="gray.600" mb={2}>
                Status: {agentStatus.success ? 'Operational' : 'Error'}
              </Text>
              {agentStatus.data && (
                <Box>
                  <Text fontSize="sm">
                    Message: {agentStatus.data.message || agentStatus.message}
                  </Text>
                  {agentStatus.data.active_agents && (
                    <Text fontSize="sm" color="green.600">
                      Active Agents: {agentStatus.data.active_agents}
                    </Text>
                  )}
                </Box>
              )}
            </Box>
          ) : (
            <Text color="gray.500">Loading agent status...</Text>
          )}
        </Box>

        <Box bg="white" p={5} borderRadius="md" shadow="sm" border="1px" borderColor="gray.200">
          <Heading size="md" mb={4}>Safety Monitor Status</Heading>
          {safetyStatus ? (
            <Box>
              <Text fontSize="sm" color="gray.600" mb={2}>
                Status: {safetyStatus.success ? 'Operational' : 'Error'}
              </Text>
              {safetyStatus.data && (
                <Box>
                  <Text fontSize="sm">
                    Message: {safetyStatus.data.message || safetyStatus.message}
                  </Text>
                  {safetyStatus.data.violations && (
                    <Text fontSize="sm" color={safetyStatus.data.violations > 0 ? 'red.600' : 'green.600'}>
                      Violations: {safetyStatus.data.violations}
                    </Text>
                  )}
                </Box>
              )}
            </Box>
          ) : (
            <Text color="gray.500">Loading safety status...</Text>
          )}
        </Box>
      </Grid>
    </Box>
  )
}

export default Monitoring 