import React, { useState, useEffect } from 'react'
import {
  Box, Heading, Text, Button, VStack, HStack, Grid,
  Card, CardHeader, CardBody, Badge, Progress, Spinner,
  Modal, ModalOverlay, ModalContent, ModalHeader, ModalFooter, ModalBody, ModalCloseButton,
  FormControl, FormLabel, Input, Textarea, Select, NumberInput, NumberInputField,
  useDisclosure, useToast, Alert, AlertIcon, Stat, StatLabel, StatNumber, StatHelpText,
  Tabs, TabList, TabPanels, Tab, TabPanel
} from '@chakra-ui/react'
import { apiService } from '../services/api'

interface Workflow {
  id: string
  title: string
  status: string
  progress: number
  current_step: string
  created_at: string
  updated_at: string
  estimated_completion: string
  assigned_agents: string[]
  physics_domain: string
  research_question: string
  cost_used: number
  max_cost: number
}

interface WorkflowFormData {
  title: string
  research_question: string
  physics_domain: string
  priority: string
  max_cost: number
  duration_hours: number
}

const Workflows: React.FC = () => {
  const [workflows, setWorkflows] = useState<Workflow[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { isOpen, onOpen, onClose } = useDisclosure()
  const toast = useToast()

  const [formData, setFormData] = useState<WorkflowFormData>({
    title: '',
    research_question: '',
    physics_domain: 'general',
    priority: 'MEDIUM',
    max_cost: 1000,
    duration_hours: 24
  })

  const loadWorkflows = async () => {
    try {
      setLoading(true)
      const workflowData = await apiService.getWorkflows()
      // Ensure we handle the response properly - it's now an array directly
      setWorkflows(Array.isArray(workflowData) ? workflowData : [])
      setError(null)
    } catch (err) {
      setError('Failed to load workflows')
      console.error('Error loading workflows:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadWorkflows()
    const interval = setInterval(loadWorkflows, 10000) // Update every 10 seconds
    return () => clearInterval(interval)
  }, [])

  const handleCreateWorkflow = async () => {
    try {
      setCreating(true)
      
      const workflowRequest = {
        project_name: formData.title,
        research_topic: formData.research_question,
        workflow_template: 'research_cycle',
        parameters: {
          physics_domain: formData.physics_domain,
          priority: formData.priority,
          max_cost: formData.max_cost,
          duration_hours: formData.duration_hours
        }
      }

      await apiService.startWorkflow(workflowRequest)
      
      toast({
        title: 'Workflow Created',
        description: `Research project "${formData.title}" has been started successfully`,
        status: 'success',
        duration: 5000,
        isClosable: true
      })

      // Reset form
      setFormData({
        title: '',
        research_question: '',
        physics_domain: 'general',
        priority: 'MEDIUM',
        max_cost: 1000,
        duration_hours: 24
      })

      onClose()
      loadWorkflows() // Refresh the list
      
    } catch (err) {
      toast({
        title: 'Error',
        description: 'Failed to create workflow',
        status: 'error',
        duration: 5000,
        isClosable: true
      })
    } finally {
      setCreating(false)
    }
  }

  const handleStopWorkflow = async (workflowId: string, title: string) => {
    try {
      await apiService.stopWorkflow(workflowId)
      
      toast({
        title: 'Workflow Stopped',
        description: `Research project "${title}" has been stopped`,
        status: 'warning',
        duration: 5000,
        isClosable: true
      })

      loadWorkflows() // Refresh the list
      
    } catch (err) {
      toast({
        title: 'Error',
        description: 'Failed to stop workflow',
        status: 'error',
        duration: 5000,
        isClosable: true
      })
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'planning': return 'blue'
      case 'executing': return 'green'
      case 'analyzing': return 'purple'
      case 'completed': return 'gray'
      case 'failed': return 'red'
      case 'queued': return 'yellow'
      default: return 'gray'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'planning': return '📋'
      case 'executing': return '⚡'
      case 'analyzing': return '🔬'
      case 'completed': return '✅'
      case 'failed': return '❌'
      case 'queued': return '⏳'
      default: return '❓'
    }
  }

  const formatCurrency = (amount: number) => `$${amount.toFixed(2)}`
  const formatDate = (dateString: string) => new Date(dateString).toLocaleString()

  if (loading && workflows.length === 0) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" color="blue.500" />
        <Text mt={4}>Loading workflows...</Text>
      </Box>
    )
  }

  if (error) {
    return (
      <Alert status="error">
        <AlertIcon />
        {error}
      </Alert>
    )
  }

  const activeWorkflows = workflows.filter(w => !['completed', 'failed'].includes(w.status.toLowerCase()))
  const completedWorkflows = workflows.filter(w => ['completed', 'failed'].includes(w.status.toLowerCase()))

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <HStack justify="space-between">
          <Box>
            <Heading size="lg">Research Workflows</Heading>
            <Text color="gray.600">Manage autonomous research projects and track progress</Text>
          </Box>
          <Button 
            colorScheme="blue" 
            onClick={onOpen}
            size="lg"
          >
            Start New Research
          </Button>
        </HStack>

        {/* Summary Stats */}
        <Grid templateColumns="repeat(4, 1fr)" gap={6}>
          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Active Projects</StatLabel>
                <StatNumber>{activeWorkflows.length}</StatNumber>
                <StatHelpText>Currently running</StatHelpText>
              </Stat>
            </CardBody>
          </Card>
          
          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Total Projects</StatLabel>
                <StatNumber>{workflows.length}</StatNumber>
                <StatHelpText>All time</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Total Cost</StatLabel>
                <StatNumber>{formatCurrency(workflows.reduce((sum, w) => sum + w.cost_used, 0))}</StatNumber>
                <StatHelpText>Resources used</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Avg Progress</StatLabel>
                <StatNumber>
                  {activeWorkflows.length > 0 
                    ? Math.round(activeWorkflows.reduce((sum, w) => sum + w.progress, 0) / activeWorkflows.length)
                    : 0}%
                </StatNumber>
                <StatHelpText>Active projects</StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </Grid>

        {/* Workflow Tabs */}
        <Tabs>
          <TabList>
            <Tab>Active Projects ({activeWorkflows.length})</Tab>
            <Tab>Completed Projects ({completedWorkflows.length})</Tab>
          </TabList>

          <TabPanels>
            {/* Active Workflows */}
            <TabPanel>
              {activeWorkflows.length === 0 ? (
                <Card>
                  <CardBody textAlign="center" py={10}>
                    <Text fontSize="lg" color="gray.500">No active research projects</Text>
                    <Text color="gray.400">Start a new research project to begin autonomous investigation</Text>
                    <Button colorScheme="blue" mt={4} onClick={onOpen}>
                      Start Research Project
                    </Button>
                  </CardBody>
                </Card>
              ) : (
                <Grid templateColumns="repeat(auto-fit, minmax(400px, 1fr))" gap={6}>
                  {activeWorkflows.map((workflow) => (
                    <Card key={workflow.id} shadow="md">
                      <CardHeader>
                        <HStack justify="space-between">
                          <VStack align="start" spacing={1}>
                            <HStack>
                              <Text fontSize="lg" fontWeight="bold">{workflow.title}</Text>
                              <Text>{getStatusIcon(workflow.status)}</Text>
                            </HStack>
                            <Badge colorScheme={getStatusColor(workflow.status)} variant="subtle">
                              {workflow.status.toUpperCase()}
                            </Badge>
                          </VStack>
                          <Button 
                            size="sm" 
                            colorScheme="red" 
                            variant="outline"
                            onClick={() => handleStopWorkflow(workflow.id, workflow.title)}
                          >
                            Stop
                          </Button>
                        </HStack>
                      </CardHeader>
                      
                      <CardBody>
                        <VStack spacing={3} align="stretch">
                          <Box>
                            <Text fontSize="sm" color="gray.600" mb={1}>Research Question</Text>
                            <Text fontSize="sm">{workflow.research_question}</Text>
                          </Box>

                          <Box>
                            <Text fontSize="sm" color="gray.600" mb={1}>Progress</Text>
                            <Progress value={workflow.progress} colorScheme="blue" size="sm" />
                            <Text fontSize="xs" color="gray.500">{workflow.progress.toFixed(1)}% - {workflow.current_step}</Text>
                          </Box>

                          <HStack justify="space-between">
                            <Box>
                              <Text fontSize="xs" color="gray.600">Domain</Text>
                              <Badge size="sm" colorScheme="purple">{workflow.physics_domain}</Badge>
                            </Box>
                            <Box>
                              <Text fontSize="xs" color="gray.600">Agents</Text>
                              <Text fontSize="xs">{workflow.assigned_agents.length}</Text>
                            </Box>
                          </HStack>

                          <HStack justify="space-between">
                            <Box>
                              <Text fontSize="xs" color="gray.600">Cost</Text>
                              <Text fontSize="xs">{formatCurrency(workflow.cost_used)} / {formatCurrency(workflow.max_cost)}</Text>
                            </Box>
                            <Box>
                              <Text fontSize="xs" color="gray.600">Started</Text>
                              <Text fontSize="xs">{formatDate(workflow.created_at)}</Text>
                            </Box>
                          </HStack>
                        </VStack>
                      </CardBody>
                    </Card>
                  ))}
                </Grid>
              )}
            </TabPanel>

            {/* Completed Workflows */}
            <TabPanel>
              {completedWorkflows.length === 0 ? (
                <Card>
                  <CardBody textAlign="center" py={10}>
                    <Text fontSize="lg" color="gray.500">No completed projects yet</Text>
                    <Text color="gray.400">Completed and failed projects will appear here</Text>
                  </CardBody>
                </Card>
              ) : (
                <Grid templateColumns="repeat(auto-fit, minmax(400px, 1fr))" gap={6}>
                  {completedWorkflows.map((workflow) => (
                    <Card key={workflow.id} shadow="md" opacity={0.8}>
                      <CardHeader>
                        <HStack>
                          <VStack align="start" spacing={1}>
                            <HStack>
                              <Text fontSize="lg" fontWeight="bold">{workflow.title}</Text>
                              <Text>{getStatusIcon(workflow.status)}</Text>
                            </HStack>
                            <Badge colorScheme={getStatusColor(workflow.status)} variant="subtle">
                              {workflow.status.toUpperCase()}
                            </Badge>
                          </VStack>
                        </HStack>
                      </CardHeader>
                      
                      <CardBody>
                        <VStack spacing={3} align="stretch">
                          <Box>
                            <Text fontSize="sm" color="gray.600" mb={1}>Research Question</Text>
                            <Text fontSize="sm">{workflow.research_question}</Text>
                          </Box>

                          <HStack justify="space-between">
                            <Box>
                              <Text fontSize="xs" color="gray.600">Final Cost</Text>
                              <Text fontSize="xs">{formatCurrency(workflow.cost_used)}</Text>
                            </Box>
                            <Box>
                              <Text fontSize="xs" color="gray.600">Completed</Text>
                              <Text fontSize="xs">{formatDate(workflow.updated_at)}</Text>
                            </Box>
                          </HStack>
                        </VStack>
                      </CardBody>
                    </Card>
                  ))}
                </Grid>
              )}
            </TabPanel>
          </TabPanels>
        </Tabs>
      </VStack>

      {/* Create Workflow Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Start New Research Project</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4}>
              <FormControl isRequired>
                <FormLabel>Project Title</FormLabel>
                <Input
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  placeholder="e.g., Quantum Entanglement at Room Temperature"
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Research Question</FormLabel>
                <Textarea
                  value={formData.research_question}
                  onChange={(e) => setFormData({...formData, research_question: e.target.value})}
                  placeholder="What specific question should this research project investigate?"
                  rows={3}
                />
              </FormControl>

              <HStack spacing={4} width="100%">
                <FormControl>
                  <FormLabel>Physics Domain</FormLabel>
                  <Select
                    value={formData.physics_domain}
                    onChange={(e) => setFormData({...formData, physics_domain: e.target.value})}
                  >
                    <option value="general">General Physics</option>
                    <option value="quantum">Quantum Mechanics</option>
                    <option value="particle_physics">Particle Physics</option>
                    <option value="optics">Optics</option>
                    <option value="thermodynamics">Thermodynamics</option>
                    <option value="astrophysics">Astrophysics</option>
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel>Priority</FormLabel>
                  <Select
                    value={formData.priority}
                    onChange={(e) => setFormData({...formData, priority: e.target.value})}
                  >
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                    <option value="URGENT">Urgent</option>
                  </Select>
                </FormControl>
              </HStack>

              <HStack spacing={4} width="100%">
                <FormControl>
                  <FormLabel>Max Budget (USD)</FormLabel>
                  <NumberInput
                    value={formData.max_cost}
                    onChange={(_, value) => setFormData({...formData, max_cost: value || 1000})}
                    min={100}
                    max={10000}
                  >
                    <NumberInputField />
                  </NumberInput>
                </FormControl>

                <FormControl>
                  <FormLabel>Expected Duration (Hours)</FormLabel>
                  <NumberInput
                    value={formData.duration_hours}
                    onChange={(_, value) => setFormData({...formData, duration_hours: value || 24})}
                    min={1}
                    max={168}
                  >
                    <NumberInputField />
                  </NumberInput>
                </FormControl>
              </HStack>
            </VStack>
          </ModalBody>

          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button 
              colorScheme="blue" 
              onClick={handleCreateWorkflow}
              isLoading={creating}
              loadingText="Starting..."
              isDisabled={!formData.title || !formData.research_question}
            >
              Start Research Project
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  )
}

export default Workflows 