import React, { useState, useEffect } from 'react'
import {
  Box,
  Grid,
  Heading,
  Text,
  Badge,
  Spinner,
  Button,
  VStack,
  Card,
  CardBody,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Progress,
  CardHeader,
  HStack,
} from '@chakra-ui/react'
import apiService from '../services/api'
import websocketService from '../services/websocket'
import type { SystemOverview, WebSocketEvent } from '../types'

const Monitoring: React.FC = () => {
  const [overview, setOverview] = useState<SystemOverview | null>(null)
  const [agentStatus, setAgentStatus] = useState<any>(null)
  const [safetyStatus, setSafetyStatus] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadMonitoringData = async () => {
    try {
      setLoading(true)
      const [overviewData, agentsData, safetyData] = await Promise.all([
        apiService.getSystemOverview(),
        apiService.getAgents(),
        apiService.getSafetyStatus()
      ])
      
      setOverview(overviewData)
      setAgentStatus(agentsData?.data || agentsData)
      setSafetyStatus(safetyData?.data || safetyData)
      setError(null)
    } catch (error) {
      setError('Failed to load monitoring data')
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

    // Auto-refresh every 10 seconds
    const interval = setInterval(loadMonitoringData, 10000)

    return () => {
      websocketService.unsubscribe('system_metrics', handleSystemUpdate)
      websocketService.unsubscribe('component_status', handleSystemUpdate)
      clearInterval(interval)
    }
  }, [])



  if (loading && !overview) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" color="blue.500" />
        <Text mt={4}>Loading monitoring data...</Text>
      </Box>
    )
  }

  if (error) {
    return (
      <Box bg="red.50" border="1px" borderColor="red.200" borderRadius="md" p={4}>
        <Text color="red.800" fontWeight="bold">Monitoring Error</Text>
        <Text color="red.600">{error}</Text>
        <Button mt={2} size="sm" onClick={loadMonitoringData}>Retry</Button>
      </Box>
    )
  }

  if (!overview) {
    return (
      <Box bg="yellow.50" border="1px" borderColor="yellow.200" borderRadius="md" p={4}>
        <Text color="yellow.800" fontWeight="bold">No Data</Text>
        <Text color="yellow.600">Unable to load monitoring data</Text>
      </Box>
    )
  }

  // Defensive programming: ensure metrics exist
  const metrics = overview.metrics || {
    cpu_percent: 0,
    memory_percent: 0,
    disk_percent: 0,
    active_agents: 0,
    response_time_ms: 0
  }



  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <Box>
          <Heading size="lg">System Monitoring</Heading>
          <Text color="gray.600">Real-time system performance and agent collaboration tracking</Text>
        </Box>

        {/* System Overview */}
        <Grid templateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={6}>
          <Card>
            <CardBody>
              <Stat>
                <StatLabel>CPU Usage</StatLabel>
                <StatNumber>{metrics.cpu_percent.toFixed(1)}%</StatNumber>
                <StatHelpText>
                  <Progress value={metrics.cpu_percent} colorScheme={metrics.cpu_percent > 80 ? 'red' : 'green'} size="sm" />
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Memory Usage</StatLabel>
                <StatNumber>{metrics.memory_percent.toFixed(1)}%</StatNumber>
                <StatHelpText>
                  <Progress value={metrics.memory_percent} colorScheme={metrics.memory_percent > 85 ? 'red' : 'green'} size="sm" />
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Active Agents</StatLabel>
                <StatNumber>{agentStatus?.total_agents || 0}</StatNumber>
                <StatHelpText>{agentStatus?.busy_agents || 0} busy • {agentStatus?.idle_agents || 0} idle</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Response Time</StatLabel>
                <StatNumber>{metrics.response_time_ms}ms</StatNumber>
                <StatHelpText>Average API response</StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </Grid>

        {/* Agent Collaboration Section */}
        {agentStatus && (
          <Card>
            <CardHeader>
              <Heading size="md">Agent Collaboration Network</Heading>
              <Text fontSize="sm" color="gray.600">Real-time agent assignments and collaboration patterns</Text>
            </CardHeader>
            <CardBody>
              <Grid templateColumns="repeat(auto-fit, minmax(300px, 1fr))" gap={6}>
                {/* Collaboration Stats */}
                <Box>
                  <Text fontSize="lg" fontWeight="bold" mb={4}>Collaboration Metrics</Text>
                  <VStack spacing={3} align="stretch">
                    <HStack justify="space-between">
                      <Text fontSize="sm">Active Collaborations</Text>
                      <Badge colorScheme="blue">{agentStatus.collaboration_stats?.active_collaborations || 0}</Badge>
                    </HStack>
                    <HStack justify="space-between">
                      <Text fontSize="sm">Total Assignments</Text>
                      <Badge colorScheme="green">{agentStatus.collaboration_stats?.total_project_assignments || 0}</Badge>
                    </HStack>
                    <HStack justify="space-between">
                      <Text fontSize="sm">Avg Team Size</Text>
                      <Badge colorScheme="purple">{(agentStatus.collaboration_stats?.avg_team_size || 0).toFixed(1)}</Badge>
                    </HStack>
                  </VStack>
                </Box>

                {/* Agent Details */}
                <Box>
                  <Text fontSize="lg" fontWeight="bold" mb={4}>Agent Status</Text>
                  <VStack spacing={3} align="stretch">
                    {agentStatus.agents_detail?.slice(0, 4).map((agent: any) => (
                      <Box key={agent.id} p={3} bg="gray.50" borderRadius="md">
                        <HStack justify="space-between">
                          <VStack align="start" spacing={1}>
                            <Text fontSize="sm" fontWeight="bold">{agent.name}</Text>
                            <Text fontSize="xs" color="gray.600">{agent.specialization}</Text>
                          </VStack>
                          <VStack align="end" spacing={1}>
                            <Badge 
                              colorScheme={agent.status === 'busy' ? 'red' : 'green'}
                              size="sm"
                            >
                              {agent.status.toUpperCase()}
                            </Badge>
                            <Text fontSize="xs" color="gray.500">
                              {agent.performance_score}% performance
                            </Text>
                          </VStack>
                        </HStack>
                        {agent.current_project && (
                          <Box mt={2} p={2} bg="blue.50" borderRadius="sm">
                            <Text fontSize="xs" color="blue.800">
                              Working on: {agent.current_project.title}
                            </Text>
                            <Progress 
                              value={agent.current_project.progress} 
                              size="xs" 
                              colorScheme="blue" 
                              mt={1}
                            />
                          </Box>
                        )}
                      </Box>
                    ))}
                  </VStack>
                </Box>
              </Grid>
            </CardBody>
          </Card>
        )}

        {/* Safety Monitoring */}
        {safetyStatus && (
          <Card>
            <CardHeader>
              <Heading size="md">Safety Monitoring</Heading>
              <Text fontSize="sm" color="gray.600">Continuous safety oversight and violation tracking</Text>
            </CardHeader>
            <CardBody>
              <Grid templateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={6}>
                <VStack spacing={3} align="stretch">
                  <HStack>
                    <Text fontSize="sm" fontWeight="bold">Overall Status:</Text>
                    <Badge 
                      colorScheme={safetyStatus.overall_status === 'safe' ? 'green' : 'red'}
                    >
                      {safetyStatus.overall_status?.toUpperCase()}
                    </Badge>
                  </HStack>
                  <HStack>
                    <Text fontSize="sm">Monitoring Active:</Text>
                    <Badge colorScheme={safetyStatus.monitoring_active ? 'green' : 'gray'}>
                      {safetyStatus.monitoring_active ? 'YES' : 'NO'}
                    </Badge>
                  </HStack>
                </VStack>

                <VStack spacing={3} align="stretch">
                  <HStack>
                    <Text fontSize="sm">Active Violations:</Text>
                    <Badge colorScheme="red">{safetyStatus.active_violations?.length || 0}</Badge>
                  </HStack>
                  <HStack>
                    <Text fontSize="sm">24h Violations:</Text>
                    <Badge colorScheme="yellow">{safetyStatus.violation_count_24h || 0}</Badge>
                  </HStack>
                </VStack>

                <VStack spacing={3} align="stretch">
                  <HStack>
                    <Text fontSize="sm">Emergency Stops:</Text>
                    <Badge colorScheme="red">{safetyStatus.emergency_stops_count || 0}</Badge>
                  </HStack>
                  <HStack>
                    <Text fontSize="sm">Last Check:</Text>
                    <Text fontSize="xs" color="gray.600">
                      {safetyStatus.last_check ? new Date(safetyStatus.last_check).toLocaleTimeString() : 'N/A'}
                    </Text>
                  </HStack>
                </VStack>
              </Grid>
            </CardBody>
          </Card>
        )}

        {/* Component Health Grid */}
        {overview?.components && (
          <Card>
            <CardHeader>
              <Heading size="md">System Components</Heading>
              <Text fontSize="sm" color="gray.600">Health status of all system components</Text>
            </CardHeader>
            <CardBody>
              <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={4}>
                {overview.components.map((component: any) => (
                  <Box key={component.name} p={3} bg="gray.50" borderRadius="md">
                    <HStack justify="space-between" mb={2}>
                      <Text fontSize="sm" fontWeight="bold">
                        {component.name.replace('_', ' ').toUpperCase()}
                      </Text>
                      <Badge 
                        colorScheme={
                          component.status === 'healthy' ? 'green' :
                          component.status === 'warning' ? 'yellow' : 'red'
                        }
                        size="sm"
                      >
                        {component.status.toUpperCase()}
                      </Badge>
                    </HStack>
                    <Progress 
                      value={component.performance} 
                      size="sm" 
                      colorScheme={
                        component.performance > 90 ? 'green' :
                        component.performance > 70 ? 'yellow' : 'red'
                      }
                    />
                    <Text fontSize="xs" color="gray.500" mt={1}>
                      {component.performance}% performance
                    </Text>
                    {component.details && (
                      <Text fontSize="xs" color="gray.600" mt={1}>
                        {component.details}
                      </Text>
                    )}
                  </Box>
                ))}
              </Grid>
            </CardBody>
          </Card>
        )}
      </VStack>
    </Box>
  )
}

export default Monitoring 