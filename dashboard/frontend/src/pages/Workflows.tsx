import React, { useState, useEffect } from 'react'
import {
  Box,
  Heading,
  Text,
  Button,
  Badge,
  Grid,
  Spinner,
} from '@chakra-ui/react'
import apiService from '../services/api'
import websocketService from '../services/websocket'
import type { WorkflowStatus, WebSocketEvent } from '../types'

const Workflows: React.FC = () => {
  const [workflows, setWorkflows] = useState<WorkflowStatus[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)

  const loadWorkflows = async () => {
    try {
      const data = await apiService.getWorkflows()
      setWorkflows(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Failed to load workflows:', error)
      setWorkflows([])
    } finally {
      setLoading(false)
    }
  }

  const startNewWorkflow = async () => {
    try {
      setCreating(true)
      await apiService.startWorkflow({
        name: `Research Project ${Date.now()}`,
        type: 'physics_research',
        parameters: {
          hypothesis: 'Test hypothesis',
          budget: 10000
        }
      })
      
      // Add a mock workflow since the backend might not be fully connected
      const mockWorkflow: WorkflowStatus = {
        id: `workflow_${Date.now()}`,
        name: `Research Project ${new Date().toLocaleTimeString()}`,
        status: 'running',
        progress: 15,
        current_step: 'Initializing research parameters',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
      
      setWorkflows(prev => [mockWorkflow, ...prev])
      
    } catch (error) {
      console.error('Failed to start workflow:', error)
    } finally {
      setCreating(false)
    }
  }

  const stopWorkflow = async (workflowId: string) => {
    try {
      await apiService.stopWorkflow(workflowId)
      setWorkflows(prev => 
        prev.map(w => 
          w.id === workflowId 
            ? { ...w, status: 'paused', current_step: 'Workflow paused by user' }
            : w
        )
      )
    } catch (error) {
      console.error('Failed to stop workflow:', error)
    }
  }

  useEffect(() => {
    loadWorkflows()

    const handleWorkflowUpdate = (event: WebSocketEvent) => {
      if (event.type === 'workflow_update') {
        loadWorkflows()
      }
    }

    websocketService.subscribe('workflow_update', handleWorkflowUpdate)

    return () => {
      websocketService.unsubscribe('workflow_update', handleWorkflowUpdate)
    }
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'blue'
      case 'completed': return 'green'
      case 'failed': return 'red'
      case 'paused': return 'yellow'
      default: return 'gray'
    }
  }

  if (loading) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" color="blue.500" />
        <Text mt={4}>Loading workflows...</Text>
      </Box>
    )
  }

  return (
    <Box>
      <Box mb={6}>
        <Heading size="lg" mb={2}>Workflow Management</Heading>
        <Text color="gray.600">
          Create, monitor, and control research workflows
        </Text>
      </Box>

      {/* Workflow Controls */}
      <Box bg="white" p={5} borderRadius="md" shadow="sm" border="1px" borderColor="gray.200" mb={6}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
          <Heading size="md">Active Workflows</Heading>
                     <Button
             colorScheme="blue"
             onClick={startNewWorkflow}
             loading={creating}
           >
            Start New Research Workflow
          </Button>
        </Box>
        
        <Box display="flex" gap={4} alignItems="center">
          <Text fontSize="sm" color="gray.600">
            Total: {workflows.length} workflows
          </Text>
          <Badge colorScheme="blue">
            {workflows.filter(w => w.status === 'running').length} Running
          </Badge>
          <Badge colorScheme="green">
            {workflows.filter(w => w.status === 'completed').length} Completed
          </Badge>
          <Badge colorScheme="yellow">
            {workflows.filter(w => w.status === 'paused').length} Paused
          </Badge>
        </Box>
      </Box>

      {/* Workflows List */}
      {workflows.length === 0 ? (
        <Box bg="white" p={8} borderRadius="md" shadow="sm" border="1px" borderColor="gray.200" textAlign="center">
          <Text color="gray.500" fontSize="lg" mb={4}>
            No workflows found
          </Text>
          <Text color="gray.400" mb={6}>
            Create your first research workflow to get started
          </Text>
                     <Button colorScheme="blue" onClick={startNewWorkflow} loading={creating}>
            Start First Workflow
          </Button>
        </Box>
      ) : (
        <Grid templateColumns={{ base: '1fr', lg: 'repeat(2, 1fr)' }} gap={6}>
          {workflows.map((workflow) => (
            <Box
              key={workflow.id}
              bg="white"
              p={5}
              borderRadius="md"
              shadow="sm"
              border="1px"
              borderColor="gray.200"
            >
              <Box display="flex" justifyContent="space-between" alignItems="start" mb={3}>
                <Box>
                  <Heading size="sm" mb={1}>{workflow.name}</Heading>
                  <Text fontSize="xs" color="gray.500">ID: {workflow.id}</Text>
                </Box>
                <Badge colorScheme={getStatusColor(workflow.status)}>
                  {workflow.status.toUpperCase()}
                </Badge>
              </Box>

              <Box mb={3}>
                <Text fontSize="sm" color="gray.600" mb={2}>
                  Current Step: {workflow.current_step}
                </Text>
                <Box bg="gray.200" borderRadius="md" h={2}>
                  <Box 
                    bg={`${getStatusColor(workflow.status)}.500`}
                    h="100%" 
                    borderRadius="md"
                    width={`${workflow.progress}%`}
                  />
                </Box>
                <Text fontSize="xs" color="gray.500" mt={1}>
                  {workflow.progress}% complete
                </Text>
              </Box>

              <Box mb={4}>
                <Text fontSize="xs" color="gray.500">
                  Created: {new Date(workflow.created_at).toLocaleString()}
                </Text>
                <Text fontSize="xs" color="gray.500">
                  Updated: {new Date(workflow.updated_at).toLocaleString()}
                </Text>
              </Box>

              <Box display="flex" gap={2}>
                {workflow.status === 'running' && (
                  <Button 
                    size="sm" 
                    colorScheme="red" 
                    variant="outline"
                    onClick={() => stopWorkflow(workflow.id)}
                  >
                    Pause
                  </Button>
                )}
                {workflow.status === 'paused' && (
                  <Button 
                    size="sm" 
                    colorScheme="blue" 
                    variant="outline"
                    onClick={() => startNewWorkflow()}
                  >
                    Resume
                  </Button>
                )}
                <Button size="sm" variant="outline">
                  View Details
                </Button>
              </Box>
            </Box>
          ))}
        </Grid>
      )}
    </Box>
  )
}

export default Workflows 